from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class ShortURL(Base):
    """Docstring model for storing shortened urls"""
    __tablename__ = "short_urls"

    id = Column(Integer, primary_key=True)
    short_id = Column(String)
    original_url = Column(String)
