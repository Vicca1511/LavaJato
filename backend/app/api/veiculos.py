from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.veiculos import Veiculo
from ..models.clientes import Cliente
from ..schemas.veiculos import VeiculoCreate, VeiculoResponse

router = APIRouter(prefix="/veiculos", tags=["veiculos"])

@router.post("/", response_model=VeiculoResponse, status_code=status.HTTP_201_CREATED)
def criar_veiculo(veiculo: VeiculoCreate, db: Session = Depends(get_db)):
    """Cria um novo veículo para um cliente"""
    
    # Verificar se cliente existe
    cliente = db.query(Cliente).filter(Cliente.id == veiculo.cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    # Verificar se placa já existe
    veiculo_existente = db.query(Veiculo).filter(Veiculo.placa == veiculo.placa).first()
    if veiculo_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Placa já cadastrada"
        )
    
    try:
        db_veiculo = Veiculo(**veiculo.dict())
        db.add(db_veiculo)
        db.commit()
        db.refresh(db_veiculo)
        return db_veiculo
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar veículo: {str(e)}"
        )

@router.get("/", response_model=List[VeiculoResponse])
def listar_veiculos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista todos os veículos"""
    veiculos = db.query(Veiculo).offset(skip).limit(limit).all()
    return veiculos

@router.get("/cliente/{cliente_id}", response_model=List[VeiculoResponse])
def listar_veiculos_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Lista veículos de um cliente específico"""
    
    # Verificar se cliente existe
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    veiculos = db.query(Veiculo).filter(Veiculo.cliente_id == cliente_id).all()
    
    # ✅ MELHORIA: Retornar mensagem informativa se não houver veículos
    if not veiculos:
        return []  # FastAPI automaticamente retorna array vazio
        # Alternativa: poderíamos retornar mensagem, mas manteremos o contrato da API
    
    return veiculos

@router.get("/{veiculo_id}", response_model=VeiculoResponse)
def obter_veiculo(veiculo_id: int, db: Session = Depends(get_db)):
    """Obtém um veículo específico"""
    veiculo = db.query(Veiculo).filter(Veiculo.id == veiculo_id).first()
    if not veiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado"
        )
    return veiculo

# ✅ NOVO ENDPOINT: Buscar cliente + veículos
@router.get("/cliente/{cliente_id}/completo")
def obter_cliente_com_veiculos(cliente_id: int, db: Session = Depends(get_db)):
    """Obtém cliente com todos os veículos (resposta customizada)"""
    
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    veiculos = db.query(Veiculo).filter(Veiculo.cliente_id == cliente_id).all()
    
    # ✅ RESPOSTA MAIS INFORMATIVA
    return {
        "cliente": {
            "id": cliente.id,
            "nome": cliente.nome,
            "cpf": cliente.cpf,
            "telefone": cliente.telefone
        },
        "veiculos": veiculos,
        "total_veiculos": len(veiculos),
        "mensagem": f"Cliente possui {len(veiculos)} veículo(s) cadastrado(s)" if veiculos else "Cliente não possui veículos cadastrados"
    }