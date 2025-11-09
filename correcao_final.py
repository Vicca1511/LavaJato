import os
import shutil
from pathlib import Path
import chardet

class CorrecaoFinal:
    def __init__(self):
        self.base_dir = Path(".")
        self.frontend_dir = self.base_dir / "frontend"
    
    def detectar_encoding(self, arquivo):
        """Detecta o encoding de um arquivo"""
        with open(arquivo, 'rb') as f:
            raw_data = f.read()
        return chardet.detect(raw_data)['encoding']
    
    def corrigir_encoding_arquivos(self):
        """Corrige problemas de encoding nos arquivos do frontend"""
        print("🔧 CORRIGINDO ENCODING DOS ARQUIVOS...")
        
        arquivos_frontend = list(self.frontend_dir.rglob("*.py"))
        
        for arquivo in arquivos_frontend:
            try:
                # Detectar encoding
                encoding = self.detectar_encoding(arquivo)
                
                if encoding != 'utf-8':
                    print(f"   🔄 Convertendo {arquivo.name} de {encoding} para UTF-8")
                    
                    # Ler com encoding correto
                    with open(arquivo, 'r', encoding=encoding, errors='replace') as f:
                        conteudo = f.read()
                    
                    # Salvar com UTF-8
                    with open(arquivo, 'w', encoding='utf-8') as f:
                        f.write(conteudo)
                    
                    print(f"   ✅ {arquivo.name} convertido para UTF-8")
                    
            except Exception as e:
                print(f"   ❌ Erro em {arquivo.name}: {e}")
    
    def criar_apps_faltantes(self):
        """Cria os apps que estão faltando"""
        print("\n📝 CRIANDO APPS FALTANTES...")
        
        # Conteúdo para o app de operações
        conteudo_operacoes = '''import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Sistema de Operações - Lava Jato",
    page_icon="🚗",
    layout="wide"
)

# URL da API
API_BASE = "http://localhost:8000/api"

def fazer_requisicao(endpoint, metodo="GET", dados=None):
    """Faz requisições para a API"""
    try:
        url = f"{API_BASE}{endpoint}"
        if metodo == "GET":
            response = requests.get(url)
        elif metodo == "POST":
            response = requests.post(url, json=dados)
        elif metodo == "PUT":
            response = requests.put(url, json=dados)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erro na requisição: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return None

def main():
    st.title("🛠️ Sistema de Operações - Lava Jato")
    st.markdown("---")
    
    # Carregar dados
    with st.spinner("Carregando dados..."):
        ordens = fazer_requisicao("/ordens-servico") or []
        clientes = fazer_requisicao("/clientes") or []
        servicos = fazer_requisicao("/servicos") or []
    
    # Abas para diferentes funcionalidades
    tab1, tab2, tab3 = st.tabs(["📋 Ordens em Andamento", "🔄 Gerenciar Ordens", "📊 Estatísticas"])
    
    with tab1:
        st.subheader("Ordens em Andamento")
        if not ordens:
            st.info("Nenhuma ordem de serviço encontrada.")
        else:
            for ordem in ordens:
                status_color = {
                    'SOLICITADO': '🟡',
                    'EM_ANDAMENTO': '🔵', 
                    'FINALIZADO': '🟢',
                    'CANCELADO': '🔴'
                }
                
                with st.expander(f"{status_color.get(ordem.get('status'), '⚪')} Ordem #{ordem['id']} - {ordem.get('veiculo', 'N/A')}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Cliente:** {ordem.get('cliente_id', 'N/A')}")
                        st.write(f"**Veículo:** {ordem.get('veiculo', 'N/A')}")
                    with col2:
                        st.write(f"**Placa:** {ordem.get('placa', 'N/A')}")
                        st.write(f"**Status:** {ordem.get('status', 'N/A')}")
                    with col3:
                        st.write(f"**Valor:** R$ {ordem.get('valor_total', 0):.2f}")
                    
                    # Ações
                    col_btn1, col_btn2, col_btn3 = st.columns(3)
                    with col_btn1:
                        if ordem.get('status') == 'SOLICITADO':
                            if st.button("▶️ Iniciar Serviço", key=f"iniciar_{ordem['id']}"):
                                if fazer_requisicao(f"/ordens-servico/{ordem['id']}", "PUT", {"status": "EM_ANDAMENTO"}):
                                    st.success("Serviço iniciado!")
                                    time.sleep(1)
                                    st.rerun()
                    with col_btn2:
                        if ordem.get('status') == 'EM_ANDAMENTO':
                            if st.button("✅ Finalizar", key=f"finalizar_{ordem['id']}"):
                                if fazer_requisicao(f"/ordens-servico/{ordem['id']}", "PUT", {"status": "FINALIZADO"}):
                                    st.success("Serviço finalizado!")
                                    time.sleep(1)
                                    st.rerun()
                    with col_btn3:
                        if st.button("📱 Notificar", key=f"notificar_{ordem['id']}"):
                            resultado = fazer_requisicao(f"/whatsapp/ordem/{ordem['id']}/notificar", "POST")
                            if resultado:
                                st.success("Notificação enviada!")
    
    with tab2:
        st.subheader("Criar Nova Ordem")
        
        with st.form("nova_ordem"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Selecionar cliente
                opcoes_clientes = [f"{c['id']} - {c.get('nome', 'N/A')}" for c in clientes]
                cliente_selecionado = st.selectbox("Cliente", opcoes_clientes) if clientes else "Nenhum cliente"
                cliente_id = cliente_selecionado.split(" - ")[0] if clientes and " - " in cliente_selecionado else None
                
                veiculo = st.text_input("Veículo", placeholder="Ex: Honda Civic")
                placa = st.text_input("Placa", placeholder="Ex: ABC1234")
            
            with col2:
                # Selecionar serviço
                opcoes_servicos = [f"{s['id']} - {s.get('nome', 'N/A')} (R$ {s.get('preco_base', 0):.2f})" for s in servicos]
                servico_selecionado = st.selectbox("Serviço", opcoes_servicos) if servicos else "Nenhum serviço"
                servico_id = servico_selecionado.split(" - ")[0] if servicos and " - " in servico_selecionado else None
                
                observacoes = st.text_area("Observações", placeholder="Observações adicionais...")
            
            if st.form_submit_button("📝 Criar Ordem"):
                if cliente_id and veiculo and placa and servico_id:
                    dados = {
                        "cliente_id": int(cliente_id),
                        "veiculo": veiculo,
                        "placa": placa.upper(),
                        "servico_id": int(servico_id),
                        "observacoes": observacoes
                    }
                    resultado = fazer_requisicao("/ordens-servico", "POST", dados)
                    if resultado:
                        st.success("Ordem criada com sucesso!")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.error("Preencha todos os campos obrigatórios!")
    
    with tab3:
        st.subheader("Estatísticas de Operações")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Ordens", len(ordens))
        with col2:
            ordens_andamento = len([o for o in ordens if o.get('status') == 'EM_ANDAMENTO'])
            st.metric("Em Andamento", ordens_andamento)
        with col3:
            ordens_finalizadas = len([o for o in ordens if o.get('status') == 'FINALIZADO'])
            st.metric("Finalizadas", ordens_finalizadas)
        with col4:
            faturamento = sum([o.get('valor_total', 0) for o in ordens if o.get('status') == 'FINALIZADO'])
            st.metric("Faturamento", f"R$ {faturamento:.2f}")
        
        # Gráfico simples de status
        if ordens:
            status_count = {}
            for ordem in ordens:
                status = ordem.get('status', 'DESCONHECIDO')
                status_count[status] = status_count.get(status, 0) + 1
            
            st.write("**Distribuição por Status:**")
            for status, count in status_count.items():
                st.write(f"- {status}: {count}")

if __name__ == "__main__":
    main()
'''

        # Conteúdo para o app do cliente
        conteudo_cliente = '''import streamlit as st
import requests
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="Área do Cliente - Lava Jato",
    page_icon="👤",
    layout="centered"
)

st.title("👤 Área do Cliente - Lava Jato")
st.markdown("---")

# URL da API
API_BASE = "http://localhost:8000/api"

def fazer_requisicao(endpoint, metodo="GET", dados=None):
    """Faz requisições para a API"""
    try:
        url = f"{API_BASE}{endpoint}"
        if metodo == "GET":
            response = requests.get(url)
        elif metodo == "POST":
            response = requests.post(url, json=dados)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception:
        return None

# Abas
tab1, tab2 = st.tabs(["🚗 Solicitar Serviço", "📋 Meus Serviços"])

with tab1:
    st.subheader("Solicitar Novo Serviço")
    
    # Carregar serviços disponíveis
    servicos = fazer_requisicao("/servicos") or []
    
    with st.form("solicitar_servico"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome Completo*", placeholder="Seu nome completo")
            telefone = st.text_input("Telefone*", placeholder="(11) 99999-9999")
            email = st.text_input("E-mail", placeholder="seu@email.com")
        
        with col2:
            veiculo = st.text_input("Veículo*", placeholder="Ex: Honda Civic")
            placa = st.text_input("Placa*", placeholder="Ex: ABC1234")
            cor = st.text_input("Cor do Veículo", placeholder="Ex: Prata")
        
        # Seleção de serviço
        if servicos:
            opcoes_servicos = {f"{s['id']}": f"{s.get('nome', 'Serviço')} - R$ {s.get('preco_base', 0):.2f}" for s in servicos}
            servico_selecionado = st.selectbox(
                "Serviço Desejado*",
                options=list(opcoes_servicos.keys()),
                format_func=lambda x: opcoes_servicos[x]
            )
        else:
            servico_selecionado = None
            st.warning("Nenhum serviço disponível no momento")
        
        observacoes = st.text_area("Observações Adicionais", placeholder="Alguma observação especial...")
        
        # Termos
        aceitar_termos = st.checkbox("Aceito os termos de serviço e política de privacidade*")
        
        if st.form_submit_button("📝 Solicitar Serviço", type="primary"):
            if not all([nome, telefone, veiculo, placa, servico_selecionado, aceitar_termos]):
                st.error("Por favor, preencha todos os campos obrigatórios (*)")
            else:
                # Primeiro, criar o cliente se necessário (em um sistema real, verificar se já existe)
                dados_cliente = {
                    "nome": nome,
                    "telefone": telefone,
                    "email": email if email else None
                }
                
                # Criar ordem de serviço
                dados_ordem = {
                    "cliente_id": 1,  # Em um sistema real, usar o ID do cliente criado/buscado
                    "veiculo": veiculo,
                    "placa": placa.upper(),
                    "servico_id": int(servico_selecionado),
                    "observacoes": f"Cliente: {nome} | Telefone: {telefone} | Cor: {cor} | {observacoes}"
                }
                
                resultado = fazer_requisicao("/ordens-servico", "POST", dados_ordem)
                if resultado:
                    st.success("🎉 Serviço solicitado com sucesso!")
                    st.info("📱 Você receberá uma confirmação por WhatsApp em breve.")
                    st.balloons()
                else:
                    st.error("❌ Erro ao solicitar serviço. Tente novamente.")

with tab2:
    st.subheader("Acompanhar Meus Serviços")
    
    # Em um sistema real, buscar ordens do cliente específico
    ordens = fazer_requisicao("/ordens-servico") or []
    
    if not ordens:
        st.info("Nenhum serviço encontrado.")
    else:
        for ordem in ordens[:5]:  # Mostrar apenas as 5 mais recentes
            with st.expander(f"Ordem #{ordem['id']} - {ordem.get('veiculo', 'Veículo')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Veículo:** {ordem.get('veiculo', 'N/A')}")
                    st.write(f"**Placa:** {ordem.get('placa', 'N/A')}")
                    st.write(f"**Data:** {ordem.get('data_entrada', 'N/A')}")
                with col2:
                    status = ordem.get('status', 'SOLICITADO')
                    status_emoji = {
                        'SOLICITADO': '🟡',
                        'EM_ANDAMENTO': '🔵',
                        'FINALIZADO': '🟢',
                        'CANCELADO': '🔴'
                    }
                    st.write(f"**Status:** {status_emoji.get(status, '⚪')} {status}")
                    st.write(f"**Valor:** R$ {ordem.get('valor_total', 0):.2f}")
                
                if ordem.get('observacoes'):
                    st.write(f"**Observações:** {ordem.get('observacoes')}")

# Rodapé
st.markdown("---")
st.markdown("📞 **Contato:** (11) 9999-9999 | 📧 **E-mail:** contato@lavajato.com")
st.markdown("🕒 **Horário de Funcionamento:** Segunda a Sábado, 8h às 18h")
'''

        # Criar app de operações
        app_operacoes = self.frontend_dir / "operacoes" / "app.py"
        app_operacoes.parent.mkdir(exist_ok=True)
        
        with open(app_operacoes, 'w', encoding='utf-8') as f:
            f.write(conteudo_operacoes)
        print("   ✅ App de operações criado")
        
        # Criar app do cliente
        app_cliente = self.frontend_dir / "cliente" / "app.py"
        app_cliente.parent.mkdir(exist_ok=True)
        
        with open(app_cliente, 'w', encoding='utf-8') as f:
            f.write(conteudo_cliente)
        print("   ✅ App do cliente criado")
    
    def organizar_estrutura_final(self):
        """Organiza a estrutura final do frontend"""
        print("\n📁 ORGANIZANDO ESTRUTURA FINAL...")
        
        # Mover arquivos existentes para estrutura correta
        arquivos_para_mover = [
            (self.frontend_dir / "admin_app.py", self.frontend_dir / "admin" / "app.py"),
            (self.frontend_dir / "operacoes_app.py", self.frontend_dir / "operacoes" / "app_old.py"),
            (self.frontend_dir / "cliente_app.py", self.frontend_dir / "cliente" / "app_old.py"),
        ]
        
        for origem, destino in arquivos_para_mover:
            if origem.exists():
                try:
                    shutil.move(str(origem), str(destino))
                    print(f"   ✅ Movido: {origem.name} -> {destino.parent.name}/{destino.name}")
                except Exception as e:
                    print(f"   ❌ Erro ao mover {origem.name}: {e}")
        
        # Remover arquivos desnecessários
        arquivos_remover = [
            self.frontend_dir / "config.py",
            self.frontend_dir / "cliente" / "cliente_app_final.py",
            self.frontend_dir / "operacoes" / "operacoes_app_final.py", 
            self.frontend_dir / "admin" / "admin_app_final.py"
        ]
        
        for arquivo in arquivos_remover:
            if arquivo.exists():
                try:
                    arquivo.unlink()
                    print(f"   🗑️  Removido: {arquivo}")
                except Exception as e:
                    print(f"   ❌ Erro ao remover {arquivo}: {e}")
    
    def verificar_estrutura_final(self):
        """Verifica a estrutura final"""
        print("\n🔍 VERIFICANDO ESTRUTURA FINAL...")
        
        apps_verificar = [
            self.frontend_dir / "admin" / "app.py",
            self.frontend_dir / "operacoes" / "app.py",
            self.frontend_dir / "cliente" / "app.py"
        ]
        
        for app in apps_verificar:
            if app.exists():
                # Verificar se o arquivo é legível
                try:
                    with open(app, 'r', encoding='utf-8') as f:
                        conteudo = f.read()
                    print(f"   ✅ {app.parent.name}/app.py (OK - {len(conteudo)} caracteres)")
                except Exception as e:
                    print(f"   ❌ {app.parent.name}/app.py (ERRO: {e})")
            else:
                print(f"   ❌ {app.parent.name}/app.py (FALTANDO)")
    
    def executar_correcao_completa(self):
        """Executa todas as correções"""
        print("🚀 EXECUTANDO CORREÇÃO FINAL DO SISTEMA")
        print("=" * 50)
        
        self.corrigir_encoding_arquivos()
        self.criar_apps_faltantes()
        self.organizar_estrutura_final()
        self.verificar_estrutura_final()
        
        print("\n🎉 CORREÇÃO FINAL CONCLUÍDA!")
        print("=" * 50)
        print("📋 ESTRUTURA FINAL DO FRONTEND:")
        print("""
frontend/
├── admin/app.py       ✅ Painel administrativo
├── operacoes/app.py   ✅ Controle de operações  
└── cliente/app.py     ✅ Interface do cliente
        """)
        print("\n🚀 Para iniciar o sistema:")
        print("   python scripts/iniciar_sistema.py")

if __name__ == "__main__":
    corretor = CorrecaoFinal()
    corretor.executar_correcao_completa()