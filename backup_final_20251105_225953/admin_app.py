import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Configura√ß√£o da p√°gina
st.set_page_config(
    page_title="LavaJato Admin - Dashboard",
    page_icon="Ìø¢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URL da API
API_BASE = "http://localhost:8000/api"

st.title("Ìø¢ Sistema LavaJato - Painel Administrativo")
st.markdown("---")

# Fun√ß√µes para API
def get_clientes():
    try:
        response = requests.get(f"{API_BASE}/clientes")
        return response.json() if response.status_code == 200 else []
    except:
        return []

def get_veiculos():
    try:
        response = requests.get(f"{API_BASE}/veiculos/")
        return response.json() if response.status_code == 200 else []
    except:
        return []

def get_servicos():
    try:
        response = requests.get(f"{API_BASE}/servicos/")
        return response.json() if response.status_code == 200 else []
    except:
        return []

def get_categorias():
    try:
        response = requests.get(f"{API_BASE}/categorias/")
        return response.json() if response.status_code == 200 else []
    except:
        return []

def get_ordens_servico():
    try:
        response = requests.get(f"{API_BASE}/ordens-servico/")
        return response.json() if response.status_code == 200 else []
    except:
        return []

def get_fila():
    try:
        response = requests.get(f"{API_BASE}/ordens-servico/fila")
        return response.json() if response.status_code == 200 else []
    except:
        return []

# Sidebar com menu horizontal
st.sidebar.title("ÌæõÔ∏è Painel de Controle")
menu_option = st.sidebar.radio(
    "Navega√ß√£o Principal:",
    ["Ì≥ä Dashboard", "Ì±• Clientes", "Ì∫ó Ve√≠culos", "Ìª†Ô∏è Servi√ßos", "Ì≥ã Categorias", "‚öôÔ∏è Configura√ß√µes"]
)

# DASHBOARD - VIS√ÉO COMPLETA
if menu_option == "Ì≥ä Dashboard":
    st.header("Ì≥ä Dashboard - Vis√£o Geral do Neg√≥cio")
    
    # Carregar dados
    clientes = get_clientes()
    veiculos = get_veiculos()
    servicos = get_servicos()
    categorias = get_categorias()
    ordens = get_ordens_servico()
    fila = get_fila()
    
    # M√©tricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Clientes", len(clientes), "Ì±•")
    with col2:
        st.metric("Total Ve√≠culos", len(veiculos), "Ì∫ó")
    with col3:
        st.metric("Servi√ßos Ativos", len(servicos), "Ìª†Ô∏è")
    with col4:
        receita_total = sum(ordem.get('valor_cobrado', 0) for ordem in ordens)
        st.metric("Receita Total", f"R$ {receita_total:,.2f}", "Ì≤∞")
    
    st.markdown("---")
    
    # Gr√°ficos e visualiza√ß√µes
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Ì≥à Distribui√ß√£o de Ve√≠culos por Porte")
        if veiculos:
            df_veiculos = pd.DataFrame(veiculos)
            porte_counts = df_veiculos['porte'].value_counts()
            fig = px.pie(
                values=porte_counts.values,
                names=porte_counts.index,
                title="Porte dos Ve√≠culos",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum ve√≠culo cadastrado")
    
    with col2:
        st.subheader("Ì≤∞ Pre√ßos dos Servi√ßos")
        if servicos:
            df_servicos = pd.DataFrame(servicos)
            fig = px.bar(
                df_servicos,
                x='nome',
                y='valor_base',
                title="Valor Base dos Servi√ßos",
                color='valor_base',
                color_continuous_scale='viridis'
            )
            fig.update_layout(xaxis_title="Servi√ßo", yaxis_title="Valor (R$)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum servi√ßo cadastrado")
    
    # Fila de servi√ßos
    st.subheader("Ì¥Ñ Fila de Servi√ßos Atuais")
    if fila:
        df_fila = pd.DataFrame(fila)
        st.dataframe(
            df_fila[['posicao_fila', 'veiculo_placa', 'servico_nome', 'status', 'valor_cobrado']],
            use_container_width=True
        )
    else:
        st.success("‚úÖ Nenhum servi√ßo na fila no momento")

# CLIENTES
elif menu_option == "Ì±• Clientes":
    st.header("Ì±• Gerenciamento de Clientes")
    
    tab1, tab2 = st.tabs(["Ì≥ã Lista de Clientes", "Ì≥ä Estat√≠sticas"])
    
    with tab1:
        clientes = get_clientes()
        if clientes:
            df = pd.DataFrame(clientes)
            st.dataframe(df, use_container_width=True)
            
            # A√ß√µes r√°pidas
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    "Ì≥• Exportar CSV",
                    df.to_csv(index=False),
                    "clientes.csv",
                    "text/csv"
                )
            with col2:
                if st.button("Ì¥Ñ Atualizar Dados"):
                    st.rerun()
        else:
            st.info("Nenhum cliente cadastrado ainda.")
    
    with tab2:
        if clientes:
            st.subheader("Estat√≠sticas de Clientes")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Clientes Cadastrados", len(clientes))
                st.metric("Clientes com Email", len([c for c in clientes if c.get('email')]))
            with col2:
                # Gr√°fico de cadastro por per√≠odo (simulado)
                st.write("Ì≥Ö Atividade de Cadastro")
                st.info("Gr√°fico de tend√™ncias em desenvolvimento")

# VE√çCULOS
elif menu_option == "Ì∫ó Ve√≠culos":
    st.header("Ì∫ó Frota de Ve√≠culos")
    
    veiculos = get_veiculos()
    if veiculos:
        df = pd.DataFrame(veiculos)
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            porte_filter = st.selectbox("Filtrar por porte:", ["Todos"] + list(df['porte'].unique()))
        with col2:
            search_term = st.text_input("Buscar por placa ou modelo:")
        
        # Aplicar filtros
        filtered_df = df
        if porte_filter != "Todos":
            filtered_df = filtered_df[filtered_df['porte'] == porte_filter]
        if search_term:
            filtered_df = filtered_df[
                filtered_df['placa'].str.contains(search_term, case=False, na=False) |
                filtered_df['modelo'].str.contains(search_term, case=False, na=False)
            ]
        
        st.dataframe(filtered_df, use_container_width=True)
        st.metric("Ve√≠culos Filtrados", len(filtered_df))
    else:
        st.info("Nenhum ve√≠culo cadastrado ainda.")

# SERVI√áOS
elif menu_option == "Ìª†Ô∏è Servi√ßos":
    st.header("Ìª†Ô∏è Cat√°logo de Servi√ßos")
    
    servicos = get_servicos()
    if servicos:
        for servico in servicos:
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.subheader(f"Ì¥ß {servico['nome']}")
                    st.write(f"*{servico.get('descricao', 'Sem descri√ß√£o')}*")
                
                with col2:
                    st.write(f"**Valor Base:** R$ {servico['valor_base']:.2f}")
                    if 'portes_preco' in servico:
                        st.write("**Pre√ßos:**")
                        for porte in servico['portes_preco']:
                            st.write(f"  - {porte['porte']}: R$ {porte.get('valor_final', servico['valor_base'] * porte['multiplicador']):.2f}")
                
                with col3:
                    st.metric("Dura√ß√£o", f"{servico.get('duracao_estimada', 'N/A')} min")
                
                st.markdown("---")
    else:
        st.info("Nenhum servi√ßo cadastrado ainda.")

# CATEGORIAS
elif menu_option == "Ì≥ã Categorias":
    st.header("Ì≥ã Categorias de Servi√ßos")
    
    categorias = get_categorias()
    if categorias:
        cols = st.columns(3)
        for i, categoria in enumerate(categorias):
            with cols[i % 3]:
                with st.container():
                    st.write(f"**{categoria['nome']}**")
                    st.write(categoria.get('descricao', 'Sem descri√ß√£o'))
                    st.markdown("---")
    else:
        st.info("Nenhuma categoria cadastrada ainda.")

# CONFIGURA√á√ïES
elif menu_option == "‚öôÔ∏è Configura√ß√µes":
    st.header("‚öôÔ∏è Configura√ß√µes do Sistema")
    
    st.subheader("Status da API")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            st.success("‚úÖ API Conectada e Funcionando")
            health_data = response.json()
            st.json(health_data)
        else:
            st.error("‚ùå API com problemas")
    except:
        st.error("Ì¥¥ API Offline")
    
    st.subheader("Estat√≠sticas do Banco")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Clientes", len(get_clientes()))
        st.metric("Ve√≠culos", len(get_veiculos()))
    with col2:
        st.metric("Servi√ßos", len(get_servicos()))
        st.metric("Categorias", len(get_categorias()))

# Status no rodap√© da sidebar
st.sidebar.markdown("---")
st.sidebar.info(f"ÔøΩÔøΩ {datetime.now().strftime('%d/%m/%Y %H:%M')}")
try:
    response = requests.get(f"{API_BASE}/health", timeout=2)
    if response.status_code == 200:
        st.sidebar.success("Ìø¢ Sistema Online")
    else:
        st.sidebar.warning("Ìø° Sistema Inst√°vel")
except:
    st.sidebar.error("Ì¥¥ Sistema Offline")
