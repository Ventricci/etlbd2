from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Parada(Base):
    __tablename__ = 'parada'
    __table_args__ = {'schema': 'sptrans'}
    
    codigo = Column(Integer, primary_key=True)
    nome = Column(String)
    endereco = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    codigocorredor = Column(Integer)
    
    linhas = relationship("LinhaParada", back_populates="parada")

class LinhaParada(Base):
    __tablename__ = 'linhaparada'
    __table_args__ = {'schema': 'sptrans'}
    
    codigolinha = Column(Integer, ForeignKey('sptrans.linha.codigo'), primary_key=True)
    codigoparada = Column(Integer, ForeignKey('sptrans.parada.codigo'), primary_key=True)
    
    linha = relationship("Linha", back_populates="paradas")
    parada = relationship("Parada", back_populates="linhas")