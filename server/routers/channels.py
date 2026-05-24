from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.channel import Channel
from models.employee import Employee
from schemas.channel import ChannelCreate, ChannelUpdate, ChannelOut
from schemas.common import ResponseModel, PaginatedResponse
from deps import get_current_user


router = APIRouter(prefix="/api/channels", tags=["渠道管理"])


@router.get("", response_model=PaginatedResponse)
def list_channels(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None),
    status: int = Query(None),
    user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    q = db.query(Channel)
    if keyword:
        q = q.filter(Channel.name.contains(keyword) | Channel.code.contains(keyword))
    if status is not None:
        q = q.filter(Channel.status == status)
    total = q.count()
    items = q.order_by(Channel.sort_order, Channel.id).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(data=[ChannelOut.model_validate(i) for i in items], total=total, page=page, page_size=page_size)


@router.post("", response_model=ResponseModel)
def create_channel(req: ChannelCreate, user: Employee = Depends(get_current_user), db: Session = Depends(get_db)):
    channel = Channel(**req.model_dump())
    db.add(channel)
    db.commit()
    db.refresh(channel)
    return ResponseModel(data=ChannelOut.model_validate(channel))


@router.get("/{channel_id}", response_model=ResponseModel)
def get_channel(channel_id: int, user: Employee = Depends(get_current_user), db: Session = Depends(get_db)):
    channel = db.query(Channel).get(channel_id)
    if not channel:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="渠道不存在")
    return ResponseModel(data=ChannelOut.model_validate(channel))


@router.put("/{channel_id}", response_model=ResponseModel)
def update_channel(channel_id: int, req: ChannelUpdate, user: Employee = Depends(get_current_user), db: Session = Depends(get_db)):
    channel = db.query(Channel).get(channel_id)
    if not channel:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="渠道不存在")
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(channel, k, v)
    db.commit()
    db.refresh(channel)
    return ResponseModel(data=ChannelOut.model_validate(channel))


@router.delete("/{channel_id}", response_model=ResponseModel)
def delete_channel(channel_id: int, user: Employee = Depends(get_current_user), db: Session = Depends(get_db)):
    channel = db.query(Channel).get(channel_id)
    if not channel:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="渠道不存在")
    db.delete(channel)
    db.commit()
    return ResponseModel(message="删除成功")