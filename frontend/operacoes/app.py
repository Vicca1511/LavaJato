import streamlit as st
import requests
import time
import pandas as pd
import sys
import os
from datetime import datetime, timedelta

# Adiciona o backend ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..', 'backend'))

# Configuração da API
API_BASE_URL = "http://localhost:8000/api"

def api_request(endpoint, method="GET", data=None):
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        return response.json() if response.status_code in [200, 201] else None
    except:
        return None

def obter_etapas_servico(servico_id):
    """Retorna etapas específicas baseadas no serviço"""
    etapas_por_servico = {
        1: ["Recepção", "Lavagem Externa", "Secagem", "Entrega"],
        2: ["Recepção", "Lavagem Externa", "Lavagem Interna", "Secagem", "Entrega"],
        3: ["Recepção", "Lavagem Externa", "Polimento", "Secagem", "Entrega"]
    }
    return etapas_por_servico.get(servico_id, ["Recepção", "Entrega"])

def main():
    st.set_page_config(
        page_title="Sistema Lava Jato - Operações",
        page_icon="🔧",
        layout="wide"
    )
    
    st.title("🔧 Setor de Operações - Lava Jato")
    st.markdown("---")
    
    # Menu lateral
    st.sidebar.title("Menu Operações")
    opcao = st.sidebar.selectbox(
        "Selecione a operação:",
        ["Dashboard", "Ordens de Serviço", "Andamento", "Relatórios"]
    )
    
    if opcao == "Dashboard":
        mostrar_dashboard()
    elif opcao == "Ordens de Serviço":
        gerenciar_ordens()
    elif opcao == "Andamento":
        acompanhar_andamento()
    elif opcao == "Relatórios":
        mostrar_relatorios()

def mostrar_dashboard():
    st.subheader("📊 Dashboard de Operações")
    
    try:
        # Métricas rápidas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Ordens Ativas", "12", "+3")
        with col2:
            st.metric("Em Andamento", "8", "+2")
        with col3:
            st.metric("Concluídas Hoje", "5", "+1")
        with col4:
            st.metric("Aguardando", "4", "-1")
        
        # Gráfico de andamento
        st.subheader("Andamento dos Serviços")
        data = {
            'Status': ['Solicitado', 'Confirmado', 'Em Andamento', 'Aguardando Pagamento', 'Finalizado'],
            'Quantidade': [2, 3, 8, 2, 5]
        }
        df = pd.DataFrame(data)
        st.bar_chart(df.set_index('Status'))
        
    except Exception as e:
        st.error(f"Erro ao carregar dashboard: {e}")

def gerenciar_ordens():
    st.subheader("📋 Gerenciar Ordens de Serviço")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("Lista de Ordens de Serviço")
        # Tenta obter ordens da API
        ordens = api_request("/ordens-servico")
        if ordens:
            for ordem in ordens[:5]:  # Mostra apenas 5 primeiras
                st.write(f"**Ordem #{ordem.get('id', 'N/A')}** - {ordem.get('veiculo', 'N/A')}")
        else:
            st.write("Nenhuma ordem encontrada ou erro na API")
        
    with col2:
        st.success("Ações Rápidas")
        if st.button("➕ Nova Ordem"):
            st.info("Funcionalidade em desenvolvimento")
        if st.button("🔄 Atualizar Lista"):
            st.rerun()

def acompanhar_andamento():
    st.subheader("⏱️ Acompanhamento em Tempo Real")
    
    # Simulação de ordens em andamento
    ordens_andamento = [
        {"id": 101, "veiculo": "Toyota Corolla", "etapa": "Lavagem Externa", "progresso": 60},
        {"id": 102, "veiculo": "Honda Civic", "etapa": "Lavagem Interna", "progresso": 30},
        {"id": 103, "veiculo": "Ford Focus", "etapa": "Recepção", "progresso": 10},
        {"id": 104, "veiculo": "Volkswagen Golf", "etapa": "Secagem", "progresso": 90}
    ]
    
    for ordem in ordens_andamento:
        with st.expander(f"Ordem #{ordem['id']} - {ordem['veiculo']}"):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**Etapa:** {ordem['etapa']}")
                st.progress(ordem['progresso'] / 100)
            with col2:
                if st.button("Atualizar", key=f"btn_{ordem['id']}"):
                    st.success(f"Ordem {ordem['id']} atualizada!")

def mostrar_relatorios():
    st.subheader("📈 Relatórios de Produção")
    
    tab1, tab2, tab3 = st.tabs(["Diário", "Semanal", "Mensal"])
    
    with tab1:
        st.info("Relatório de produção do dia")
        dados_diarios = {
            'Hora': ['08:00', '10:00', '12:00', '14:00', '16:00'],
            'Serviços': [3, 5, 2, 4, 3]
        }
        df_diario = pd.DataFrame(dados_diarios)
        st.line_chart(df_diario.set_index('Hora'))
    
    with tab2:
        st.info("Relatório semanal")
        dias_semana = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']
        servicos_semana = [15, 18, 12, 20, 22, 8]
        df_semanal = pd.DataFrame({'Dia': dias_semana, 'Serviços': servicos_semana})
        st.bar_chart(df_semanal.set_index('Dia'))
    
    with tab3:
        st.info("Relatório mensal")
        st.write("Relatório mensal em desenvolvimento")

if __name__ == "__main__":
    main()
