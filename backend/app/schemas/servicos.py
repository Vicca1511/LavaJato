from pydantic import BaseModel, field_validator
from typing import Optional , List
from datetime import datetime

class PortePrecoBase(BaseModel):
    porte: str # P , M , G 
    multiplicador: float

    @field_validator('porte')
    @classmethod
    def validate_porte(cls, v: str) -> str:
        if v.upper() not in ['P', 'M', 'G']:
            raise ValueError('Porte deve ser definido por apenas uma letra =  P, M ou G')
        return v.upper() 
    
    @field_validator('multiplicador')
    @classmethod
    def validate_multipolicador(cls, v: float) -> float:
        if v <= 0:
            raise ValueError('Multiplicador deve ser maior que 0')
        return round(v, 2)
    
class PortePrecoCreate(PortePrecoBase):
    pass    

class PortePrecoResponse(PortePrecoBase):
    id:int
    servico_id:int
    valor_final:float # Calculado dinamicamente

    class Config:
        from_attributes = True

class ServicoBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    valor_base: float
    duracao_estimada: Optional[int] = None
    categoria:Optional[str] = None

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
    portes_preco: List[PortePrecoCreate]  # Lista de preços por porte


class ServicoResponse(ServicoBase):
    id: int
    ativo: bool
    portes_preco: List[PortePrecoResponse]
    
    class Config:
        from_attributes = True

class ServicoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    valor_base: Optional[float] = None
    duracao_estimada: Optional[int] = None
    categoria: Optional[str] = None
    ativo: Optional[bool] = None            