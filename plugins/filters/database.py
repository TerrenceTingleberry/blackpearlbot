from sqlalchemy import Column, Integer, String

from plugins.database import BASE

'''
Args:
- id -> int
- guild_id -> str
- filter -> str, max characters: 50
- response -> str, maxcharacters: 500
'''
class Filter(BASE):
    __tablename__ = "filters"
    id = Column(Integer, primary_key=True)
    guild_id = Column(String)
    filter = Column(String(50))
    response = Column(String(500))
