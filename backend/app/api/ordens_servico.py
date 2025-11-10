from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.ordens_servico import OrdemServico
from app.models.veiculos import Veiculo
from app.models.servicos import Servico
from app.schemas.ordens_servico import OrdemServicoCreate, OrdemServicoResponse, FilaResponse

router = APIRouter(tags=["Ordens de Servico"])

@router.get("/simple")
def get_ordens_simple(db: Session = Depends(get_db)):
    """Endpoint simples - sem relacionamentos complexos"""
    try:
        ordens = db.query(OrdemServico).all()
        return [
            {
                "id": o.id,
                "veiculo": o.veiculo,
                "placa": o.placa,
                "status": o.status.value,
                "valor_total": o.valor_total,
                "etapa_atual": o.etapa_atual,
                "progresso": o.progresso
            }
            for o in ordens
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=OrdemServicoResponse)
def criar_ordem_servico(ordem: OrdemServicoCreate, db: Session = Depends(get_db)):
    """Cria nova ordem de servico"""
    try:
        nova_ordem = OrdemServico(**ordem.dict())
        db.add(nova_ordem)
        db.commit()
        db.refresh(nova_ordem)
        return nova_ordem
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao criar ordem: {str(e)}")

@router.get("/", response_model=List[OrdemServicoResponse])
def listar_ordens_servico(db: Session = Depends(get_db)):
    """Lista todas as ordens de servico"""
    try:
        return db.query(OrdemServico).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar ordens: {str(e)}")

@router.get("/fila", response_model=List[FilaResponse])
def obter_fila_atendimento(db: Session = Depends(get_db)):
    """Retorna a fila de atendimento para display"""
    try:
        ordens = db.query(OrdemServico).filter(
            OrdemServico.status.in_(["SOLICITADO", "CONFIRMADO", "EM_ANDAMENTO"])
        ).order_by(OrdemServico.data_entrada).all()
        
        fila_response = []
        for ordem in ordens:
            fila_response.append(FilaResponse(
                id=ordem.id,
                cliente_nome=f"Cliente {ordem.cliente_id}",
                veiculo_placa=ordem.placa,
                servico_nome="Lavagem",
                valor_cobrado=float(ordem.valor_total),
                data_entrada=ordem.data_entrada
            ))

        return fila_response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar fila: {str(e)}")
