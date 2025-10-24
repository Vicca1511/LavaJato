from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.servicos import Servico
from ..models.porte_preco import PortePreco
from ..schemas.servicos import ServicoCreate, ServicoResponse, ServicoUpdate, PortePrecoResponse

router = APIRouter(prefix="/servicos", tags=["servicos"])

@router.post("/", response_model=ServicoResponse, status_code=status.HTTP_201_CREATED)
def criar_servico(servico: ServicoCreate, db: Session = Depends(get_db)):
    """Cria um novo serviço com seus preços por porte"""
    
    # Verificar se nome já existe
    servico_existente = db.query(Servico).filter(Servico.nome == servico.nome).first()
    if servico_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Serviço com este nome já existe"
        )
    
    try:
        # Criar serviço
        db_servico = Servico(
            nome=servico.nome,
            descricao=servico.descricao,
            valor_base=servico.valor_base,
            duracao_estimada=servico.duracao_estimada,
            categoria=servico.categoria
        )
        db.add(db_servico)
        db.flush()  # Para obter o ID sem commit
        
        # Criar preços por porte
        for porte_preco in servico.portes_preco:
            db_porte_preco = PortePreco(
                servico_id = db_servico.id,
                porte = porte_preco.porte,
                multiplicador = porte_preco.multiplicador
            )
            db.add(db_porte_preco)
        
        db.commit()
        db.refresh(db_servico)
        
        # Carregar portes_preco para resposta
        db_servico.portes_preco = db.query(PortePreco).filter(PortePreco.servico_id == db_servico.id).all()

        return db_servico
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar serviço: {str(e)}"
        )

@router.get("/", response_model=List[ServicoResponse])
def listar_servicos(ativo: bool = True, db: Session = Depends(get_db)):
    """Lista todos os serviços (apenas ativos por padrão)"""
    query = db.query(Servico)
    if ativo:
        query = query.filter(Servico.ativo == True)
    
    servicos = query.all()
    
    # Carregar portes_preco para cada serviço
    for servico in servicos:
        servico.portes_preco = db.query(PortePreco).filter(PortePreco.servico_id == servico.id).all()
    
    return servicos

@router.get("/{servico_id}", response_model=ServicoResponse)
def obter_servico(servico_id: int, db: Session = Depends(get_db)):
    """Obtém um serviço específico"""
    servico = db.query(Servico).filter(Servico.id == servico_id).first()
    if not servico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Serviço não encontrado"
        )
    
    # Carregar portes_preco
    servico.portes_preco = db.query(PortePreco).filter(PortePreco.servico_id == servico_id).all()
    
    return servico

@router.get("/categoria/{categoria}", response_model=List[ServicoResponse])
def listar_servicos_por_categoria(categoria: str, ativo: bool = True, db: Session = Depends(get_db)):
    """Lista serviços por categoria"""
    query = db.query(Servico).filter(Servico.categoria == categoria)
    if ativo:
        query = query.filter(Servico.ativo == True)
    
    servicos = query.all()
    
    for servico in servicos:
        servico.portes_preco = db.query(PortePreco).filter(PortePreco.servico_id == servico.id).all()
    
    return servicos

@router.put("/{servico_id}", response_model=ServicoResponse)
def atualizar_servico(servico_id: int, servico_update: ServicoUpdate, db: Session = Depends(get_db)):
    """Atualiza um serviço existente"""
    db_servico = db.query(Servico).filter(Servico.id == servico_id).first()
    if not db_servico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Serviço não encontrado"
        )
    
    try:
        # Atualizar apenas campos fornecidos
        update_data = servico_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_servico, field, value)
        
        db.commit()
        db.refresh(db_servico)
        
        # Carregar portes_preco
        db_servico.portes_preco = db.query(PortePreco).filter(PortePreco.servico_id == servico_id).all()
        
        return db_servico
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar serviço: {str(e)}"
        )
    
@router.delete("/{servico_id}")
def desativar_servico(servico_id: int, db: Session = Depends(get_db)):
    """Desativa um serviço (soft delete)"""
    servico = db.query(Servico).filter(Servico.id == servico_id).first()
    if not servico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Serviço não encontrado"
        )
    
    servico.ativo = False
    db.commit()
    
    return {"message": "Serviço desativado com sucesso"}

# Endpoint específico para cálculo de preço
@router.get("/{servico_id}/calcular-preco/{porte}")
def calcular_preco_servico(servico_id: int, porte: str, db: Session = Depends(get_db)):
    """Calcula o preço final de um serviço para um porte específico"""
    servico = db.query(Servico).filter(Servico.id == servico_id).first()
    if not servico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Serviço não encontrado"
        )
    
    porte_preco = db.query(PortePreco).filter(
        PortePreco.servico_id == servico_id,
        PortePreco.porte == porte.upper()
    ).first()
    
    if not porte_preco:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Preço para porte {porte} não configurado"
        )
    
    valor_final = servico.valor_base * porte_preco.multiplicador
    
    return {
        "servico": servico.nome,
        "porte": porte.upper(),
        "valor_base": servico.valor_base,
        "multiplicador": porte_preco.multiplicador,
        "valor_final": round(valor_final, 2),
        "duracao_estimada": servico.duracao_estimada
    }    
    
