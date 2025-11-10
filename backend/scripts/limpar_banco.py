#!/usr/bin/env python3
"""
Limpeza DIRETA do banco - sem modelos SQLAlchemy
"""
import sqlite3
import os

def clean_direct():
    try:
        # Conecta diretamente ao SQLite
        db_path = 'lavajato.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Conta antes
        cursor.execute("SELECT COUNT(*) FROM ordens_servico")
        total_antes = cursor.fetchone()[0]
        print(f'Ordens antes: {total_antes}')
        
        if total_antes > 0:
            print("Removendo ordens de serviço...")
            cursor.execute("DELETE FROM ordens_servico")
            conn.commit()
            
            # Conta depois
            cursor.execute("SELECT COUNT(*) FROM ordens_servico")
            total_depois = cursor.fetchone()[0]
            print(f'Ordens depois: {total_depois} - Banco limpo!')
        else:
            print('Banco já está vazio!')
            
        conn.close()
        print("✅ Limpeza concluída com sucesso!")
        
    except Exception as e:
        print(f'❌ Erro: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    clean_direct()