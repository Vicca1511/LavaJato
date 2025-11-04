from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import enum

class StatusServico(enum.Enum):
    AGUARDANDO = "aguardando"
    EM_LAVAGEM = "em_lavagem"
    FINALIZADO = "finalizado"
    ENTREGUE = "entregue"
    CANCELADO = "cancelado"

class Agendamento(Base):
    __tablename__ = "agendamentos"

    id = Column(Integer, primary_key=True, index=True)
    veiculo_id = Column(Integer, ForeignKey("veiculos.id"), nullable=False)
    servico_id = Column(Integer, ForeignKey("servicos.id"), nullable=False)
    status = Column(Enum(StatusServico), default=StatusServico.AGUARDANDO)
    valor_cobrado = Column(Float, nullable=False)
    posicao_fila = Column(Integer)
    data_entrada = Column(DateTime, default=func.now())
    data_inicio_servico = Column(DateTime)
    data_fim_servico = Column(DateTime)
    data_entrega = Column(DateTime)
    observacoes = Column(Text)
    codigo_pagamento = Column(String(50))  # QR Code PIX
    codigo_confirmacao = Column(String(20))  # Código de confirmação
    pago = Column(Boolean, default=False)
    notificado_whatsapp = Column(Boolean, default=False)

    # Relacionamentos
    veiculo = relationship("Veiculo", back_populates="agendamentos")
    servico = relationship("Servico")

    def __repr__(self):
        return f"<Agendamento {self.id} - {self.veiculo.placa} - {self.status.value}>"

    @property
    def tempo_espera(self):
        if self.data_entrada and self.data_inicio_servico:
            return (self.data_inicio_servico - self.data_entrada).total_seconds() / 60
        return 0

    @property
    def tempo_servico(self):
        if self.data_inicio_servico and self.data_fim_servico:
            return (self.data_fim_servico - self.data_inicio_servico).total_seconds() / 60
        return 0
