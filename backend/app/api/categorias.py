from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.categorias import Categoria
from app.schemas.categorias import Categoria as CategoriaSchema, CategoriaCreate

router = APIRouter()

@router.get("/", response_model=List[CategoriaSchema])
def listar_categorias(db: Session = Depends(get_db)):
    categorias = db.query(Categoria).all()
    return categorias

@router.post("/", response_model=CategoriaSchema)
def criar_categoria(categoria: CategoriaCreate, db: Session = Depends(get_db)):
    db_categoria = Categoria(**categoria.model_dump())
    db.add(db_categoria)
    db.commit()
    db.refresh(db_categoria)
    return db_categoria

@router.get("/{categoria_id}", response_model=CategoriaSchema)
def obter_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return categoria

@router.put("/{categoria_id}", response_model=CategoriaSchema)
def atualizar_categoria(categoria_id: int, categoria_data: CategoriaCreate, db: Session = Depends(get_db)):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    # Atualizar campos
    for field, value in categoria_data.model_dump().items():
        setattr(categoria, field, value)
    
    db.commit()
    db.refresh(categoria)
    return categoria

@router.delete("/{categoria_id}")
def excluir_categoria(categoria_id: int, db: Session = Depends(get_db)):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    
    db.delete(categoria)
    db.commit()
    return {"message": "Categoria excluída com sucesso"}
