from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
import random
import string
from sqlalchemy.sql import func

from ..database import get_db
from ..models.agendamentos import Agendamento, StatusServico
from ..models.veiculos import Veiculo
from ..models.servicos import Servico
from ..models.porte_preco import PortePreco
from ..schemas.agendamentos import AgendamentoCreate, AgendamentoResponse, FilaResponse

router = APIRouter()

def gerar_codigo_confirmacao():
    return ''.join(random.choices(string.digits, k=6))

def calcular_valor_servico(servico_id: int, porte_veiculo: str, db: Session) -> float:
    servico = db.query(Servico).filter(Servico.id == servico_id).first()
    porte_preco = db.query(PortePreco).filter(
        PortePreco.servico_id == servico_id,
        PortePreco.porte == porte_veiculo
    ).first()
    
    if servico and porte_preco:
        return servico.valor_base * porte_preco.multiplicador
    return 0.0

def calcular_tempo_espera(agendamento: Agendamento) -> float:
    if agendamento.data_entrada and agendamento.data_inicio_servico:
        return (agendamento.data_inicio_servico - agendamento.data_entrada).total_seconds() / 60
    return 0

def calcular_tempo_servico(agendamento: Agendamento) -> float:
    if agendamento.data_inicio_servico and agendamento.data_fim_servico:
        return (agendamento.data_fim_servico - agendamento.data_inicio_servico).total_seconds() / 60
    return 0

def agendamento_para_response(agendamento: Agendamento) -> dict:
    """Converte model Agendamento para schema de resposta"""
    response_data = {
        "id": agendamento.id,
        "veiculo_id": agendamento.veiculo_id,
        "servico_id": agendamento.servico_id,
        "status": agendamento.status,
        "valor_cobrado": agendamento.valor_cobrado,
        "posicao_fila": agendamento.posicao_fila,
        "data_entrada": agendamento.data_entrada,
        "data_inicio_servico": agendamento.data_inicio_servico,
        "data_fim_servico": agendamento.data_fim_servico,
        "data_entrega": agendamento.data_entrega,
        "observacoes": agendamento.observacoes,
        "codigo_pagamento": agendamento.codigo_pagamento,
        "codigo_confirmacao": agendamento.codigo_confirmacao,
        "pago": agendamento.pago,
        "notificado_whatsapp": agendamento.notificado_whatsapp,
        "tempo_espera": calcular_tempo_espera(agendamento),
        "tempo_servico": calcular_tempo_servico(agendamento)
    }
    
    # Adicionar veiculo se disponivel
    if hasattr(agendamento, 'veiculo') and agendamento.veiculo:
        response_data["veiculo"] = {
            "id": agendamento.veiculo.id,
            "placa": agendamento.veiculo.placa,
            "modelo": agendamento.veiculo.modelo,
            "cor": agendamento.veiculo.cor,
            "porte": agendamento.veiculo.porte,
            "cliente_id": agendamento.veiculo.cliente_id
        }
    
    # Adicionar servico se disponivel
    if hasattr(agendamento, 'servico') and agendamento.servico:
        response_data["servico"] = {
            "id": agendamento.servico.id,
            "nome": agendamento.servico.nome,
            "descricao": agendamento.servico.descricao,
            "valor_base": agendamento.servico.valor_base,
            "duracao_estimada": agendamento.servico.duracao_estimada
        }
    
    return response_data

@router.post("/", response_model=AgendamentoResponse)
def criar_agendamento(agendamento: AgendamentoCreate, db: Session = Depends(get_db)):
    # Verificar se veículo existe
    veiculo = db.query(Veiculo).filter(Veiculo.id == agendamento.veiculo_id).first()
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")

    # Verificar se serviço existe
    servico = db.query(Servico).filter(Servico.id == agendamento.servico_id).first()
    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")

    # Calcular valor baseado no porte do veículo
    valor_cobrado = calcular_valor_servico(agendamento.servico_id, veiculo.porte, db)
    if valor_cobrado == 0:
        raise HTTPException(status_code=400, detail="Preço não configurado para este porte de veículo")

    # Calcular posição na fila
    ultimo_agendamento = db.query(Agendamento).filter(
        Agendamento.status.in_([StatusServico.AGUARDANDO, StatusServico.EM_LAVAGEM])
    ).order_by(Agendamento.posicao_fila.desc()).first()
    
    nova_posicao = (ultimo_agendamento.posicao_fila + 1) if ultimo_agendamento else 1

    # Criar agendamento
    db_agendamento = Agendamento(
        veiculo_id=agendamento.veiculo_id,
        servico_id=agendamento.servico_id,
        valor_cobrado=valor_cobrado,
        posicao_fila=nova_posicao,
        observacoes=agendamento.observacoes,
        codigo_confirmacao=gerar_codigo_confirmacao()
    )

    db.add(db_agendamento)
    db.commit()
    db.refresh(db_agendamento)
    
    # Carregar relacionamentos para a resposta
    db_agendamento = db.query(Agendamento).options(
        joinedload(Agendamento.veiculo),
        joinedload(Agendamento.servico)
    ).filter(Agendamento.id == db_agendamento.id).first()
    
    return agendamento_para_response(db_agendamento)

@router.get("/fila", response_model=FilaResponse)
def ver_fila(db: Session = Depends(get_db)):
    # Carregar agendamentos com relacionamentos usando joinedload
    em_espera = db.query(Agendamento).options(
        joinedload(Agendamento.veiculo),
        joinedload(Agendamento.servico)
    ).filter(
        Agendamento.status == StatusServico.AGUARDANDO
    ).order_by(Agendamento.posicao_fila).all()
    
    em_lavagem = db.query(Agendamento).options(
        joinedload(Agendamento.veiculo),
        joinedload(Agendamento.servico)
    ).filter(
        Agendamento.status == StatusServico.EM_LAVAGEM
    ).all()
    
    finalizados = db.query(Agendamento).options(
        joinedload(Agendamento.veiculo),
        joinedload(Agendamento.servico)
    ).filter(
        Agendamento.status == StatusServico.FINALIZADO
    ).all()
    
    # Converter para response
    return FilaResponse(
        em_espera=[agendamento_para_response(ag) for ag in em_espera],
        em_lavagem=[agendamento_para_response(ag) for ag in em_lavagem],
        finalizados=[agendamento_para_response(ag) for ag in finalizados]
    )

@router.post("/{agendamento_id}/iniciar")
def iniciar_servico(agendamento_id: int, db: Session = Depends(get_db)):
    agendamento = db.query(Agendamento).filter(Agendamento.id == agendamento_id).first()
    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    
    agendamento.status = StatusServico.EM_LAVAGEM
    agendamento.data_inicio_servico = func.now()
    db.commit()
    
    return {"message": "Serviço iniciado"}

@router.post("/{agendamento_id}/finalizar")
def finalizar_servico(agendamento_id: int, db: Session = Depends(get_db)):
    agendamento = db.query(Agendamento).filter(Agendamento.id == agendamento_id).first()
    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    
    agendamento.status = StatusServico.FINALIZADO
    agendamento.data_fim_servico = func.now()
    db.commit()
    
    return {"message": "Serviço finalizado"}

@router.post("/{agendamento_id}/entregar")
def entregar_veiculo(agendamento_id: int, db: Session = Depends(get_db)):
    agendamento = db.query(Agendamento).filter(Agendamento.id == agendamento_id).first()
    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    
    agendamento.status = StatusServico.ENTREGUE
    agendamento.data_entrega = func.now()
    db.commit()
    
    return {"message": "Veículo entregue"}

@router.get("/{agendamento_id}/pix")
def gerar_qr_code_pix(agendamento_id: int, db: Session = Depends(get_db)):
    agendamento = db.query(Agendamento).options(
        joinedload(Agendamento.veiculo),
        joinedload(Agendamento.servico)
    ).filter(Agendamento.id == agendamento_id).first()
    
    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    
    # Simular geração de QR Code PIX
    codigo_pix = f"00020126580014BR.GOV.BCB.PIX0136{random.randint(100000000000000000, 999999999999999999)}5204000053039865406{agendamento.valor_cobrado:.2f}5802BR5900LAVAJATO6008SAO PAULO6304{random.randint(1000, 9999)}"
    
    agendamento.codigo_pagamento = codigo_pix
    db.commit()
    
    return {
        "qr_code": codigo_pix,
        "valor": agendamento.valor_cobrado,
        "descricao": f"Servico: {agendamento.servico.nome} - Veiculo: {agendamento.veiculo.placa}",
        "codigo_confirmacao": agendamento.codigo_confirmacao
    }

@router.post("/{agendamento_id}/confirmar-pagamento")
def confirmar_pagamento(agendamento_id: int, db: Session = Depends(get_db)):
    agendamento = db.query(Agendamento).filter(Agendamento.id == agendamento_id).first()
    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    
    agendamento.pago = True
    db.commit()
    
    return {"message": "Pagamento confirmado"}

@router.post("/{agendamento_id}/notificar-whatsapp")
def notificar_whatsapp(agendamento_id: int, db: Session = Depends(get_db)):
    agendamento = db.query(Agendamento).options(
        joinedload(Agendamento.veiculo),
        joinedload(Agendamento.servico)
    ).filter(Agendamento.id == agendamento_id).first()
    
    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    
    # Simular envio de WhatsApp
    mensagem = f"Lava Jato - Seu veiculo {agendamento.veiculo.placa} esta pronto para retirada! Servico: {agendamento.servico.nome} - Valor: R$ {agendamento.valor_cobrado:.2f} - Codigo: {agendamento.codigo_confirmacao}"
    
    agendamento.notificado_whatsapp = True
    db.commit()
    
    return {
        "message": "Notificacao enviada",
        "telefone": agendamento.veiculo.cliente.telefone if hasattr(agendamento.veiculo, 'cliente') else "N/A",
        "mensagem": mensagem
    }
