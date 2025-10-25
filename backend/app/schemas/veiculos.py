from pydantic import BaseModel, field_validator
from typing import Optional
import re

class VeiculoBase(BaseModel):
    placa: str
    modelo: str
    cor: str
    porte: str  # P, M, G
    observacoes: Optional[str] = None

    @field_validator('placa')
    @classmethod
    def validate_placa(cls, v: str) -> str:
        placa_clean = re.sub(r'[^A-Za-z0-9]', '', v.upper())
        if len(placa_clean) not in [7, 8]:  # Mercosul ou antiga
            raise ValueError('Placa deve ter 7 ou 8 caracteres')
        return placa_clean

    @field_validator('porte')
    @classmethod
    def validate_porte(cls, v: str) -> str:
        if v.upper() not in ['P', 'M', 'G']:
            raise ValueError('Porte deve ser P (Pequeno), M (Médio) ou G (Grande)')
        return v.upper()

    @field_validator('modelo')
    @classmethod
    def validate_modelo(cls, v: str) -> str:
        if len(v.strip()) < 2:
            raise ValueError('Modelo deve ter pelo menos 2 caracteres')
        return v.strip()

class VeiculoCreate(VeiculoBase):
    cliente_id: int

class VeiculoUpdate(VeiculoBase):
    cliente_id: Optional[int] = None

class Veiculo(VeiculoBase):
    id: int
    cliente_id: int

    class Config:
        from_attributes = True

class VeiculoResponse(VeiculoBase):
    id: int
    cliente_id: int

    class Config:
        from_attributes = True

class VeiculoComCliente(VeiculoResponse):
    cliente: 'ClienteResponse'