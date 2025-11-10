#!/usr/bin/env python3
"""
Corrige os preços dos serviços DIRETAMENTE no banco
"""
import sqlite3

def corrigir_servicos_direct():
    try:
        # Conecta diretamente ao SQLite
        conn = sqlite3.connect('lavajato.db')
        cursor = conn.cursor()
        
        print("💰 Corrigindo preços dos serviços...")
        
        # Atualiza preços dos serviços
        servicos_precos = [
            ("Ducha", 25.00),
            ("Lavagem interna Simples", 45.00),
            ("Lavagem interna Completa", 85.00),
            ("Lavagem Externa", 35.00)
        ]
        
        for nome, preco in servicos_precos:
            cursor.execute('''
                UPDATE servicos SET preco = ? WHERE nome = ?
            ''', (preco, nome))
            print(f"   ✅ {nome}: R$ {preco:.2f}")
        
        conn.commit()
        print("✅ Preços dos serviços corrigidos!")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao corrigir serviços: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    corrigir_servicos_direct()