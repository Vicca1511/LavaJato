from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional
import re

class ClienteBase(BaseModel):
    nome: str
    cpf: str
    telefone: str
    email: Optional[EmailStr] = None

    @field_validator('nome')
    @classmethod
    def validate_nome(cls, v: str) -> str:
        if len(v.strip()) < 2:
            raise ValueError('Nome deve ter pelo menos 2 caracteres')
        return v.strip()

    @field_validator('cpf')
    @classmethod
    def validate_cpf(cls, v: str) -> str:
        cpf_clean = re.sub(r'\D', '', v)
        if len(cpf_clean) != 11:
            raise ValueError('CPF deve ter 11 dígitos')
        return cpf_clean

    @field_validator('telefone')
    @classmethod
    def validate_telefone(cls, v: str) -> str:
        telefone_clean = re.sub(r'\D', '', v)
        if len(telefone_clean) not in [10, 11]:
            raise ValueError('Telefone deve ter 10 ou 11 dígitos')
        return v

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(ClienteBase):
    pass

class Cliente(ClienteBase):
    id: int
    data_cadastro: datetime

    class Config:
        from_attributes = True

class ClienteResponse(ClienteBase):
    id: int
    data_cadastro: datetime

    class Config:
        from_attributes = True