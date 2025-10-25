from app.database import SessionLocal
from app.models.categorias import Categoria
from app.models.servicos import Servico
from app.models.porte_preco import PortePreco

def criar_dados_demo():
    db = SessionLocal()
    
    try:
        print("ÌæØ CRIANDO DADOS DE DEMONSTRA√á√ÉO...")
        
        # Criar categorias
        categorias = [
            Categoria(nome="Lavagem B√°sica", descricao="Servi√ßos de limpeza simples", ordem_exibicao=1),
            Categoria(nome="Lavagem Completa", descricao="Servi√ßos de limpeza completa", ordem_exibicao=2),
            Categoria(nome="Est√©tica Automotiva", descricao="Servi√ßos de embelezamento", ordem_exibicao=3)
        ]
        
        for cat in categorias:
            db.add(cat)
        
        db.commit()
        print("‚úÖ Categorias criadas!")
        
        # Criar servi√ßos de exemplo (opcional - pode fazer ao vivo)
        print("Ì≥ù Servi√ßos podem ser criados durante a demonstra√ß√£o ao vivo")
        
        db.close()
        print("Ìæä SISTEMA PRONTO PARA DEMONSTRA√á√ÉO!")
        
    except Exception as e:
        print(f"‚ùå Erro: {e}")
        db.rollback()

if __name__ == "__main__":
    criar_dados_demo()
