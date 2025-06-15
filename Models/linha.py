from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from .base import Base

class Linha(Base):
    __tablename__ = 'linha'
    __table_args__ = {'schema': 'sptrans'}
    
    codigo = Column(Integer, primary_key=True)
    letreironumerico = Column(String)
    modooperacao = Column(Integer)
    modocircular = Column(Boolean)
    sentido = Column(Integer)
    descritivoprincipal = Column(String)
    descritivosecundario = Column(String)
    
    paradas = relationship("LinhaParada", back_populates="linha")