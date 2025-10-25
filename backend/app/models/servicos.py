from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Servico(Base):
    __tablename__ = "servicos"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    valor_base = Column(Float, nullable=False)
    duracao_estimada = Column(Integer)
    categoria_id = Column(Integer, ForeignKey("categorias.id"))
    ativo = Column(Boolean, default=True)
    
    # Relacionamentos (CORRIGIDOS)
    categoria = relationship("Categoria", back_populates="servicos")
    portes_preco = relationship("PortePreco", back_populates="servico", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Servico {self.nome} - R$ {self.valor_base}>"
    
    @property
    def preco_medio(self):
        """Preço médio considerando todos os portes"""
        if self.portes_preco:
            multiplicadores = [pp.multiplicador for pp in self.portes_preco]
            return self.valor_base * (sum(multiplicadores) / len(multiplicadores))
        return self.valor_base
    

