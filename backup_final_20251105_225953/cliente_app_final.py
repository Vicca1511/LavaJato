import streamlit as st
import requests
import json

# Configuração da página
st.set_page_config(
    page_title="LavaJato - Area do Cliente",
    layout="wide"
)

# Configurações
API_URL = "http://localhost:8000"

st.title("LavaJato Express - Area do Cliente")
st.markdown("---")

# Funções auxiliares
def fazer_requisicao_api(endpoint, metodo="GET", dados=None):
    try:
        url = f"{API_URL}{endpoint}"
        if metodo == "GET":
            response = requests.get(url)
        elif metodo == "POST":
            response = requests.post(url, json=dados)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erro na API: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Erro de conexao: {e}")
        return None

# Menu lateral
st.sidebar.title("Menu do Cliente")
opcao = st.sidebar.selectbox(
    "Escolha uma opcao:",
    ["Cadastrar Cliente", "Consultar Veiculos", "Agendar Servico"]
)

if opcao == "Cadastrar Cliente":
    st.header("Cadastro de Cliente")
    
    with st.form("cadastro_cliente"):
        nome = st.text_input("Nome completo*")
        cpf = st.text_input("CPF* (somente numeros)", max_chars=11)
        telefone = st.text_input("Telefone*")
        email = st.text_input("Email")
        
        if st.form_submit_button("Cadastrar"):
            if nome and cpf and telefone:
                cliente_data = {
                    "nome": nome,
                    "cpf": cpf,
                    "telefone": telefone,
                    "email": email
                }
                
                resultado = fazer_requisicao_api("/api/clientes/", "POST", cliente_data)
                if resultado:
                    st.success("Cliente cadastrado com sucesso!")
            else:
                st.error("Preencha os campos obrigatorios")

elif opcao == "Consultar Veiculos":
    st.header("Consultar Veiculos por CPF")
    
    cpf_consulta = st.text_input("Digite seu CPF (somente numeros):", key="cpf_consulta")
    
    if st.button("Consultar Veiculos"):
        if cpf_consulta:
            clientes = fazer_requisicao_api("/api/clientes/")
            if clientes:
                cliente_encontrado = None
                for cliente in clientes:
                    if cliente.get('cpf', '').replace('.', '').replace('-', '') == cpf_consulta:
                        cliente_encontrado = cliente
                        break
                
                if cliente_encontrado:
                    st.success(f"Cliente encontrado: {cliente_encontrado['nome']}")
                    veiculos = fazer_requisicao_api(f"/api/veiculos/cliente/{cliente_encontrado['id']}")
                    if veiculos:
                        for veiculo in veiculos:
                            st.write(f"Placa: {veiculo['placa']}")
                            st.write(f"Modelo: {veiculo['modelo']}")
                            st.write(f"Cor: {veiculo['cor']}")
                            st.markdown("---")
                else:
                    st.error("Cliente nao encontrado")
        else:
            st.error("Digite um CPF")

elif opcao == "Agendar Servico":
    st.header("Agendar Servico")
    st.info("Funcionalidade em desenvolvimento")

# Rodape
st.markdown("---")
st.markdown("Duvidas? Entre em contato: (11) 99999-9999")
