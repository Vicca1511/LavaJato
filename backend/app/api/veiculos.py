from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.veiculos import Veiculo
from app.models.clientes import Cliente
from app.schemas.veiculos import VeiculoCreate, VeiculoResponse, VeiculoUpdate

router = APIRouter(tags=["veiculos"])

@router.post("/", response_model=VeiculoResponse, status_code=status.HTTP_201_CREATED)
def criar_veiculo(veiculo: VeiculoCreate, db: Session = Depends(get_db)):
    # Verificar se cliente existe
    cliente = db.query(Cliente).filter(Cliente.id == veiculo.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    db_veiculo = Veiculo(**veiculo.model_dump())
    db.add(db_veiculo)
    db.commit()
    db.refresh(db_veiculo)
    return db_veiculo

@router.get("/", response_model=List[VeiculoResponse])
def listar_veiculos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    veiculos = db.query(Veiculo).offset(skip).limit(limit).all()
    return veiculos

@router.get("/{veiculo_id}", response_model=VeiculoResponse)
def obter_veiculo(veiculo_id: int, db: Session = Depends(get_db)):
    veiculo = db.query(Veiculo).filter(Veiculo.id == veiculo_id).first()
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    return veiculo

@router.put("/{veiculo_id}", response_model=VeiculoResponse)
def atualizar_veiculo(veiculo_id: int, veiculo_data: VeiculoUpdate, db: Session = Depends(get_db)):
    veiculo = db.query(Veiculo).filter(Veiculo.id == veiculo_id).first()
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    
    # Verificar se cliente existe (se for atualizado)
    if veiculo_data.cliente_id and veiculo_data.cliente_id != veiculo.cliente_id:
        cliente = db.query(Cliente).filter(Cliente.id == veiculo_data.cliente_id).first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Atualizar campos
    update_data = veiculo_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(veiculo, field, value)
    
    db.commit()
    db.refresh(veiculo)
    return veiculo

@router.delete("/{veiculo_id}")
def excluir_veiculo(veiculo_id: int, db: Session = Depends(get_db)):
    veiculo = db.query(Veiculo).filter(Veiculo.id == veiculo_id).first()
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    
    db.delete(veiculo)
    db.commit()
    return {"message": "Veículo excluído com sucesso"}
