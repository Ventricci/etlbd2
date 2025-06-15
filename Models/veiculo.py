from sqlalchemy import Column, String, Boolean
from .base import Base

class Veiculo(Base):
    __tablename__ = 'veiculo'
    __table_args__ = {'schema': 'sptrans'}
    
    prefixo = Column(String, primary_key=True)
    acessopcd = Column(Boolean)