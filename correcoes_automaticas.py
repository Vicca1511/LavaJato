import os
import shutil
from pathlib import Path
import sqlite3

class CorretorSistema:
    def __init__(self):
        self.base_dir = Path(".")
        self.backend_dir = self.base_dir / "backend"
    
    def criar_arquivos_faltantes(self):
        """Cria arquivos essenciais que podem estar faltando"""
        print("🛠️  CRIANDO ARQUIVOS FALTANTES...")
        
        # Arquivo requirements.txt atualizado
        requirements_content = """fastapi==0.104.1
uvicorn==0.24.0
streamlit==1.28.0
sqlalchemy==2.0.23
cryptography==41.0.7
pandas==2.1.3
plotly==5.17.0
requests==2.31.0
python-multipart==0.0.6
websockets==12.0
python-dotenv==1.0.0
pydantic-settings==2.1.0
"""
        
        with open(self.base_dir / "requirements.txt", "w", encoding="utf-8") as f:
            f.write(requirements_content)
        print("✅ requirements.txt criado/atualizado")
        
        # Arquivo .env de exemplo
        env_content = """# Configurações LGPD
ENCRYPTION_KEY=your_encryption_key_here_change_in_production

# WhatsApp 
WHATSAPP_API_URL=http://localhost:8000
WHATSAPP_API_TOKEN=your_token_here

# Banco de Dados
DATABASE_URL=sqlite:///./lavajato.db

# Segurança
ADMIN_PASSWORD=admin123
"""
        
        env_path = self.backend_dir / ".env"
        if not env_path.exists():
            with open(env_path, "w", encoding="utf-8") as f:
                f.write(env_content)
            print("✅ .env criado (backend/.env)")
        
        # Verificar e criar estrutura de diretórios
        dirs_necessarios = [
            self.backend_dir / "app" / "core",
            self.backend_dir / "app" / "schemas", 
            self.backend_dir / "app" / "services"
        ]
        
        for dir_path in dirs_necessarios:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        print("✅ Estrutura de diretórios verificada")
    
    def verificar_e_corrigir_banco(self):
        """Verifica e corrige estrutura do banco de dados"""
        print("\n🗄️  VERIFICANDO BANCO DE DADOS...")
        
        db_path = self.backend_dir / "lavajato.db"
        
        if not db_path.exists():
            print("❌ Banco de dados não encontrado. Criando...")
            self._criar_banco_dados()
            return
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Verificar tabelas essenciais
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tabelas_existentes = [t[0] for t in cursor.fetchall()]
            
            tabelas_necessarias = ['clientes', 'servicos', 'ordens_servico', 'veiculos', 'categorias']
            
            for tabela in tabelas_necessarias:
                if tabela not in tabelas_existentes:
                    print(f"⚠️  Tabela '{tabela}' não encontrada. Sistema pode ter problemas.")
                else:
                    print(f"✅ Tabela '{tabela}' encontrada")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Erro ao verificar banco: {e}")
    
    def _criar_banco_dados(self):
        """Cria banco de dados básico se não existir"""
        try:
            # Isso será criado automaticamente quando o FastAPI iniciar
            # com os models SQLAlchemy
            print("📋 O banco será criado automaticamente ao iniciar o FastAPI")
            print("   Execute: uvicorn backend.app.main:app --reload")
            
        except Exception as e:
            print(f"❌ Erro ao criar banco: {e}")
    
    def verificar_imports_apps(self):
        """Verifica e corrige imports nos apps Streamlit"""
        print("\n🎨 VERIFICANDO APPS STREAMLIT...")
        
        apps = [
            ("admin_app_final.py", "Admin"),
            ("operacoes_app_final.py", "Operações"),
            ("cliente_app.py", "Cliente")
        ]
        
        for app_file, app_nome in apps:
            app_path = self.base_dir / app_file
            if app_path.exists():
                try:
                    with open(app_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Verificar imports básicos
                    imports_necessarios = [
                        "import streamlit as st",
                        "import requests", 
                        "import pandas as pd"
                    ]
                    
                    for imp in imports_necessarios:
                        if imp not in content:
                            print(f"⚠️  {app_nome}: Import faltando - {imp}")
                        else:
                            print(f"✅ {app_nome}: {imp.split()[1]} OK")
                            
                except Exception as e:
                    print(f"❌ Erro ao verificar {app_nome}: {e}")
            else:
                print(f"❌ Arquivo {app_file} não encontrado")
    
    def executar_correcoes(self):
        """Executa todas as correções"""
        print("🚀 INICIANDO CORREÇÕES AUTOMÁTICAS")
        print("="*50)
        
        self.criar_arquivos_faltantes()
        self.verificar_e_corrigir_banco() 
        self.verificar_imports_apps()
        
        print("\n" + "="*50)
        print("🎉 CORREÇÕES CONCLUÍDAS!")
        print("="*50)
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Instalar dependências: pip install -r requirements.txt")
        print("2. Executar testes: python teste_completo_sistema.py")
        print("3. Iniciar servidor: uvicorn backend.app.main:app --reload")
        print("4. Testar apps Streamlit")

def main():
    corretor = CorretorSistema()
    corretor.executar_correcoes()

if __name__ == "__main__":
    main()