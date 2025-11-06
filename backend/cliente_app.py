import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="LavaJato System - Clientes", 
    page_icon="Ì∫ó",
    layout="wide"
)

API_URL = "http://localhost:8000/api"

st.title("Ì∫ó LavaJato System - √Årea do Cliente")
st.markdown("---")

# Fun√ß√µes para API
def get_clientes():
    try:
        response = requests.get(f"{API_URL}/clientes")
        return response.json() if response.status_code == 200 else []
    except:
        return []

def criar_cliente(dados):
    try:
        response = requests.post(f"{API_URL}/clientes", json=dados)
        return response.status_code == 201, response.json() if response.status_code == 201 else response.text
    except Exception as e:
        return False, str(e)

def get_veiculos():
    try:
        response = requests.get(f"{API_URL}/veiculos/")
        return response.json() if response.status_code == 200 else []
    except:
        return []

def get_servicos():
    try:
        response = requests.get(f"{API_URL}/servicos/")
        return response.json() if response.status_code == 200 else []
    except:
        return []

# Sidebar com menu horizontal (sem drill down)
st.sidebar.title("Ì≥ã Menu R√°pido")
menu_option = st.sidebar.radio(
    "Navega√ß√£o:",
    ["Ì≥ä Dashboard", "Ì±• Clientes", "Ì∫ó Ve√≠culos", "Ìª†Ô∏è Servi√ßos"]
)

# DASHBOARD - NOVO
if menu_option == "Ì≥ä Dashboard":
    st.header("Ì≥ä Dashboard - Vis√£o Geral")
    
    col1, col2, col3, col4 = st.columns(4)
    
    clientes = get_clientes()
    veiculos = get_veiculos()
    servicos = get_servicos()
    
    with col1:
        st.metric("Total Clientes", len(clientes))
    with col2:
        st.metric("Total Ve√≠culos", len(veiculos))
    with col3:
        st.metric("Servi√ßos Ativos", len(servicos))
    with col4:
        st.metric("Sistema", "‚úÖ Online")
    
    # Gr√°ficos r√°pidos
    col1, col2 = st.columns(2)
    
    with col1:
        if clientes:
            df_clientes = pd.DataFrame(clientes)
            st.subheader("Ì≥à √öltimos Clientes")
            st.dataframe(df_clientes[['nome', 'telefone', 'data_cadastro']].head(5), use_container_width=True)
    
    with col2:
        if servicos:
            df_servicos = pd.DataFrame(servicos)
            st.subheader("Ìª†Ô∏è Servi√ßos Dispon√≠veis")
            st.dataframe(df_servicos[['nome', 'valor_base']].head(5), use_container_width=True)

# CLIENTES
elif menu_option == "Ì±• Clientes":
    st.header("Ì±• Gerenciamento de Clientes")
    
    tab1, tab2 = st.tabs(["Ì≥ã Lista de Clientes", "‚ûï Cadastrar Cliente"])
    
    with tab1:
        clientes = get_clientes()
        if clientes:
            df = pd.DataFrame(clientes)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Nenhum cliente cadastrado ainda.")
    
    with tab2:
        with st.form("cadastro_cliente"):
            st.subheader("Novo Cliente")
            nome = st.text_input("Nome Completo*")
            cpf = st.text_input("CPF*", placeholder="000.000.000-00")
            telefone = st.text_input("Telefone*", placeholder="(11) 99999-9999")
            email = st.text_input("Email", placeholder="cliente@email.com")
            
            if st.form_submit_button("Ì≤æ Cadastrar Cliente"):
                if nome and cpf and telefone:
                    dados = {
                        "nome": nome,
                        "cpf": cpf.replace(".", "").replace("-", ""),
                        "telefone": telefone,
                        "email": email if email else None
                    }
                    sucesso, resultado = criar_cliente(dados)
                    if sucesso:
                        st.success("‚úÖ Cliente cadastrado com sucesso!")
                        st.rerun()
                    else:
                        st.error(f"‚ùå Erro: {resultado}")
                else:
                    st.warning("‚ö†Ô∏è Preencha todos os campos obrigat√≥rios (*)")

# VE√çCULOS
elif menu_option == "Ì∫ó Ve√≠culos":
    st.header("Ì∫ó Ve√≠culos Cadastrados")
    veiculos = get_veiculos()
    if veiculos:
        df = pd.DataFrame(veiculos)
        st.dataframe(df[['placa', 'modelo', 'cor', 'porte']], use_container_width=True)
    else:
        st.info("Nenhum ve√≠culo cadastrado ainda.")

# SERVI√áOS
elif menu_option == "Ìª†Ô∏è Servi√ßos":
    st.header("Ìª†Ô∏è Cat√°logo de Servi√ßos")
    servicos = get_servicos()
    if servicos:
        for servico in servicos:
            with st.expander(f"Ì¥ß {servico['nome']} - R$ {servico.get('preco_medio', servico['valor_base']):.2f}"):
                st.write(f"**Descri√ß√£o:** {servico.get('descricao', 'Sem descri√ß√£o')}")
                st.write(f"**Valor Base:** R$ {servico['valor_base']:.2f}")
                if 'portes_preco' in servico:
                    st.write("**Pre√ßos por Porte:**")
                    for porte in servico['portes_preco']:
                        st.write(f"  - {porte['porte']}: R$ {porte.get('valor_final', servico['valor_base'] * porte['multiplicador']):.2f}")
    else:
        st.info("Nenhum servi√ßo cadastrado ainda.")

# Status da API no rodap√©
st.sidebar.markdown("---")
try:
    response = requests.get(f"{API_URL}/health")
    if response.status_code == 200:
        st.sidebar.success("Ìø¢ API Conectada")
    else:
        st.sidebar.error("Ì¥¥ API Offline")
except:
    st.sidebar.error("Ì¥¥ API Offline")
