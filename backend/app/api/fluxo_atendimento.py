from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.fluxo_atendimento import FluxoAtendimentoService
from ..models.ordens_servico import OrdemServico, StatusOrdemServico

router = APIRouter(tags=["Fluxo Atendimento"])

@router.post("/ordens/{ordem_id}/iniciar")
def iniciar_ordem_servico(ordem_id: int, responsavel: str = "Sistema", db: Session = Depends(get_db)):
    """Inicia uma ordem de serviço"""
    try:
        fluxo_service = FluxoAtendimentoService(db)
        ordem = fluxo_service.iniciar_ordem(ordem_id, responsavel)
        return {"message": "Ordem iniciada com sucesso", "ordem": ordem}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao iniciar ordem: {str(e)}")

@router.post("/ordens/{ordem_id}/avancar-etapa")
def avancar_etapa_servico(ordem_id: int, responsavel: str = "Sistema", db: Session = Depends(get_db)):
    """Avança para a próxima etapa do serviço"""
    try:
        fluxo_service = FluxoAtendimentoService(db)
        ordem, proxima_etapa = fluxo_service.avancar_etapa(ordem_id, responsavel)
        
        if proxima_etapa:
            return {
                "message": "Etapa avançada com sucesso", 
                "ordem": ordem,
                "proxima_etapa": proxima_etapa.nome
            }
        else:
            return {
                "message": "Todas as etapas concluídas", 
                "ordem": ordem
            }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao avançar etapa: {str(e)}")

@router.post("/ordens/{ordem_id}/finalizar")
def finalizar_ordem_servico(ordem_id: int, db: Session = Depends(get_db)):
    """Finaliza uma ordem de serviço"""
    try:
        fluxo_service = FluxoAtendimentoService(db)
        ordem = fluxo_service.finalizar_ordem(ordem_id)
        return {"message": "Ordem finalizada com sucesso", "ordem": ordem}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao finalizar ordem: {str(e)}")

@router.get("/ordens/{ordem_id}/etapas")
def listar_etapas_ordem(ordem_id: int, db: Session = Depends(get_db)):
    """Lista todas as etapas de uma ordem"""
    ordem = db.query(OrdemServico).filter(OrdemServico.id == ordem_id).first()
    if not ordem:
        raise HTTPException(status_code=404, detail="Ordem não encontrada")
    
    return {
        "ordem_id": ordem.id,
        "etapa_atual": ordem.etapa_atual,
        "progresso": ordem.progresso,
        "etapas": [
            {
                "id": etapa.id,
                "nome": etapa.nome,
                "descricao": etapa.descricao,
                "status": etapa.status,
                "ordem": etapa.ordem,
                "responsavel": etapa.responsavel,
                "data_inicio": etapa.data_inicio,
                "data_conclusao": etapa.data_conclusao
            }
            for etapa in ordem.etapas
        ] if ordem.etapas else []
    }

@router.get("/ordens/em-andamento")
def listar_ordens_em_andamento(db: Session = Depends(get_db)):
    """Lista todas as ordens em andamento com suas etapas"""
    ordens = db.query(OrdemServico).filter(
        OrdemServico.status == StatusOrdemServico.EM_ANDAMENTO
    ).all()
    
    return {
        "total": len(ordens),
        "ordens": [
            {
                "id": ordem.id,
                "cliente": ordem.cliente.nome,
                "telefone": ordem.cliente.telefone,
                "veiculo": ordem.veiculo,
                "placa": ordem.placa,
                "etapa_atual": ordem.etapa_atual,
                "progresso": ordem.progresso,
                "data_inicio": ordem.data_inicio,
                "etapas": [
                    {
                        "nome": etapa.nome,
                        "status": etapa.status,
                        "ordem": etapa.ordem,
                        "responsavel": etapa.responsavel
                    }
                    for etapa in ordem.etapas
                ] if ordem.etapas else []
            }
            for ordem in ordens
        ]
    }
