from pydantic import BaseModel, field_validator
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

# Evita import circular
if TYPE_CHECKING:
    from backend.app.schemas.servicos import ServicoResponse

class CategoriaBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    ordem_exibicao: int = 0

    @field_validator('nome')
    @classmethod
    def validate_nome(cls, v: str) -> str:
        if len(v.strip()) < 2:
            raise ValueError('Nome deve ter pelo menos 2 caracteres')
        return v.strip()

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaUpdate(CategoriaBase):
    pass

class Categoria(CategoriaBase):
    id: int
    ativo: bool

    class Config:
        from_attributes = True

class CategoriaResponse(CategoriaBase):
    id: int
    ativo: bool

    class Config:
        from_attributes = True

class CategoriaComServicos(CategoriaResponse):
    servicos: List['ServicoResponse'] = []