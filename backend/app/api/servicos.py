from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.servicos import Servico
from app.models.porte_preco import PortePreco
from app.schemas.servicos import ServicoCreate, ServicoResponse, PortePrecoResponse, ServicoUpdate

router = APIRouter(tags=["Servicos"])

@router.post("/", response_model=ServicoResponse, status_code=status.HTTP_201_CREATED)
def criar_servico(servico: ServicoCreate, db: Session = Depends(get_db)):
    db_servico = Servico(
        nome=servico.nome,
        descricao=servico.descricao,
        valor_base=servico.valor_base,
        duracao_estimada=servico.duracao_estimada,
        categoria_id=servico.categoria_id
    )
    db.add(db_servico)
    db.flush()

    for porte_preco in servico.portes_preco:
        db_porte_preco = PortePreco(
            servico_id=db_servico.id,
            porte=porte_preco.porte,
            multiplicador=porte_preco.multiplicador
        )
        db.add(db_porte_preco)

    db.commit()
    db.refresh(db_servico)
    return preparar_resposta_servico(db_servico, db)

@router.get("/", response_model=List[ServicoResponse])
def listar_servicos(db: Session = Depends(get_db)):
    servicos = db.query(Servico).all()
    return [preparar_resposta_servico(servico, db) for servico in servicos]

@router.get("/{servico_id}", response_model=ServicoResponse)
def obter_servico(servico_id: int, db: Session = Depends(get_db)):
    servico = db.query(Servico).filter(Servico.id == servico_id).first()
    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    return preparar_resposta_servico(servico, db)

@router.put("/{servico_id}", response_model=ServicoResponse)
def atualizar_servico(servico_id: int, servico_data: ServicoUpdate, db: Session = Depends(get_db)):
    servico = db.query(Servico).filter(Servico.id == servico_id).first()
    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    
    # Atualizar campos do serviço
    update_data = servico_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(servico, field, value)
    
    db.commit()
    db.refresh(servico)
    return preparar_resposta_servico(servico, db)

@router.delete("/{servico_id}")
def excluir_servico(servico_id: int, db: Session = Depends(get_db)):
    servico = db.query(Servico).filter(Servico.id == servico_id).first()
    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    
    # Excluir portes_preco primeiro (cascade)
    db.query(PortePreco).filter(PortePreco.servico_id == servico_id).delete()
    
    # Excluir serviço
    db.delete(servico)
    db.commit()
    return {"message": "Serviço excluído com sucesso"}

def preparar_resposta_servico(servico: Servico, db: Session) -> ServicoResponse:
    """Prepara a resposta do serviço com cálculos dinâmicos"""
    portes_preco = db.query(PortePreco).filter(PortePreco.servico_id == servico.id).all()

    # Criar lista de PortePrecoResponse com valor_base para cálculo
    portes_response = []
    for porte in portes_preco:
        porte_dict = {
            "id": porte.id,
            "servico_id": porte.servico_id,
            "porte": porte.porte,
            "multiplicador": porte.multiplicador,
            "valor_base": servico.valor_base  # Passar valor_base para cálculo
        }
        portes_response.append(PortePrecoResponse(**porte_dict))

    # Criar resposta do serviço
    servico_dict = {
        "id": servico.id,
        "nome": servico.nome,
        "descricao": servico.descricao,
        "valor_base": servico.valor_base,
        "duracao_estimada": servico.duracao_estimada,
        "categoria_id": servico.categoria_id,
        "ativo": servico.ativo,
        "portes_preco": portes_response
    }

    return ServicoResponse(**servico_dict)
