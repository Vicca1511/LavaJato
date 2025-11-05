from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Veiculo(Base):
    __tablename__ = "veiculos"

    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String(10), nullable=False)
    modelo = Column(String(50), nullable=False)
    cor = Column(String(20), nullable=False)
    porte = Column(String(1), nullable=False)  # P, M, G
    observacoes = Column(Text)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)

    # Relacionamentos
    cliente = relationship("Cliente", back_populates="veiculos")
    # ordem_servico = relationship("OrdemServico")  # Temporariamente comentada

    def __repr__(self):
        return f"<Veiculo {self.placa} - {self.modelo}>"

    @property
    def servico_em_andamento(self):
        if self.agendamentos:
            for agendamento in self.agendamentos:
                if agendamento.status.value in ['aguardando', 'em_lavagem']:
                    return agendamento
        return None
