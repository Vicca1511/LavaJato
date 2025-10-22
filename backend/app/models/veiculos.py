from sqlalchemy import Column , Integer , String , ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Veiculo(Base):
  
  __tablename__ = "veiculos"

  id = Column(Integer, primary_key=True, index=True)
  cliente_id = Column(Integer, ForeignKey("clientes.id"))
  placa = Column(String(8), unique=True, nullable=False)
  modelo = Column(String(50), nullable=False)
  cor = Column(String(20))
  
  cliente = relationship("Cliente", back_populates="veiculos")

