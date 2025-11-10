
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey, DateTime, Enum
from sqlalchemy.sql import func
from ..database import Base
import enum

class StatusOrdemServico(enum.Enum):
    SOLICITADO = "SOLICITADO"
    CONFIRMADO = "CONFIRMADO" 
    EM_ANDAMENTO = "EM_ANDAMENTO"
    AGUARDANDO_PAGAMENTO = "AGUARDANDO_PAGAMENTO"
    FINALIZADO = "FINALIZADO"
    CANCELADO = "CANCELADO"

class OrdemServico(Base):
    __tablename__ = "ordens_servico"

    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    veiculo = Column(String(100), nullable=False)
    placa = Column(String(10), nullable=False)
    status = Column(Enum(StatusOrdemServico), default=StatusOrdemServico.SOLICITADO)
    data_entrada = Column(DateTime, default=func.now())
    data_inicio = Column(DateTime)
    data_fim = Column(DateTime)
    valor_total = Column(Float, default=0.0)
    observacoes = Column(Text)
    notificado_whatsapp = Column(Boolean, default=False)
    etapa_atual = Column(String(100), default="RECEPCAO")
    progresso = Column(Integer, default=0)
    
    # ZERO RELACIONAMENTOS - vamos fazer joins manualmente se necessário
