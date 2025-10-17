from sqlalchemy import Column, Integer , String , DateTime
from datetime import datetime
from ..database import Base

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    cpf = Column(String(14), unique=True, index=True, nullable=False)
    telefone = Column(String(15), nullable=False)
    email = Column(String(100), nullable=True)
    data_cadastro = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Cliente {self.nome} - {self.cpf}>"