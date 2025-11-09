# frontend/admin/app.py - FOCO: Visualização completa e relatórios
import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000/api"

def api_request(endpoint):
    try:
        response = requests.get(f"{API_BASE}{endpoint}")
        return response.json() if response.status_code == 200 else []
    except:
        return []

def main():
    st.set_page_config(page_title="Painel Admin", page_icon="📊", layout="wide")
    st.title("📊 Painel Administrativo - Visão Completa")
    
    # Carregar dados
    with st.spinner("Carregando dados do sistema..."):
        ordens = api_request("/ordens-servico")
        clientes = api_request("/clientes")
        servicos = api_request("/servicos")
        veiculos = api_request("/veiculos/")
    
    # Métricas em tempo real
    st.subheader("📈 Métricas em Tempo Real")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        ordens_hoje = len([o for o in ordens if str(o.get('data_entrada', '')).startswith(str(datetime.now().date()))])
        st.metric("Ordens Hoje", ordens_hoje)
    
    with col2:
        ordens_ativas = len([o for o in ordens if o.get('status') in ['SOLICITADO', 'EM_ANDAMENTO']])
        st.metric("Ordens Ativas", ordens_ativas)
    
    with col3:
        faturamento_dia = sum(o.get('valor_total', 0) for o in ordens if str(o.get('data_entrada', '')).startswith(str(datetime.now().date())))
        st.metric("Faturamento Hoje", f"R$ {faturamento_dia:.2f}")
    
    with col4:
        tempo_medio = "15 min"  # Placeholder
        st.metric("Tempo Médio", tempo_medio)
    
    # Abas de visualização
    tab1, tab2, tab3 = st.tabs(["🔍 Todas as Ordens", "📋 Clientes/Veículos", "📊 Estatísticas"])
    
    with tab1:
        st.subheader("📋 Todas as Ordens de Serviço")
        
        if ordens:
            # Filtros
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                status_filter = st.selectbox("Filtrar por Status", ["Todos", "SOLICITADO", "EM_ANDAMENTO", "FINALIZADO"])
            with col_f2:
                search_placa = st.text_input("Buscar por Placa")
            
            # Aplicar filtros
            ordens_filtradas = ordens
            if status_filter != "Todos":
                ordens_filtradas = [o for o in ordens_filtradas if o.get('status') == status_filter]
            if search_placa:
                ordens_filtradas = [o for o in ordens_filtradas if search_placa.upper() in o.get('placa', '').upper()]
            
            # Mostrar ordens
            for ordem in sorted(ordens_filtradas, key=lambda x: x.get('data_entrada', ''), reverse=True):
                with st.expander(f"#{ordem['id']} - {ordem.get('veiculo', 'N/A')} ({ordem.get('status', 'N/A')})", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Cliente ID:** {ordem.get('cliente_id', 'N/A')}")
                        st.write(f"**Veículo:** {ordem.get('veiculo', 'N/A')}")
                        st.write(f"**Placa:** {ordem.get('placa', 'N/A')}")
                    with col2:
                        st.write(f"**Status:** {ordem.get('status', 'N/A')}")
                        st.write(f"**Valor:** R$ {ordem.get('valor_total', 0):.2f}")
                        st.write(f"**Data:** {ordem.get('data_entrada', 'N/A')}")
                        st.write(f"**Observações:** {ordem.get('observacoes', 'Nenhuma')}")
        else:
            st.info("Nenhuma ordem cadastrada")
    
    with tab2:
        st.subheader("👥 Clientes e Veículos")
        
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            st.write("**Clientes Cadastrados:**")
            if clientes:
                for cliente in clientes[:10]:  # Mostrar apenas 10
                    st.write(f"- {cliente.get('nome', 'N/A')} ({cliente.get('telefone', 'N/A')})")
            else:
                st.info("Nenhum cliente cadastrado")
        
        with col_c2:
            st.write("**Veículos Cadastrados:**")
            if veiculos:
                for veiculo in veiculos[:10]:  # Mostrar apenas 10
                    st.write(f"- {veiculo.get('placa', 'N/A')} ({veiculo.get('modelo', 'N/A')})")
            else:
                st.info("Nenhum veículo cadastrado")
    
    with tab3:
        st.subheader("📊 Estatísticas do Sistema")
        
        # Estatísticas básicas
        col_s1, col_s2 = st.columns(2)
        
        with col_s1:
            st.write("**Distribuição por Status:**")
            status_count = {}
            for ordem in ordens:
                status = ordem.get('status', 'DESCONHECIDO')
                status_count[status] = status_count.get(status, 0) + 1
            
            for status, count in status_count.items():
                st.write(f"- {status}: {count} ordens")
        
        with col_s2:
            st.write("**Serviços Mais Populares:**")
            servicos_count = {}
            for ordem in ordens:
                servico_id = ordem.get('servico_id')
                if servico_id:
                    servicos_count[servico_id] = servicos_count.get(servico_id, 0) + 1
            
            for servico_id, count in sorted(servicos_count.items(), key=lambda x: x[1], reverse=True)[:3]:
                st.write(f"- Serviço {servico_id}: {count} vezes")

if __name__ == "__main__":
    main()