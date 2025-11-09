from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class StatusOrdemServico(str, Enum):
    SOLICITADO = "SOLICITADO"
    CONFIRMADO = "CONFIRMADO"
    EM_ANDAMENTO = "EM_ANDAMENTO"
    AGUARDANDO_PAGAMENTO = "AGUARDANDO_PAGAMENTO"
    FINALIZADO = "FINALIZADO"
    CANCELADO = "CANCELADO"

class OrdemServicoBase(BaseModel):
    veiculo_id: int
    servico_id: int
    observacoes: Optional[str] = None

class OrdemServicoCreate(OrdemServicoBase):
    pass

# SCHEMA CORRIGIDO - que combina com o modelo REAL
class OrdemServicoResponse(BaseModel):
    id: int
    cliente_id: int
    veiculo: str
    placa: str
    status: str
    valor_total: float
    observacoes: Optional[str] = None
    data_entrada: datetime
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    notificado_whatsapp: bool = False
    etapa_atual: Optional[str] = None
    progresso: int = 0

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

    class Config:
        from_attributes = True

class WhatsAppMessage(BaseModel):
    telefone: str
    mensagem: str

class PagamentoPix(BaseModel):
    valor: float
    descricao: str
