from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.servicos import Servico
from app.models.porte_preco import PortePreco
from app.schemas.servicos import ServicoCreate, ServicoResponse

router = APIRouter(tags=["servicos"])

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
    return db_servico

@router.get("/", response_model=List[ServicoResponse])
def listar_servicos(db: Session = Depends(get_db)):
    servicos = db.query(Servico).all()
    return servicos

@router.get("/{servico_id}", response_model=ServicoResponse)
def obter_servico(servico_id: int, db: Session = Depends(get_db)):
    servico = db.query(Servico).filter(Servico.id == servico_id).first()
    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    return servico