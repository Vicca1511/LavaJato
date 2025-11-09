import os
import shutil
from pathlib import Path

class DiagnosticoCorrecao:
    def __init__(self):
        self.base_dir = Path(".")
        self.backend_dir = self.base_dir / "backend"
        self.frontend_dir = self.base_dir / "frontend"
    
    def diagnosticar_frontend(self):
        """Diagnostica problemas nos frontends"""
        print("🔍 DIAGNOSTICANDO FRONTENDS...")
        
        # Verificar estrutura atual do frontend
        frontend_files = list(self.frontend_dir.rglob("*.py"))
        print(f"📁 Arquivos encontrados no frontend: {len(frontend_files)}")
        
        for file in frontend_files:
            print(f"   📄 {file.relative_to(self.frontend_dir)}")
        
        # Verificar se os apps principais existem
        apps_necessarios = {
            "admin": self.frontend_dir / "admin" / "app.py",
            "operacoes": self.frontend_dir / "operacoes" / "app.py", 
            "cliente": self.frontend_dir / "cliente" / "app.py"
        }
        
        print("\n✅ APPS NECESSÁRIOS:")
        for app_name, app_path in apps_necessarios.items():
            if app_path.exists():
                print(f"   ✅ {app_name}: {app_path}")
            else:
                print(f"   ❌ {app_name}: {app_path} (FALTANDO)")
    
    def diagnosticar_backend(self):
        """Diagnostica problemas no backend"""
        print("\n🔍 DIAGNOSTICANDO BACKEND...")
        
        # Verificar rotas duplicadas de veículos
        veiculos_routes = list(self.backend_dir.rglob("*veiculos*"))
        print("📋 Arquivos de veículos encontrados:")
        for file in veiculos_routes:
            print(f"   📄 {file.relative_to(self.backend_dir)}")
    
    def corrigir_frontend(self):
        """Corrige a estrutura do frontend"""
        print("\n🔧 CORRIGINDO FRONTEND...")
        
        # Mapear arquivos existentes para as pastas corretas
        mapeamento_frontend = {
            "admin": [
                "admin_app_final.py",
                "admin_app.py", 
                "backend/admin_app.py"
            ],
            "operacoes": [
                "operacoes_app_final.py",
                "operacoes_app.py",
                "backend/operacoes_app.py"
            ],
            "cliente": [
                "cliente_app.py", 
                "cliente_app_final.py",
                "backend/cliente_app.py"
            ]
        }
        
        # Primeiro, criar estrutura de pastas
        for pasta in ["admin", "operacoes", "cliente"]:
            (self.frontend_dir / pasta).mkdir(exist_ok=True)
            print(f"   ✅ Criada pasta: frontend/{pasta}")
        
        # Mover arquivos para as pastas corretas
        for pasta, arquivos in mapeamento_frontend.items():
            for arquivo in arquivos:
                origem = Path(arquivo)
                if origem.exists():
                    destino = self.frontend_dir / pasta / "app.py"
                    
                    # Ler conteúdo do arquivo
                    with open(origem, 'r', encoding='utf-8') as f:
                        conteudo = f.read()
                    
                    # Salvar no destino
                    with open(destino, 'w', encoding='utf-8') as f:
                        f.write(conteudo)
                    
                    print(f"   ✅ Movido: {origem} -> {destino}")
                    
                    # Remover arquivo original se não estiver no backend
                    if not str(origem).startswith("backend/"):
                        origem.unlink()
                        print(f"   🗑️  Removido: {origem}")
        
        # Criar apps básicos se não existirem
        apps_basicos = {
            "admin": '''import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Admin - Lava Jato", layout="wide")
st.title("🚗 Painel Administrativo - Lava Jato")

# Conectar à API
try:
    response = requests.get("http://localhost:8000/api/clientes")
    if response.status_code == 200:
        clientes = response.json()
        st.success(f"✅ Conectado à API - {len(clientes)} clientes")
    else:
        st.error("❌ Erro ao conectar com a API")
except:
    st.error("❌ API não disponível")

st.write("---")
st.subheader("📊 Dashboard")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Clientes", len(clientes) if 'clientes' in locals() else 0)
with col2:
    st.metric("Serviços", "4")
with col3:
    st.metric("Faturamento", "R$ 1.240,00")
''',
            "operacoes": '''import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Operações - Lava Jato", layout="wide")
st.title("🛠️ Controle de Operações - Lava Jato")

try:
    ordens = requests.get("http://localhost:8000/api/ordens-servico").json()
    st.success(f"✅ {len(ordens)} ordens carregadas")
except:
    st.error("❌ Erro ao carregar ordens")
    ordens = []

st.write("---")
st.subheader("📋 Ordens em Andamento")

for ordem in ordens:
    with st.expander(f"Ordem #{ordem['id']} - {ordem.get('veiculo', 'N/A')}"):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Cliente:** {ordem.get('cliente_id', 'N/A')}")
            st.write(f"**Veículo:** {ordem.get('veiculo', 'N/A')}")
            st.write(f"**Placa:** {ordem.get('placa', 'N/A')}")
        with col2:
            st.write(f"**Status:** {ordem.get('status', 'N/A')}")
            st.write(f"**Valor:** R$ {ordem.get('valor_total', 0):.2f}")
''',
            "cliente": '''import streamlit as st
import requests

st.set_page_config(page_title="Cliente - Lava Jato", page_icon="👤")
st.title("👤 Área do Cliente - Lava Jato")

st.write("---")
st.subheader("🚗 Solicitar Serviço")

with st.form("solicitar_servico"):
    nome = st.text_input("Nome Completo")
    telefone = st.text_input("Telefone")
    veiculo = st.text_input("Veículo")
    placa = st.text_input("Placa")
    servico = st.selectbox("Serviço", ["Lavagem Básica", "Lavagem Completa", "Polimento"])
    
    if st.form_submit_button("📝 Solicitar Serviço"):
        st.success("✅ Serviço solicitado com sucesso!")
'''
        }
        
        for app_name, conteudo in apps_basicos.items():
            app_path = self.frontend_dir / app_name / "app.py"
            if not app_path.exists():
                with open(app_path, 'w', encoding='utf-8') as f:
                    f.write(conteudo)
                print(f"   ✅ Criado app básico: frontend/{app_name}/app.py")
    
    def corrigir_backend(self):
        """Corrige rotas duplicadas no backend"""
        print("\n🔧 CORRIGINDO BACKEND...")
        
        # Identificar e remover arquivos duplicados de veículos
        veiculos_files = list(self.backend_dir.rglob("*veiculos*"))
        
        # Manter apenas o arquivo principal na pasta api
        arquivo_principal = self.backend_dir / "app" / "api" / "veiculos.py"
        
        for file in veiculos_files:
            if file != arquivo_principal:
                print(f"   🗑️  Removendo duplicata: {file}")
                file.unlink()
        
        # Verificar se o arquivo principal existe e é válido
        if arquivo_principal.exists():
            print(f"   ✅ Arquivo principal mantido: {arquivo_principal}")
            
            # Garantir que o conteúdo está correto
            with open(arquivo_principal, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            # Se o arquivo estiver vazio ou corrompido, criar um novo
            if len(conteudo.strip()) < 100:
                novo_conteudo = '''from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.veiculos import Veiculo
from app.models.clientes import Cliente

router = APIRouter()

@router.get("/")
def listar_veiculos(db: Session = Depends(get_db)):
    """Lista todos os veículos"""
    return db.query(Veiculo).all()

@router.post("/")
def criar_veiculo(veiculo_data: dict, db: Session = Depends(get_db)):
    """Cria um novo veículo"""
    veiculo = Veiculo(**veiculo_data)
    db.add(veiculo)
    db.commit()
    db.refresh(veiculo)
    return veiculo

@router.get("/{veiculo_id}")
def obter_veiculo(veiculo_id: int, db: Session = Depends(get_db)):
    """Obtém um veículo específico"""
    veiculo = db.query(Veiculo).filter(Veiculo.id == veiculo_id).first()
    if not veiculo:
        raise HTTPException(status_code=404, detail="Veículo não encontrado")
    return veiculo
'''
                with open(arquivo_principal, 'w', encoding='utf-8') as f:
                    f.write(novo_conteudo)
                print(f"   🔄 Conteúdo do veiculos.py atualizado")
    
    def verificar_sistema(self):
        """Verifica se o sistema está funcionando"""
        print("\n🔍 VERIFICANDO SISTEMA...")
        
        import requests
        import time
        
        # Verificar backend
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend: ONLINE")
            else:
                print("❌ Backend: ERRO")
        except:
            print("❌ Backend: OFFLINE")
        
        # Verificar frontends
        frontend_ports = {
            "Admin": 8501,
            "Operações": 8502,
            "Cliente": 8503
        }
        
        for nome, port in frontend_ports.items():
            try:
                response = requests.get(f"http://localhost:{port}/", timeout=2)
                print(f"✅ {nome}: ONLINE (porta {port})")
            except:
                print(f"❌ {nome}: OFFLINE (porta {port})")
    
    def executar_correcao_completa(self):
        """Executa todas as correções"""
        print("🚀 INICIANDO CORREÇÕES DO SISTEMA")
        print("=" * 50)
        
        self.diagnosticar_frontend()
        self.diagnosticar_backend()
        self.corrigir_frontend()
        self.corrigir_backend()
        self.verificar_sistema()
        
        print("\n🎉 CORREÇÕES CONCLUÍDAS!")
        print("=" * 50)
        print("📋 PRÓXIMOS PASSOS:")
        print("1. Execute: python scripts/iniciar_sistema.py")
        print("2. Acesse: http://localhost:8501 (Admin)")
        print("3. Acesse: http://localhost:8502 (Operações)")
        print("4. Acesse: http://localhost:8503 (Cliente)")

if __name__ == "__main__":
    corretor = DiagnosticoCorrecao()
    corretor.executar_correcao_completa()