from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from ..services.whatsapp_service import whatsapp_service
from ..services.mensagem_templates import MensagemTemplates
from ..services.agendamento_service import agendamento_service

router = APIRouter()

class WhatsAppTestRequest(BaseModel):
    telefone: str
    mensagem: Optional[str] = None

class AgendamentoTestRequest(BaseModel):
    telefone: str
    cliente_nome: str
    veiculo_placa: str
    data_hora: str
    servico: str

@router.get("/status")
def get_whatsapp_status():
    return whatsapp_service.get_status()

@router.post("/test")
def testar_whatsapp(request: WhatsAppTestRequest):
    mensagem = request.mensagem or MensagemTemplates.teste_conexao()
    resultado = whatsapp_service.enviar_mensagem(request.telefone, mensagem)
    
    return {
        "telefone_testado": request.telefone,
        "resultado": resultado
    }

@router.post("/test-agendamento")
def testar_agendamento(request: AgendamentoTestRequest):
    resultado = agendamento_service.enviar_confirmacao_agendamento(
        telefone=request.telefone,
        cliente_nome=request.cliente_nome,
        veiculo_placa=request.veiculo_placa,
        data_hora=request.data_hora,
        servico=request.servico
    )
    
    return {
        "tipo": "confirmacao_agendamento",
        "resultado": resultado
    }

@router.get("/modos")
def get_modos():
    return {
        "modo_atual": "SIMULATION",
        "custo": "GRATUITO"
    }
