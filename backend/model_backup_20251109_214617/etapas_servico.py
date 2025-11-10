from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class EtapaServico(Base):
    __tablename__ = "etapas_servico"

    id = Column(Integer, primary_key=True)
    ordem_servico_id = Column(Integer, ForeignKey("ordens_servico.id"), nullable=False)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    status = Column(String(20), default="PENDENTE")
    ordem = Column(Integer, nullable=False)
    tempo_estimado = Column(Integer)
    data_inicio = Column(DateTime)
    data_conclusao = Column(DateTime)
    responsavel = Column(String(100))

   
    ordem_servico = relationship("OrdemServico", back_populates="etapas", lazy="select")