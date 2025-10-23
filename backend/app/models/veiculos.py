from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from ..database import Base

class Veiculo(Base):
    __tablename__ = "veiculos"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    placa = Column(String(8), unique=True, nullable=False)
    modelo = Column(String(50), nullable=False)
    cor = Column(String(20))
    porte = Column(String(1), nullable=False)  # P, M, G
    observacoes = Column(Text, nullable=True)
    
    # Relacionamento com Cliente
    cliente = relationship("Cliente", back_populates="veiculos")
    
    def __repr__(self):
        return f"<Veiculo {self.placa} - {self.modelo}>"