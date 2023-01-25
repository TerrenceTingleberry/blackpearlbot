from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from plugins.database import BASE


class Panel(BASE):
    __tablename__ = "panel"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    description = Column(String(500))
    guild_id = Column(String)
    forms = relationship("Form", back_populates="panel")


class Form(BASE):
    __tablename__ = "form"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    description = Column(String(500))
    panel_id = Column(Integer, ForeignKey("panel.id"))
    panel = relationship("Panel", back_populates="forms")
    fields = relationship("Field", back_populates="form")


class Field(BASE):
    __tablename__ = "field"
    id = Column(Integer, primary_key=True)
    name = Column(String(500))
    form_id = Column(Integer, ForeignKey("form.id"))
    form = relationship("Form", back_populates="fields")
    response = Column(String(500))
