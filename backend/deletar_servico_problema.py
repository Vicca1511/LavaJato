from app.database import SessionLocal
from app.models.servicos import Servico

db = SessionLocal()
try:
    # Encontrar e deletar o serviço problemático
    servico_problema = db.query(Servico).filter(Servico.nome == "string").first()
    
    if servico_problema:
        print(f"���️ Deletando serviço problemático: {servico_problema.nome}")
        db.delete(servico_problema)
        db.commit()
        print("✅ Serviço deletado com sucesso!")
    else:
        print("✅ Serviço 'string' não encontrado (já foi corrigido)")
        
except Exception as e:
    db.rollback()
    print(f"❌ Erro: {e}")
finally:
    db.close()
