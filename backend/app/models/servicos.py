from sqlalchemy import Column , Integer , String , Float , Boolean , Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Servico(Base):
    __tablename__ = "servicos"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    valor_base = Column(Float, nullable=False)  # Valor para porte P
    duracao_estimada = Column(Integer)  # Minutos
    categoria = Column(String(50))  # lavagem, polimento, interior, etc.
    ativo = Column(Boolean, default=True)
    
    # Relacionamento com PortePreco
    portes_preco = relationship("PortePreco", back_populates="servico", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Servico {self.nome} - R$ {self.valor_base}>"

