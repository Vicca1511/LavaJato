import sqlite3
from pathlib import Path

def criar_tabela_ordens_servico():
    """Cria a tabela ordens_servico faltante"""
    db_path = Path("backend/lavajato.db")
    
    if not db_path.exists():
        print("❌ Banco de dados não encontrado!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Criar tabela ordens_servico
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ordens_servico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            veiculo TEXT NOT NULL,
            placa TEXT NOT NULL,
            status TEXT DEFAULT 'SOLICITADO',
            data_entrada DATETIME DEFAULT CURRENT_TIMESTAMP,
            data_inicio DATETIME,
            data_fim DATETIME,
            valor_total REAL DEFAULT 0.0,
            observacoes TEXT,
            notificado_whatsapp BOOLEAN DEFAULT 0,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )
        ''')
        
        # Inserir algumas ordens de exemplo
        ordens_exemplo = [
            (1, 'Honda Civic', 'ABC1234', 'SOLICITADO', 85.0, 'Lavagem completa'),
            (2, 'Toyota Corolla', 'DEF5678', 'EM_ANDAMENTO', 120.0, 'Lavagem + Polimento'),
            (3, 'Fiat Uno', 'GHI9012', 'FINALIZADO', 45.0, 'Lavagem simples')
        ]
        
        cursor.executemany('''
        INSERT INTO ordens_servico (cliente_id, veiculo, placa, status, valor_total, observacoes)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', ordens_exemplo)
        
        conn.commit()
        conn.close()
        
        print("✅ Tabela 'ordens_servico' criada com sucesso!")
        print("✅ 3 ordens de exemplo inseridas!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar tabela: {e}")
        return False

def verificar_tabelas():
    """Verifica todas as tabelas existentes"""
    db_path = Path("backend/lavajato.db")
    
    if not db_path.exists():
        print("❌ Banco de dados não encontrado!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tabelas = cursor.fetchall()
        
        print("📊 TABELAS EXISTENTES:")
        for tabela in tabelas:
            cursor.execute(f"SELECT COUNT(*) FROM {tabela[0]}")
            count = cursor.fetchone()[0]
            print(f"   ✅ {tabela[0]}: {count} registros")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar tabelas: {e}")

if __name__ == "__main__":
    print("🗄️  CRIANDO TABELA ORDENS_SERVICO")
    print("="*40)
    
    criar_tabela_ordens_servico()
    print()
    verificar_tabelas()