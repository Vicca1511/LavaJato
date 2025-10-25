#!/bin/bash
echo "ÌæØ PREPARANDO SISTEMA PARA DEMONSTRA√á√ÉO..."

# Zerar banco
echo "Ì∑ëÔ∏è  Zerando banco de dados..."
rm -f backend/lavajato.db

# Recriar banco vazio
echo "Ì¥Ñ Recriando banco vazio..."
cd backend && python -c "
from app.database import Base, engine
from app.models import clientes, veiculos, servicos, porte_preco, categorias
Base.metadata.create_all(bind=engine)
print('‚úÖ Banco recriado!')
"

# Criar algumas categorias b√°sicas
echo "Ì≥ù Criando categorias b√°sicas..."
python -c "
from app.database import SessionLocal
from app.models.categorias import Categoria
db = SessionLocal()

categorias = [
    Categoria(nome='Lavagem B√°sica', descricao='Servi√ßos de limpeza simples', ordem_exibicao=1),
    Categoria(nome='Lavagem Completa', descricao='Servi√ßos de limpeza completa', ordem_exibicao=2),
    Categoria(nome='Est√©tica Automotiva', descricao='Servi√ßos de embelezamento', ordem_exibicao=3)
]

for cat in categorias:
    db.add(cat)

db.commit()
db.close()
print('‚úÖ Categorias b√°sicas criadas!')
"

echo "Ìæä SISTEMA PRONTO PARA DEMONSTRA√á√ÉO!"
echo "Ì∫Ä Para iniciar:"
echo "   Backend: cd backend && python -m uvicorn app.main:app --reload"
echo "   Frontend: cd frontend && streamlit run admin_app.py"
