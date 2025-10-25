from pydantic import BaseModel, field_validator, computed_field
from typing import Optional, List
from datetime import datetime

class PortePrecoBase(BaseModel):
    porte: str  # P, M, G
    multiplicador: float

    @field_validator('porte')
    @classmethod
    def validate_porte(cls, v: str) -> str:
        if v.upper() not in ['P', 'M', 'G']:
            raise ValueError('Porte deve ser P, M ou G')
        return v.upper()

    @field_validator('multiplicador')
    @classmethod
    def validate_multiplicador(cls, v: float) -> float:
        if v <= 0:
            raise ValueError('Multiplicador deve ser maior que 0')
        return round(v, 2)

class PortePrecoCreate(PortePrecoBase):
    pass

class PortePreco(PortePrecoBase):
    id: int
    servico_id: int

    class Config:
        from_attributes = True

class PortePrecoResponse(PortePrecoBase):
    id: int
    servico_id: int
    valor_base: float  # Adicionar valor_base para cálculo
    
    @computed_field
    @property
    def valor_final(self) -> float:
        return round(self.valor_base * self.multiplicador, 2)

    class Config:
        from_attributes = True

class ServicoBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    valor_base: float
    duracao_estimada: Optional[int] = None
    categoria_id: int

    @field_validator('nome')
    @classmethod
    def validate_nome(cls, v: str) -> str:
        if len(v.strip()) < 2:
            raise ValueError('Nome deve ter pelo menos 2 caracteres')
        return v.strip()

    @field_validator('valor_base')
    @classmethod
    def validate_valor_base(cls, v: float) -> float:
        if v <= 0:
            raise ValueError('Valor base deve ser maior que 0')
        return round(v, 2)

    @field_validator('duracao_estimada')
    @classmethod
    def validate_duracao(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError('Duração deve ser maior que 0')
        return v

class ServicoCreate(ServicoBase):
    portes_preco: List[PortePrecoCreate]

class Servico(ServicoBase):
    id: int
    ativo: bool

    class Config:
        from_attributes = True

class ServicoResponse(ServicoBase):
    id: int
    ativo: bool
    portes_preco: List[PortePrecoResponse]
    
    @computed_field
    @property
    def preco_medio(self) -> float:
        if self.portes_preco:
            multiplicadores = [pp.multiplicador for pp in self.portes_preco]
            return round(self.valor_base * (sum(multiplicadores) / len(multiplicadores)), 2)
        return self.valor_base

    class Config:
        from_attributes = True

class ServicoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    valor_base: Optional[float] = None
    duracao_estimada: Optional[int] = None
    categoria_id: Optional[int] = None
    ativo: Optional[bool] = None

class ServicoComPrecoFinal(ServicoResponse):
    valor_final: float
    porte_selecionado: str