from sqlalchemy import Column, Integer, String, ForeignKey, Time, DateTime
from .base import Base

class Itinerario(Base):
    __tablename__ = 'itinerario'
    __table_args__ = {'schema': 'sptrans'}
    
    codigolinha = Column(Integer, ForeignKey('sptrans.linha.codigo'), primary_key=True)
    prefixoveiculo = Column(String, ForeignKey('sptrans.veiculo.prefixo'), primary_key=True)
    datareferencia = Column(DateTime, primary_key=True)
    codigoparada = Column(Integer, ForeignKey('sptrans.parada.codigo'))
    previsaochegada = Column(Time)