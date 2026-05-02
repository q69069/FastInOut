"""
消息中心路由
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from database import get_db
from models.message import AppMessage as Message
from routers.auth import get_current_user

router = APIRouter(prefix="/messages", tags=["消息中心"])


class MessageResponse(BaseModel):
    id: int
    type: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    recipient_id: Optional[int] = None
    sender_id: Optional[int] = None
    status: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    created_at: Optional[datetime] = None
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    type: str
    title: str
    content: str
    recipient_id: int
    sender_id: Optional[int] = None
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None


@router.get("/", response_model=list[MessageResponse])
def list_messages(
    status: str = None,
    recipient_id: int = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    query = db.query(Message)
    if status:
        query = query.filter(Message.status == status)
    if recipient_id:
        query = query.filter(Message.recipient_id == recipient_id)
    else:
        query = query.filter(Message.recipient_id == current_user.id)
    return query.order_by(Message.created_at.desc()).all()


@router.post("/", response_model=MessageResponse)
def create_message(
    data: MessageCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    msg = Message(**data.model_dump(), sender_id=current_user.id)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


@router.put("/{message_id}/read")
def mark_as_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    msg = db.query(Message).filter(Message.id == message_id).first()
    if msg:
        msg.status = "read"
        msg.read_at = datetime.now()
        db.commit()
    return {"success": True}


@router.get("/unread-count")
def unread_count(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    count = db.query(Message).filter(
        Message.recipient_id == current_user.id,
        Message.status == "unread"
    ).count()
    return {"count": count}