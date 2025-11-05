from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.clientes import Cliente
from app.schemas.clientes import ClienteCreate, ClienteResponse

router = APIRouter()

@router.post("", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def criar_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    try:
        # Verificar se CPF já existe
        cliente_existente = db.query(Cliente).filter(Cliente.cpf == cliente.cpf).first()
        if cliente_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CPF já cadastrado"
            )
        
        db_cliente = Cliente(**cliente.model_dump())
        db.add(db_cliente)
        db.commit()
        db.refresh(db_cliente)
        return db_cliente
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar cliente: {str(e)}"
        )

@router.get("", response_model=list[ClienteResponse])
def listar_clientes(db: Session = Depends(get_db)):
    try:
        clientes = db.query(Cliente).all()
        return clientes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar clientes: {str(e)}"
        )

@router.get("/{cliente_id}", response_model=ClienteResponse)
def obter_cliente(cliente_id: int, db: Session = Depends(get_db)):
    try:
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
            )
        return cliente
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar cliente: {str(e)}"
        )

@router.put("/{cliente_id}", response_model=ClienteResponse)
def atualizar_cliente(cliente_id: int, cliente_data: ClienteCreate, db: Session = Depends(get_db)):
    try:
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
            )
        
        # Verificar se novo CPF já existe em outro cliente
        if cliente_data.cpf != cliente.cpf:
            cpf_existente = db.query(Cliente).filter(
                Cliente.cpf == cliente_data.cpf,
                Cliente.id != cliente_id
            ).first()
            if cpf_existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="CPF já cadastrado em outro cliente"
                )
        
        # Atualizar campos
        for field, value in cliente_data.model_dump().items():
            setattr(cliente, field, value)
        
        db.commit()
        db.refresh(cliente)
        return cliente
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar cliente: {str(e)}"
        )

@router.delete("/{cliente_id}")
def excluir_cliente(cliente_id: int, db: Session = Depends(get_db)):
    try:
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
            )
        
        db.delete(cliente)
        db.commit()
        return {"message": "Cliente excluído com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao excluir cliente: {str(e)}"
        )
