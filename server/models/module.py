from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Module(Base):
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    module_key = Column(String(30), unique=True, nullable=False, comment="模块标识")
    name = Column(String(30), nullable=False, comment="模块名称")
    parent_id = Column(Integer, ForeignKey("modules.id"), comment="上级模块ID")
    module_type = Column(String(10), default="page", comment="page/action/api")
    pc_view = Column(Boolean, default=True, comment="PC端是否显示")
    h5_tab = Column(String(20), comment="H5对应Tab")
    sort_order = Column(Integer, default=0, comment="排序")
    icon = Column(String(30), comment="图标")
    path = Column(String(100), comment="前端路由路径")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    parent = relationship("Module", remote_side=[id])
