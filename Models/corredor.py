from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base

class Corredor(Base):
    __tablename__ = 'corredor'
    __table_args__ = {'schema': 'sptrans'}
    
    codigo = Column(Integer, primary_key=True)
    nome = Column(String)