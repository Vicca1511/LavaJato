from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.clientes import Cliente
from ..schemas.clientes import ClienteCreate, ClienteResponse

# ✅ CORRETO: Criar o router primeiro
router = APIRouter(prefix="/clientes", tags=["clientes"])

@router.post("/", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def criar_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    """Cria um novo cliente"""
    # Verificar se CPF já existe
    db_cliente = db.query(Cliente).filter(Cliente.cpf == cliente.cpf).first()
    if db_cliente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF já cadastrado"
        )
    
    try:
        db_cliente = Cliente(**cliente.dict())
        db.add(db_cliente)
        db.commit()
        db.refresh(db_cliente)
        return db_cliente
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar cliente: {str(e)}"
        )

@router.get("/", response_model=List[ClienteResponse])
def listar_clientes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista todos os clientes"""
    clientes = db.query(Cliente).offset(skip).limit(limit).all()
    return clientes

@router.get("/{cliente_id}", response_model=ClienteResponse)
def obter_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Obtém um cliente específico"""
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    return cliente
