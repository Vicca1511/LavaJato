from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
from app.models.ordens_servico import StatusOrdemServico  # Importar do model

class OrdemServicoBase(BaseModel):
    veiculo_id: int
    servico_id: int
    observacoes: Optional[str] = None

class OrdemServicoCreate(OrdemServicoBase):
    pass

class OrdemServicoResponse(OrdemServicoBase):
    id: int
    status: StatusOrdemServico
    valor_cobrado: float
    posicao_fila: Optional[int] = None
    data_entrada: datetime
    data_inicio_servico: Optional[datetime] = None
    data_fim_servico: Optional[datetime] = None
    data_entrega: Optional[datetime] = None
    codigo_pagamento: Optional[str] = None  # Tornar opcional
    codigo_confirmacao: Optional[str] = None
    pago: bool = False
    notificado_whatsapp: bool = False
    tempo_espera: float = 0.0
    tempo_servico: float = 0.0

    class Config:
        from_attributes = True

class FilaResponse(BaseModel):
    id: int
    posicao_fila: int
    status: str
    veiculo_placa: str
    servico_nome: str
    valor_cobrado: float
    data_entrada: datetime

class WhatsAppMessage(BaseModel):
    telefone: str
    mensagem: str

class PagamentoPix(BaseModel):
    valor: float
    descricao: str
