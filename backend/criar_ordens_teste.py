#!/usr/bin/env python3
"""
Cria ordens de serviço de teste
"""
import sys
import os
sys.path.append('.')

from app.database import get_db
from app.models.ordens_servico import OrdemServico, StatusOrdemServico
from app.models.clientes import Cliente
from app.models.veiculos import Veiculo
from app.models.servicos import Servico
from datetime import datetime, timedelta

def criar_ordens_teste():
    db = next(get_db())
    
    try:
        # Busca clientes e veículos existentes
        clientes = db.query(Cliente).all()
        veiculos = db.query(Veiculo).all()
        servicos = db.query(Servico).all()
        
        if not clientes or not veiculos:
            print("❌ Precisa de clientes e veículos primeiro")
            return
        
        print(f"📝 Criando ordens de serviço...")
        print(f"   👥 Clientes: {len(clientes)}")
        print(f"   🚗 Veículos: {len(veiculos)}")
        print(f"   🔧 Serviços: {len(servicos)}")
        
        # Ordem 1 - Em andamento
        ordem1 = OrdemServico(
            cliente_id=clientes[0].id,
            veiculo=f"{veiculos[0].modelo} - {veiculos[0].placa}",
            placa=veiculos[0].placa,
            status=StatusOrdemServico.EM_ANDAMENTO,
            valor_total=85.50,
            etapa_atual="LAVAGEM_EXTERNA",
            progresso=60,
            observacoes="Veículo com muitas manchas de insetos",
            data_entrada=datetime.now() - timedelta(hours=2)
        )
        db.add(ordem1)
        
        # Ordem 2 - Solicitado
        ordem2 = OrdemServico(
            cliente_id=clientes[1].id,
            veiculo=f"{veiculos[1].modelo} - {veiculos[1].placa}",
            placa=veiculos[1].placa,
            status=StatusOrdemServico.SOLICITADO,
            valor_total=120.00,
            etapa_atual="RECEPCAO",
            progresso=10,
            observacoes="Cliente solicitou cera protetora",
            data_entrada=datetime.now() - timedelta(hours=1)
        )
        db.add(ordem2)
        
        # Ordem 3 - Finalizado
        ordem3 = OrdemServico(
            cliente_id=clientes[2].id,
            veiculo=f"{veiculos[2].modelo} - {veiculos[2].placa}",
            placa=veiculos[2].placa,
            status=StatusOrdemServico.FINALIZADO,
            valor_total=65.00,
            etapa_atual="ENTREGA",
            progresso=100,
            observacoes="Serviço concluído com sucesso",
            data_entrada=datetime.now() - timedelta(days=1),
            data_fim=datetime.now() - timedelta(hours=3)
        )
        db.add(ordem3)
        
        db.commit()
        print("✅ 3 ordens de serviço criadas com sucesso!")
        print("   🟡 Ordem #1 - EM_ANDAMENTO")
        print("   🔵 Ordem #2 - SOLICITADO") 
        print("   🟢 Ordem #3 - FINALIZADO")
        
    except Exception as e:
        print(f"❌ Erro ao criar ordens: {e}")
        db.rollback()

if __name__ == "__main__":
    criar_ordens_teste()