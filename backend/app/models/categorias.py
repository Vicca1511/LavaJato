from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy.orm import relationship
from ..database import Base

class Categoria(Base):
    __tablename__ = "categorias"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), nullable=False)
    descricao = Column(Text)
    ordem_exibicao = Column(Integer, default=0)
    ativo = Column(Boolean, default=True)
    
    # Relacionamento com Servicos (CORRIGIDO)
    servicos = relationship("Servico", back_populates="categoria")
    
    def __repr__(self):
        return f"<Categoria {self.nome}>"

