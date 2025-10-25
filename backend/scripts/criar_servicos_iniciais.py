#!/usr/bin/env python3
import sys
import os

# Adicionar o diretório pai ao Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.servicos import Servico
from app.models.porte_preco import PortePreco
from app.models.categorias import Categoria

def criar_dados_iniciais():
    db = SessionLocal()
    
    try:
        # Criar categorias
        categorias = [
            Categoria(nome="Lavagens", descricao="Serviços de limpeza", ordem_exibicao=1),
            Categoria(nome="Polimento", descricao="Serviços de polimento e proteção", ordem_exibicao=2),
            Categoria(nome="Higienização", descricao="Limpeza interna profunda", ordem_exibicao=3)
        ]
        
        for categoria in categorias:
            db.add(categoria)
        db.flush()  # Para obter os IDs
        
        # Serviços de Lavagem
        servico1 = Servico(
            nome="Lavagem Externa",
            descricao="Lavagem completa da parte externa do veículo",
            valor_base=30.00,
            duracao_estimada=45,
            categoria_id=categorias[0].id
        )
        
        servico2 = Servico(
            nome="Lavagem Interna",
            descricao="Limpeza completa do interior do veículo", 
            valor_base=30.00,
            duracao_estimada=40,
            categoria_id=categorias[0].id
        )
        
        servico3 = Servico(
            nome="Lavagem Completa",
            descricao="Lavagem externa + interna",
            valor_base=55.00,  # Preço especial pacote
            duracao_estimada=75,
            categoria_id=categorias[0].id
        )
        
        # Polimento
        servico4 = Servico(
            nome="Polimento Completo", 
            descricao="Polimento e proteção da pintura",
            valor_base=80.00,
            duracao_estimada=120,
            categoria_id=categorias[1].id
        )
        
        db.add_all([servico1, servico2, servico3, servico4])
        db.flush()
        
        # Preços por porte para cada serviço
        portes_preco = []
        
        # Lavagem Externa
        portes_preco.extend([
            PortePreco(servico_id=servico1.id, porte="P", multiplicador=1.0),
            PortePreco(servico_id=servico1.id, porte="M", multiplicador=1.3),
            PortePreco(servico_id=servico1.id, porte="G", multiplicador=1.6)
        ])
        
        # Lavagem Interna
        portes_preco.extend([
            PortePreco(servico_id=servico2.id, porte="P", multiplicador=1.0),
            PortePreco(servico_id=servico2.id, porte="M", multiplicador=1.2),
            PortePreco(servico_id=servico2.id, porte="G", multiplicador=1.4)
        ])
        
        # Lavagem Completa
        portes_preco.extend([
            PortePreco(servico_id=servico3.id, porte="P", multiplicador=1.0),
            PortePreco(servico_id=servico3.id, porte="M", multiplicador=1.25),
            PortePreco(servico_id=servico3.id, porte="G", multiplicador=1.5)
        ])
        
        # Polimento
        portes_preco.extend([
            PortePreco(servico_id=servico4.id, porte="P", multiplicador=1.0),
            PortePreco(servico_id=servico4.id, porte="M", multiplicador=1.4),
            PortePreco(servico_id=servico4.id, porte="G", multiplicador=1.8)
        ])
        
        db.add_all(portes_preco)
        db.commit()
        
        print("✅ Dados iniciais criados com sucesso!")
        print("📊 Categorias:", [c.nome for c in categorias])
        print("🚗 Serviços:", [s.nome for s in [servico1, servico2, servico3, servico4]])
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    criar_dados_iniciais()