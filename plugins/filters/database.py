from sqlalchemy import Column, Integer, String

from plugins.database import BASE


class Filter(BASE):
    __tablename__ = "filters"
    id = Column(Integer, primary_key=True)
    guild_id = Column(String)
    filter = Column(String(50))
    response = Column(String(500))
