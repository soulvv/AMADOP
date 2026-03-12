from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from database import get_db
from models import Notification
from schemas import NotificationCreate, NotificationResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/notifications", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db)
):
    """Create a new notification (internal service call)"""
    new_notification = Notification(
        user_id=notification.user_id,
        message=notification.message
    )
    
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)
    
    logger.info(f"Notification created: {new_notification.id} for user {notification.user_id}")
    return new_notification


@router.get("/notifications/{user_id}", response_model=List[NotificationResponse])
async def get_user_notifications(
    user_id: int,
    unread_only: bool = False,
    db: Session = Depends(get_db)
):
    """Retrieve notifications for a specific user"""
    query = db.query(Notification).filter(Notification.user_id == user_id)
    
    if unread_only:
        query = query.filter(Notification.read == False)
    
    notifications = query.order_by(Notification.created_at.desc()).all()
    return notifications


@router.patch("/notifications/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db)
):
    """Mark a notification as read"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    notification.read = True
    db.commit()
    
    logger.info(f"Notification marked as read: {notification_id}")
    return None
