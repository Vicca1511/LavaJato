from app.database import SessionLocal
from app.models.categorias import Categoria
from app.models.servicos import Servico
from app.models.porte_preco import PortePreco

def criar_dados_demo():
    db = SessionLocal()
    
    try:
        print("� CRIANDO DADOS DE DEMONSTRAÇÃO...")
        
        # Criar categorias
        categorias = [
            Categoria(nome="Lavagem Básica", descricao="Serviços de limpeza simples", ordem_exibicao=1),
            Categoria(nome="Lavagem Completa", descricao="Serviços de limpeza completa", ordem_exibicao=2),
            Categoria(nome="Estética Automotiva", descricao="Serviços de embelezamento", ordem_exibicao=3)
        ]
        
        for cat in categorias:
            db.add(cat)
        
        db.commit()
        print("✅ Categorias criadas!")
        
        # Criar serviços de exemplo (opcional - pode fazer ao vivo)
        print("� Serviços podem ser criados durante a demonstração ao vivo")
        
        db.close()
        print("� SISTEMA PRONTO PARA DEMONSTRAÇÃO!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        db.rollback()

if __name__ == "__main__":
    criar_dados_demo()
