#!/usr/bin/env python3
"""
Cria ordens de serviço DIRETO no banco - sem modelos SQLAlchemy
"""
import sqlite3
from datetime import datetime, timedelta

def criar_ordens_direct():
    try:
        # Conecta diretamente ao SQLite
        conn = sqlite3.connect('lavajato.db')
        cursor = conn.cursor()
        
        print("📝 Criando ordens de serviço diretamente no banco...")
        
        # Ordem 1 - Em andamento
        cursor.execute('''
            INSERT INTO ordens_servico 
            (cliente_id, veiculo, placa, status, valor_total, etapa_atual, progresso, observacoes, data_entrada)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            1,  # cliente_id
            "Gol - RHU5F69",  # veiculo
            "RHU5F69",  # placa
            "EM_ANDAMENTO",  # status
            85.50,  # valor_total
            "LAVAGEM_EXTERNA",  # etapa_atual
            60,  # progresso
            "Veículo com muitas manchas de insetos",  # observacoes
            datetime.now().isoformat()  # data_entrada
        ))
        
        # Ordem 2 - Solicitado
        cursor.execute('''
            INSERT INTO ordens_servico 
            (cliente_id, veiculo, placa, status, valor_total, etapa_atual, progresso, observacoes, data_entrada)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            2,  # cliente_id
            "March - OPC6D99",  # veiculo
            "OPC6D99",  # placa
            "SOLICITADO",  # status
            120.00,  # valor_total
            "RECEPCAO",  # etapa_atual
            10,  # progresso
            "Cliente solicitou cera protetora",  # observacoes
            datetime.now().isoformat()  # data_entrada
        ))
        
        # Ordem 3 - Finalizado
        cursor.execute('''
            INSERT INTO ordens_servico 
            (cliente_id, veiculo, placa, status, valor_total, etapa_atual, progresso, observacoes, data_entrada, data_fim)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            5,  # cliente_id
            "HONDA CIVIC TOURING - ABC1234",  # veiculo
            "ABC1234",  # placa
            "FINALIZADO",  # status
            65.00,  # valor_total
            "ENTREGA",  # etapa_atual
            100,  # progresso
            "Serviço concluído com sucesso",  # observacoes
            (datetime.now() - timedelta(days=1)).isoformat(),  # data_entrada
            (datetime.now() - timedelta(hours=3)).isoformat()  # data_fim
        ))
        
        conn.commit()
        
        # Verifica se foram criadas
        cursor.execute("SELECT COUNT(*) FROM ordens_servico")
        total = cursor.fetchone()[0]
        
        print(f"✅ {total} ordens de serviço criadas com sucesso!")
        print("   🟡 Ordem #1 - EM_ANDAMENTO")
        print("   🔵 Ordem #2 - SOLICITADO") 
        print("   🟢 Ordem #3 - FINALIZADO")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao criar ordens: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    criar_ordens_direct()