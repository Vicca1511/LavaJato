#!/bin/bash
echo "� PREPARANDO SISTEMA PARA DEMONSTRAÇÃO..."

# Zerar banco
echo "�️  Zerando banco de dados..."
rm -f backend/lavajato.db

# Recriar banco vazio
echo "� Recriando banco vazio..."
cd backend && python -c "
from app.database import Base, engine
from app.models import clientes, veiculos, servicos, porte_preco, categorias
Base.metadata.create_all(bind=engine)
print('✅ Banco recriado!')
"

# Criar algumas categorias básicas
echo "� Criando categorias básicas..."
python -c "
from app.database import SessionLocal
from app.models.categorias import Categoria
db = SessionLocal()

categorias = [
    Categoria(nome='Lavagem Básica', descricao='Serviços de limpeza simples', ordem_exibicao=1),
    Categoria(nome='Lavagem Completa', descricao='Serviços de limpeza completa', ordem_exibicao=2),
    Categoria(nome='Estética Automotiva', descricao='Serviços de embelezamento', ordem_exibicao=3)
]

for cat in categorias:
    db.add(cat)

db.commit()
db.close()
print('✅ Categorias básicas criadas!')
"

echo "� SISTEMA PRONTO PARA DEMONSTRAÇÃO!"
echo "� Para iniciar:"
echo "   Backend: cd backend && python -m uvicorn app.main:app --reload"
echo "   Frontend: cd frontend && streamlit run admin_app.py"
