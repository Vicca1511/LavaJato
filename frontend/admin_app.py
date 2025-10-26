import streamlit as st
import requests
import pandas as pd

# Configuracao da pagina
st.set_page_config(
    page_title="LavaJato Admin",
    page_icon=":car:",
    layout="wide"
)

# URL da API
API_BASE = "http://localhost:8000/api"

st.title("Sistema LavaJato - Painel do Proprietario")
st.markdown("---")

# Funcoes para API CORRIGIDAS - agora aceita 200 e 201
def get_clientes():
    try:
        response = requests.get(f"{API_BASE}/clientes/")
        return response.json() if response.status_code in [200, 201] else []
    except:
        return []

def get_veiculos():
    try:
        response = requests.get(f"{API_BASE}/veiculos/")
        return response.json() if response.status_code in [200, 201] else []
    except:
        return []

def get_servicos():
    try:
        response = requests.get(f"{API_BASE}/servicos/")
        return response.json() if response.status_code in [200, 201] else []
    except:
        return []

def get_categorias():
    try:
        response = requests.get(f"{API_BASE}/categorias/")
        return response.json() if response.status_code in [200, 201] else []
    except:
        return []

# Funcoes de cadastro CORRIGIDAS
def cadastrar_cliente(dados):
    try:
        response = requests.post(f"{API_BASE}/clientes/", json=dados)
        return response.status_code in [200, 201]
    except:
        return False

def cadastrar_veiculo(dados):
    try:
        response = requests.post(f"{API_BASE}/veiculos/", json=dados)
        return response.status_code in [200, 201]
    except:
        return False

def cadastrar_servico(dados):
    try:
        response = requests.post(f"{API_BASE}/servicos/", json=dados)
        return response.status_code in [200, 201]
    except:
        return False

def cadastrar_categoria(dados):
    try:
        response = requests.post(f"{API_BASE}/categorias/", json=dados)
        return response.status_code in [200, 201]
    except:
        return False

# Sidebar para navegacao
st.sidebar.title("Menu Admin")
opcao = st.sidebar.selectbox(
    "Selecione a secao:",
    ["Dashboard", "Clientes", "Veiculos", "Servicos", "Categorias"]
)

if opcao == "Dashboard":
    st.header("Dashboard Geral")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        clientes = get_clientes()
        st.metric("Total Clientes", len(clientes))
    with col2:
        veiculos = get_veiculos()
        st.metric("Total Veiculos", len(veiculos))
    with col3:
        servicos = get_servicos()
        st.metric("Total Servicos", len(servicos))
    with col4:
        categorias = get_categorias()
        st.metric("Total Categorias", len(categorias))

elif opcao == "Clientes":
    st.header("Gerenciar Clientes")
    with st.form("novo_cliente", clear_on_submit=True):
        st.subheader("Novo Cliente")
        nome = st.text_input("Nome")
        cpf = st.text_input("CPF")
        telefone = st.text_input("Telefone")
        email = st.text_input("Email")
        submitted = st.form_submit_button("Cadastrar Cliente")
        if submitted:
            if nome and cpf and telefone:
                if cadastrar_cliente({"nome": nome, "cpf": cpf, "telefone": telefone, "email": email}):
                    st.success("✅ Cliente cadastrado com sucesso! Campos limpos.")
                else:
                    st.error("❌ Erro ao cadastrar cliente")
            else:
                st.warning("⚠️ Preencha Nome, CPF e Telefone")
    st.subheader("Clientes Cadastrados")
    clientes = get_clientes()
    if clientes:
        st.dataframe(pd.DataFrame(clientes))

elif opcao == "Veiculos":
    st.header("Gerenciar Veiculos")
    with st.form("novo_veiculo", clear_on_submit=True):
        st.subheader("Novo Veiculo")
        clientes = get_clientes()
        if clientes:
            cliente_options = {f"{c['id']} - {c['nome']}": c['id'] for c in clientes}
            cliente_selecionado = st.selectbox("Cliente", list(cliente_options.keys()))
        placa = st.text_input("Placa")
        modelo = st.text_input("Modelo")
        cor = st.text_input("Cor")
        porte = st.selectbox("Porte", ["P", "M", "G"])
        observacoes = st.text_area("Observacoes")
        submitted = st.form_submit_button("Cadastrar Veiculo")
        if submitted:
            if placa and modelo and cor and clientes:
                cliente_id = cliente_options[cliente_selecionado]
                if cadastrar_veiculo({
                    "placa": placa, "modelo": modelo, "cor": cor, "porte": porte,
                    "observacoes": observacoes, "cliente_id": cliente_id
                }):
                    st.success("✅ Veiculo cadastrado com sucesso! Campos limpos.")
                else:
                    st.error("❌ Erro ao cadastrar veiculo")
    st.subheader("Veiculos Cadastrados")
    veiculos = get_veiculos()
    if veiculos:
        st.dataframe(pd.DataFrame(veiculos))

elif opcao == "Servicos":
    st.header("Gerenciar Servicos")
    with st.form("novo_servico", clear_on_submit=True):
        st.subheader("Novo Servico")
        categorias = get_categorias()
        if categorias:
            categoria_options = {f"{c['id']} - {c['nome']}": c['id'] for c in categorias}
            categoria_selecionada = st.selectbox("Categoria", list(categoria_options.keys()))
        nome = st.text_input("Nome do Servico")
        descricao = st.text_area("Descricao")
        valor_base = st.number_input("Valor Base (R$)", min_value=0.0, step=0.5)
        duracao = st.number_input("Duracao Estimada (minutos)", min_value=0)
        col1, col2, col3 = st.columns(3)
        with col1:
            mult_p = st.number_input("Multiplicador P", min_value=1.0, value=1.0, step=0.1)
        with col2:
            mult_m = st.number_input("Multiplicador M", min_value=1.0, value=1.2, step=0.1)
        with col3:
            mult_g = st.number_input("Multiplicador G", min_value=1.0, value=1.4, step=0.1)
        submitted = st.form_submit_button("Cadastrar Servico")
        if submitted:
            if nome and valor_base > 0 and categorias:
                categoria_id = categoria_options[categoria_selecionada]
                portes_preco = [
                    {"porte": "P", "multiplicador": mult_p},
                    {"porte": "M", "multiplicador": mult_m},
                    {"porte": "G", "multiplicador": mult_g}
                ]
                if cadastrar_servico({
                    "nome": nome, "descricao": descricao, "valor_base": valor_base,
                    "duracao_estimada": duracao, "categoria_id": categoria_id,
                    "portes_preco": portes_preco
                }):
                    st.success("✅ Servico cadastrado com sucesso! Campos limpos.")
                else:
                    st.error("❌ Erro ao cadastrar servico")
    st.subheader("Servicos Cadastrados")
    servicos = get_servicos()
    if servicos:
        for servico in servicos:
            with st.expander(f"{servico['nome']} - R$ {servico['valor_base']}"):
                st.write(f"Descricao: {servico['descricao']}")

elif opcao == "Categorias":
    st.header("Gerenciar Categorias")
    with st.form("nova_categoria", clear_on_submit=True):
        st.subheader("Nova Categoria")
        nome = st.text_input("Nome da Categoria")
        descricao = st.text_area("Descricao")
        ordem = st.number_input("Ordem de Exibicao", min_value=0, value=0)
        submitted = st.form_submit_button("Cadastrar Categoria")
        if submitted:
            if nome:
                if cadastrar_categoria({"nome": nome, "descricao": descricao, "ordem_exibicao": ordem}):
                    st.success("✅ Categoria cadastrada com sucesso! Campos limpos.")
                else:
                    st.error("❌ Erro ao cadastrar categoria")
    st.subheader("Categorias Cadastradas")
    categorias = get_categorias()
    if categorias:
        st.dataframe(pd.DataFrame(categorias))

st.markdown("---")
st.markdown("🚗 Sistema LavaJato - Desenvolvido para otimizar seu negocio!")