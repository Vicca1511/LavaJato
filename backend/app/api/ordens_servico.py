from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
import random
import string
from sqlalchemy.sql import func

from ..database import get_db
from ..models.ordens_servico import OrdemServico, StatusOrdemServico
from ..models.veiculos import Veiculo
from ..models.servicos import Servico
from ..models.porte_preco import PortePreco
from ..schemas.ordens_servico import OrdemServicoCreate, OrdemServicoResponse, FilaResponse

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

def calcular_tempo_espera(ordem_servico: OrdemServico) -> float:
    if ordem_servico.data_entrada and ordem_servico.data_inicio_servico:
        return (ordem_servico.data_inicio_servico - ordem_servico.data_entrada).total_seconds() / 60
    return 0

def calcular_tempo_servico(ordem_servico: OrdemServico) -> float:
    if ordem_servico.data_inicio_servico and ordem_servico.data_fim_servico:
        return (ordem_servico.data_fim_servico - ordem_servico.data_inicio_servico).total_seconds() / 60
    return 0

def ordem_servico_para_response(ordem_servico: OrdemServico) -> dict:
    """Converte model OrdemServico para schema de resposta"""
    response_data = {
        "id": ordem_servico.id,
        "veiculo_id": ordem_servico.veiculo_id,
        "servico_id": ordem_servico.servico_id,
        "status": ordem_servico.status,
        "valor_cobrado": ordem_servico.valor_cobrado,
        "posicao_fila": ordem_servico.posicao_fila,
        "data_entrada": ordem_servico.data_entrada,
        "data_inicio_servico": ordem_servico.data_inicio_servico,
        "data_fim_servico": ordem_servico.data_fim_servico,
        "data_entrega": ordem_servico.data_entrega,
        "observacoes": ordem_servico.observacoes,
        "codigo_pagamento": ordem_servico.codigo_pagamento,
        "codigo_confirmacao": ordem_servico.codigo_confirmacao,
        "pago": ordem_servico.pago,
        "notificado_whatsapp": ordem_servico.notificado_whatsapp,
        "tempo_espera": calcular_tempo_espera(ordem_servico),
        "tempo_servico": calcular_tempo_servico(ordem_servico)
    }
    
    # Adicionar veiculo se disponivel
    if hasattr(ordem_servico, 'veiculo') and ordem_servico.veiculo:
        response_data["veiculo"] = {
            "id": ordem_servico.veiculo.id,
            "placa": ordem_servico.veiculo.placa,
            "modelo": ordem_servico.veiculo.modelo,
            "cor": ordem_servico.veiculo.cor,
            "porte": ordem_servico.veiculo.porte,
            "cliente_id": ordem_servico.veiculo.cliente_id
        }
    
    # Adicionar servico se disponivel
    if hasattr(ordem_servico, 'servico') and ordem_servico.servico:
        response_data["servico"] = {
            "id": ordem_servico.servico.id,
            "nome": ordem_servico.servico.nome,
            "descricao": ordem_servico.servico.descricao,
            "valor_base": ordem_servico.servico.valor_base,
            "duracao_estimada": ordem_servico.servico.duracao_estimada
        }
    
    return response_data

@router.post("/", response_model=OrdemServicoResponse)
def criar_ordem_servico(ordem_servico: OrdemServicoCreate, db: Session = Depends(get_db)):
    # Verificar se veículo existe
    veiculo = db.query(Veiculo).filter(Veiculo.id == ordem_servico.veiculo_id).first()
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")

    # Verificar se serviço existe
    servico = db.query(Servico).filter(Servico.id == ordem_servico.servico_id).first()
    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")

    # Calcular valor baseado no porte do veículo
    valor_cobrado = calcular_valor_servico(ordem_servico.servico_id, veiculo.porte, db)
    if valor_cobrado == 0:
        raise HTTPException(status_code=400, detail="Preço não configurado para este porte de veículo")

    # Calcular posição na fila
    ultimo_ordem_servico = db.query(OrdemServico).filter(
        OrdemServico.status.in_([StatusOrdemServico.AGUARDANDO, StatusOrdemServico.EM_LAVAGEM])
    ).order_by(OrdemServico.posicao_fila.desc()).first()
    
    nova_posicao = (ultimo_ordem_servico.posicao_fila + 1) if ultimo_ordem_servico else 1

    # Criar ordem_servico
    db_ordem_servico = OrdemServico(
        veiculo_id=ordem_servico.veiculo_id,
        servico_id=ordem_servico.servico_id,
        valor_cobrado=valor_cobrado,
        posicao_fila=nova_posicao,
        observacoes=ordem_servico.observacoes,
        codigo_confirmacao=gerar_codigo_confirmacao()
    )

    db.add(db_ordem_servico)
    db.commit()
    db.refresh(db_ordem_servico)
    
    # Carregar relacionamentos para a resposta
    db_ordem_servico = db.query(OrdemServico).options(
        joinedload(OrdemServico.veiculo),
        joinedload(OrdemServico.servico)
    ).filter(OrdemServico.id == db_ordem_servico.id).first()
    
    return ordem_servico_para_response(db_ordem_servico)

@router.get("/fila", response_model=FilaResponse)
def ver_fila(db: Session = Depends(get_db)):
    # Carregar ordem_servicos com relacionamentos usando joinedload
    em_espera = db.query(OrdemServico).options(
        joinedload(OrdemServico.veiculo),
        joinedload(OrdemServico.servico)
    ).filter(
        OrdemServico.status == StatusOrdemServico.AGUARDANDO
    ).order_by(OrdemServico.posicao_fila).all()
    
    em_lavagem = db.query(OrdemServico).options(
        joinedload(OrdemServico.veiculo),
        joinedload(OrdemServico.servico)
    ).filter(
        OrdemServico.status == StatusOrdemServico.EM_LAVAGEM
    ).all()
    
    finalizados = db.query(OrdemServico).options(
        joinedload(OrdemServico.veiculo),
        joinedload(OrdemServico.servico)
    ).filter(
        OrdemServico.status == StatusOrdemServico.FINALIZADO
    ).all()
    
    # Converter para response
    return FilaResponse(
        em_espera=[ordem_servico_para_response(ag) for ag in em_espera],
        em_lavagem=[ordem_servico_para_response(ag) for ag in em_lavagem],
        finalizados=[ordem_servico_para_response(ag) for ag in finalizados]
    )

@router.post("/{ordem_servico_id}/iniciar")
def iniciar_servico(ordem_servico_id: int, db: Session = Depends(get_db)):
    ordem_servico = db.query(OrdemServico).filter(OrdemServico.id == ordem_servico_id).first()
    if not ordem_servico:
        raise HTTPException(status_code=404, detail="OrdemServico não encontrado")
    
    ordem_servico.status = StatusOrdemServico.EM_LAVAGEM
    ordem_servico.data_inicio_servico = func.now()
    db.commit()
    
    return {"message": "Serviço iniciado"}

@router.post("/{ordem_servico_id}/finalizar")
def finalizar_servico(ordem_servico_id: int, db: Session = Depends(get_db)):
    ordem_servico = db.query(OrdemServico).filter(OrdemServico.id == ordem_servico_id).first()
    if not ordem_servico:
        raise HTTPException(status_code=404, detail="OrdemServico não encontrado")
    
    ordem_servico.status = StatusOrdemServico.FINALIZADO
    ordem_servico.data_fim_servico = func.now()
    db.commit()
    
    return {"message": "Serviço finalizado"}

@router.post("/{ordem_servico_id}/entregar")
def entregar_veiculo(ordem_servico_id: int, db: Session = Depends(get_db)):
    ordem_servico = db.query(OrdemServico).filter(OrdemServico.id == ordem_servico_id).first()
    if not ordem_servico:
        raise HTTPException(status_code=404, detail="OrdemServico não encontrado")
    
    ordem_servico.status = StatusOrdemServico.ENTREGUE
    ordem_servico.data_entrega = func.now()
    db.commit()
    
    return {"message": "Veículo entregue"}

@router.get("/{ordem_servico_id}/pix")
def gerar_qr_code_pix(ordem_servico_id: int, db: Session = Depends(get_db)):
    ordem_servico = db.query(OrdemServico).options(
        joinedload(OrdemServico.veiculo),
        joinedload(OrdemServico.servico)
    ).filter(OrdemServico.id == ordem_servico_id).first()
    
    if not ordem_servico:
        raise HTTPException(status_code=404, detail="OrdemServico não encontrado")
    
    # Simular geração de QR Code PIX
    codigo_pix = f"00020126580014BR.GOV.BCB.PIX0136{random.randint(100000000000000000, 999999999999999999)}5204000053039865406{ordem_servico.valor_cobrado:.2f}5802BR5900LAVAJATO6008SAO PAULO6304{random.randint(1000, 9999)}"
    
    ordem_servico.codigo_pagamento = codigo_pix
    db.commit()
    
    return {
        "qr_code": codigo_pix,
        "valor": ordem_servico.valor_cobrado,
        "descricao": f"Servico: {ordem_servico.servico.nome} - Veiculo: {ordem_servico.veiculo.placa}",
        "codigo_confirmacao": ordem_servico.codigo_confirmacao
    }

@router.post("/{ordem_servico_id}/confirmar-pagamento")
def confirmar_pagamento(ordem_servico_id: int, db: Session = Depends(get_db)):
    ordem_servico = db.query(OrdemServico).filter(OrdemServico.id == ordem_servico_id).first()
    if not ordem_servico:
        raise HTTPException(status_code=404, detail="OrdemServico não encontrado")
    
    ordem_servico.pago = True
    db.commit()
    
    return {"message": "Pagamento confirmado"}

@router.post("/{ordem_servico_id}/notificar-whatsapp")
def notificar_whatsapp(ordem_servico_id: int, db: Session = Depends(get_db)):
    ordem_servico = db.query(OrdemServico).options(
        joinedload(OrdemServico.veiculo),
        joinedload(OrdemServico.servico)
    ).filter(OrdemServico.id == ordem_servico_id).first()
    
    if not ordem_servico:
        raise HTTPException(status_code=404, detail="OrdemServico não encontrado")
    
    # Simular envio de WhatsApp
    mensagem = f"Lava Jato - Seu veiculo {ordem_servico.veiculo.placa} esta pronto para retirada! Servico: {ordem_servico.servico.nome} - Valor: R$ {ordem_servico.valor_cobrado:.2f} - Codigo: {ordem_servico.codigo_confirmacao}"
    
    ordem_servico.notificado_whatsapp = True
    db.commit()
    
    return {
        "message": "Notificacao enviada",
        "telefone": ordem_servico.veiculo.cliente.telefone if hasattr(ordem_servico.veiculo, 'cliente') else "N/A",
        "mensagem": mensagem
    }
