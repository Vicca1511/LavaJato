import sys
import os

# Adicionar o backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.database import get_db
from app.models.ordens_servico import OrdemServico

def limpar_ordens_antigas():
    """Remove todas as ordens de serviço existentes"""
    db = next(get_db())
    try:
        # Contar ordens antes
        total_antes = db.query(OrdemServico).count()
        print(f"Ordens antes da limpeza: {total_antes}")
        
        # Remover todas as ordens
        db.query(OrdemServico).delete()
        db.commit()
        
        # Contar após
        total_depois = db.query(OrdemServico).count()
        print(f"Ordens após limpeza: {total_depois}")
        print("✅ Banco de dados limpo com sucesso!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao limpar banco: {e}")

if __name__ == "__main__":
    limpar_ordens_antigas()
