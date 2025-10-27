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

class StatusPagamento(enum.Enum):
    PENDENTE = "pendente"
    PROCESSANDO = "processando"
    CONFIRMADO = "confirmado"
    ESTORNADO = "estornado"
    CANCELADO = "cancelado"

class Agendamento(Base):
    __tablename__ = "agendamentos"

    id = Column(Integer, primary_key=True, index=True)
    veiculo_id = Column(Integer, ForeignKey("veiculos.id"), nullable=False)
    servico_id = Column(Integer, ForeignKey("servicos.id"), nullable=False)
    
    # Status do serviço
    status = Column(Enum(StatusServico), default=StatusServico.AGUARDANDO)
    
    # Controle de pagamento
    status_pagamento = Column(Enum(StatusPagamento), default=StatusPagamento.PENDENTE)
    valor_cobrado = Column(Float, nullable=False)
    pago = Column(Boolean, default=False)
    
    # Controle de tempo
    posicao_fila = Column(Integer)
    data_entrada = Column(DateTime, default=func.now())
    data_inicio_servico = Column(DateTime)
    data_fim_servico = Column(DateTime)
    data_entrega = Column(DateTime)
    
    # Identificação e controle
    codigo_confirmacao = Column(String(20))
    codigo_pagamento = Column(String(50))
    observacoes = Column(Text)
    
    # Notificações
    notificado_entrada = Column(Boolean, default=False)
    notificado_inicio = Column(Boolean, default=False) 
    notificado_finalizado = Column(Boolean, default=False)
    notificado_pagamento = Column(Boolean, default=False)
    
    # Auditoria
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

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

    def pode_ser_entregue(self):
        """Verifica se o veículo pode ser entregue"""
        return (self.status == StatusServico.FINALIZADO and 
                self.pago and 
                self.status_pagamento == StatusPagamento.CONFIRMADO)

    def precisa_notificar_finalizado(self):
        """Verifica se precisa enviar notificação de finalizado"""
        return (self.status == StatusServico.FINALIZADO and 
                not self.notificado_finalizado)
