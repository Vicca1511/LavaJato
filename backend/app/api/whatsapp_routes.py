# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from app.services.whatsapp_manager import whatsapp_manager

router = APIRouter()

class ServicoItem(BaseModel):
    nome: str
    valor: float

class EnvioResumoSchema(BaseModel):
    numero_cliente: str
    nome_cliente: str
    servicos: List[ServicoItem]

@router.post("/enviar-resumo")
async def enviar_resumo_servicos(data: EnvioResumoSchema):
    """Envia resumo de servicos para cliente via WhatsApp"""
    try:
        # Converte para lista de dicionarios
        servicos_list = [{"nome": s.nome, "valor": s.valor} for s in data.servicos]
        total = sum(s.valor for s in data.servicos)
        
        resultado = await whatsapp_manager.enviar_resumo_servico(
            data.numero_cliente,
            data.nome_cliente,
            servicos_list,
            total
        )
        
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def status_whatsapp():
    """Retorna status do servico WhatsApp"""
    return {
        "inicializado": whatsapp_manager.is_initialized,
        "conectado": whatsapp_manager.whatsapp.is_connected if whatsapp_manager.whatsapp else False
    }

@router.post("/inicializar")
async def inicializar_whatsapp():
    """Inicializa o servico WhatsApp manualmente"""
    try:
        success = await whatsapp_manager.initialize()
        return {"success": success, "inicializado": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
