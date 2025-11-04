from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class StatusOrdemServico(str, Enum):
    AGUARDANDO = "aguardando"
    EM_LAVAGEM = "em_lavagem"
    FINALIZADO = "finalizado"
    ENTREGUE = "entregue"
    CANCELADO = "cancelado"

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
    posicao_fila: Optional[int]
    data_entrada: datetime
    data_inicio_servico: Optional[datetime]
    data_fim_servico: Optional[datetime]
    data_entrega: Optional[datetime]
    codigo_pagamento: Optional[str]
    codigo_confirmacao: Optional[str]
    pago: bool
    notificado_whatsapp: bool
    tempo_espera: float
    tempo_servico: float

    class Config:
        from_attributes = True

class FilaResponse(BaseModel):
    em_espera: List[OrdemServicoResponse]
    em_lavagem: List[OrdemServicoResponse]
    finalizados: List[OrdemServicoResponse]

class WhatsAppMessage(BaseModel):
    telefone: str
    mensagem: str

class PagamentoPix(BaseModel):
    valor: float
    descricao: str
