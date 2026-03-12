from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
import httpx
import logging

from database import get_db
from models import Comment
from schemas import CommentCreate, CommentResponse
from config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


async def verify_token(authorization: Optional[str] = Header(None)) -> dict:
    """Verify JWT token with auth service"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = authorization.split(" ")[1]
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.AUTH_SERVICE_URL}/me",
                params={"token": token},
                timeout=5.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth service unavailable"
        )


async def trigger_notification(user_id: int, message: str):
    """Send notification to notification service (non-blocking)"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.NOTIFICATION_SERVICE_URL}/notifications",
                json={"user_id": user_id, "message": message},
                timeout=2.0
            )
            
            if response.status_code >= 200 and response.status_code < 300:
                logger.info(f"Notification sent to user {user_id}")
            else:
                logger.warning(f"Notification failed with status {response.status_code}")
    except httpx.RequestError as e:
        logger.error(f"Failed to send notification: {str(e)}")


@router.post("/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Create a new comment on a post"""
    # Verify post exists and get author
    try:
        async with httpx.AsyncClient() as client:
            post_response = await client.get(
                f"{settings.POST_SERVICE_URL}/posts/{comment.post_id}",
                timeout=5.0
            )
            
            if post_response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Post not found"
                )
            elif post_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Post service unavailable"
                )
            
            post_data = post_response.json()
            post_author_id = post_data["author_id"]
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Post service unavailable"
        )
    
    # Create comment
    new_comment = Comment(
        post_id=comment.post_id,
        user_id=current_user["id"],
        content=comment.content
    )
    
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    logger.info(f"Comment created: {new_comment.id} by user {current_user['id']}")
    
    # Trigger notification if commenter is not the post author
    if current_user["id"] != post_author_id:
        notification_message = f"New comment on your post from {current_user['username']}"
        await trigger_notification(post_author_id, notification_message)
    
    # Add username to response
    response = CommentResponse.from_orm(new_comment)
    response.username = current_user["username"]
    
    return response


@router.get("/comments/{post_id}", response_model=List[CommentResponse])
async def get_comments_for_post(post_id: int, db: Session = Depends(get_db)):
    """Retrieve all comments for a specific post"""
    comments = db.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.created_at).all()
    return comments
