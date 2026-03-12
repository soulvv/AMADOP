from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
import httpx
import logging

from database import get_db
from models import Post
from schemas import PostCreate, PostResponse
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


@router.post("/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Create a new blog post"""
    new_post = Post(
        title=post.title,
        content=post.content,
        author_id=current_user["id"]
    )
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    logger.info(f"Post created: {new_post.id} by user {current_user['id']}")
    
    # Add author username to response
    response = PostResponse.from_orm(new_post)
    response.author_username = current_user["username"]
    
    return response


@router.get("/posts", response_model=List[PostResponse])
async def get_all_posts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Retrieve all blog posts with pagination"""
    if limit > 100:
        limit = 100
    
    posts = db.query(Post).order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
    return posts


@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific blog post by ID"""
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    return post


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    """Delete a blog post (author only)"""
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    if post.author_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post"
        )
    
    db.delete(post)
    db.commit()
    
    logger.info(f"Post deleted: {post_id} by user {current_user['id']}")
    return None
