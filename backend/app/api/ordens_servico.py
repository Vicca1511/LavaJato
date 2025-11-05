from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
import random
import string
from sqlalchemy.sql import func
from datetime import datetime

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

@router.post("/", response_model=OrdemServicoResponse)
def criar_ordem_servico(ordem: OrdemServicoCreate, db: Session = Depends(get_db)):
    """Cria nova ordem de serviço - REGISTRO HISTÓRICO (sem update/delete)"""
    try:
        # Verificar se veículo existe
        veiculo = db.query(Veiculo).filter(Veiculo.id == ordem.veiculo_id).first()
        if not veiculo:
            raise HTTPException(status_code=404, detail="Veículo não encontrado")
        
        # Verificar se serviço existe
        servico = db.query(Servico).filter(Servico.id == ordem.servico_id).first()
        if not servico:
            raise HTTPException(status_code=404, detail="Serviço não encontrado")
        
        # Calcular valor baseado no porte do veículo e serviço
        valor_cobrado = calcular_valor_servico(ordem.servico_id, veiculo.porte, db)
        
        # Determinar posição na fila
        ultima_posicao = db.query(func.max(OrdemServico.posicao_fila)).scalar() or 0
        
        db_ordem = OrdemServico(
            veiculo_id=ordem.veiculo_id,
            servico_id=ordem.servico_id,
            status=StatusOrdemServico.AGUARDANDO,
            valor_cobrado=valor_cobrado,
            posicao_fila=ultima_posicao + 1,
            data_entrada=datetime.utcnow(),
            codigo_confirmacao=gerar_codigo_confirmacao(),
            observacoes=ordem.observacoes
        )
        
        db.add(db_ordem)
        db.commit()
        db.refresh(db_ordem)
        
        return preparar_resposta_ordem(db_ordem, db)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar ordem: {str(e)}")

@router.get("/fila", response_model=List[FilaResponse])
def obter_fila(db: Session = Depends(get_db)):
    """Obtem todas as ordens aguardando e em lavagem (FILA)"""
    try:
        ordens = db.query(OrdemServico).filter(
            OrdemServico.status.in_([StatusOrdemServico.AGUARDANDO, StatusOrdemServico.EM_LAVAGEM])
        ).order_by(OrdemServico.posicao_fila).all()
        
        return [preparar_resposta_fila(ordem, db) for ordem in ordens]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar fila: {str(e)}")

@router.get("/", response_model=List[OrdemServicoResponse])
def listar_ordens_servico(db: Session = Depends(get_db)):
    """Lista TODAS as ordens de serviço (histórico completo)"""
    try:
        ordens = db.query(OrdemServico).order_by(OrdemServico.data_entrada.desc()).all()
        return [preparar_resposta_ordem(ordem, db) for ordem in ordens]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar ordens: {str(e)}")

@router.get("/{ordem_servico_id}", response_model=OrdemServicoResponse)
def obter_ordem_servico(ordem_servico_id: int, db: Session = Depends(get_db)):
    """Obtem uma ordem específica por ID"""
    try:
        ordem = db.query(OrdemServico).filter(OrdemServico.id == ordem_servico_id).first()
        if not ordem:
            raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada")
        return preparar_resposta_ordem(ordem, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar ordem: {str(e)}")

# FUNÇÕES AUXILIARES
def preparar_resposta_ordem(ordem_servico: OrdemServico, db: Session) -> OrdemServicoResponse:
    """Prepara resposta completa da ordem"""
    veiculo = db.query(Veiculo).filter(Veiculo.id == ordem_servico.veiculo_id).first()
    servico = db.query(Servico).filter(Servico.id == ordem_servico.servico_id).first()
    
    # Converter para dict e garantir que o status seja string
    response_data = {
        "id": ordem_servico.id,
        "veiculo_id": ordem_servico.veiculo_id,
        "servico_id": ordem_servico.servico_id,
        "status": ordem_servico.status.value,  # Usar .value para string
        "valor_cobrado": float(ordem_servico.valor_cobrado),
        "posicao_fila": ordem_servico.posicao_fila,
        "data_entrada": ordem_servico.data_entrada,
        "data_inicio_servico": ordem_servico.data_inicio_servico,
        "data_fim_servico": ordem_servico.data_fim_servico,
        "data_entrega": ordem_servico.data_entrega,
        "codigo_confirmacao": ordem_servico.codigo_confirmacao,
        "observacoes": ordem_servico.observacoes,
        "pago": bool(ordem_servico.pago),
        "notificado_whatsapp": bool(ordem_servico.notificado_whatsapp),
        "tempo_espera": float(ordem_servico.tempo_espera),
        "tempo_servico": float(ordem_servico.tempo_servico)
    }
    
    return OrdemServicoResponse(**response_data)

def preparar_resposta_fila(ordem_servico: OrdemServico, db: Session) -> FilaResponse:
    """Prepara resposta para fila (dados simplificados)"""
    veiculo = db.query(Veiculo).filter(Veiculo.id == ordem_servico.veiculo_id).first()
    servico = db.query(Servico).filter(Servico.id == ordem_servico.servico_id).first()
    
    response_data = {
        "id": ordem_servico.id,
        "posicao_fila": ordem_servico.posicao_fila,
        "status": ordem_servico.status.value,  # Usar .value para string
        "veiculo_placa": veiculo.placa if veiculo else "N/A",
        "servico_nome": servico.nome if servico else "N/A",
        "valor_cobrado": float(ordem_servico.valor_cobrado),
        "data_entrada": ordem_servico.data_entrada
    }
    
    return FilaResponse(**response_data)
