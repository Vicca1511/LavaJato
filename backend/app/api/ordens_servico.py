from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.ordens_servico import OrdemServico
from app.models.veiculos import Veiculo
from app.models.servicos import Servico
from app.schemas.ordens_servico import OrdemServicoCreate, OrdemServicoResponse, FilaResponse

router = APIRouter(tags=["Ordens de Servico"])

@router.post("/", response_model=OrdemServicoResponse)
def criar_ordem_servico(ordem: OrdemServicoCreate, db: Session = Depends(get_db)):
    """Cria nova ordem de serviço"""
    try:
        print(f"DEBUG FRONTEND: Dados recebidos - {ordem.dict()}")
        
        # Verificar se veículo existe
        veiculo = db.query(Veiculo).filter(Veiculo.id == ordem.veiculo_id).first()
        if not veiculo:
            raise HTTPException(status_code=404, detail="Veículo não encontrado")

        # Verificar se serviço existe
        servico = db.query(Servico).filter(Servico.id == ordem.servico_id).first()
        if not servico:
            raise HTTPException(status_code=404, detail="Serviço não encontrado")

        # Criar ordem com campos que EXISTEM no modelo
        db_ordem = OrdemServico(
            cliente_id=1,  # Cliente padrão
            veiculo=veiculo.modelo,
            placa=veiculo.placa,
            valor_total=servico.valor_base,
            observacoes=f"Serviço: {servico.nome}. {ordem.observacoes or ''}",
            status="SOLICITADO"
        )
        
        db.add(db_ordem)
        db.commit()
        db.refresh(db_ordem)
        
        print(f"DEBUG: Ordem criada com sucesso! ID: {db_ordem.id}")
        return db_ordem

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"DEBUG: ERRO: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar ordem: {str(e)}")

@router.get("/", response_model=List[OrdemServicoResponse])
def listar_ordens_servico(db: Session = Depends(get_db)):
    """Lista TODAS as ordens de serviço"""
    try:
        ordens = db.query(OrdemServico).order_by(OrdemServico.data_entrada.desc()).all()
        return ordens
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar ordens: {str(e)}")

@router.get("/fila", response_model=List[FilaResponse])
def obter_fila(db: Session = Depends(get_db)):
    """Obtem fila de ordens (SOLICITADO e EM_ANDAMENTO)"""
    try:
        ordens = db.query(OrdemServico).filter(
            OrdemServico.status.in_(['SOLICITADO', 'EM_ANDAMENTO'])
        ).order_by(OrdemServico.data_entrada).all()
        
        fila_response = []
        for i, ordem in enumerate(ordens, 1):
            fila_response.append(FilaResponse(
                id=ordem.id,
                posicao_fila=i,
                status=ordem.status.value,
                veiculo_placa=ordem.placa,
                servico_nome="Lavagem",
                valor_cobrado=float(ordem.valor_total),
                data_entrada=ordem.data_entrada
            ))
        
        return fila_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar fila: {str(e)}")
