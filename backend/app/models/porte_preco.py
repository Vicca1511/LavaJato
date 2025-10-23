from sqlalchemy import Column , Integer , String , Float , ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class PortePreco(Base):
    __tablename__ = "porte_preco"

    id = Column(Integer , primary_key=True , index=True)
    servico_id = Column(Integer, ForeignKey("servicos.id"), nullable=False)
    porte = Column(String(1), nullable=False)
    multiplicador = Column(Float , nullable = False)

    # Relacionamento com Servico
    servico = relationship("Servico",back_populates="portes_precos")

    def __repr__(self):
        return f"<PortePreco {self.porte} - x{self.multiplicador}>"
    
    @property
    def valor_final(self):
        # Esta propriedade será calculada dinamicamente
        if hasattr(self, '_servico'):
            return self._servico.valor_base * self.multiplicador
        return 0.0


