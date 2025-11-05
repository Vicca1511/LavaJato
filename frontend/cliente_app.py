import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="LavaJato System", page_icon="🚗")
st.title("🚗 LavaJato System")

API_URL = "http://localhost:8000/api"

# Menu simples
option = st.selectbox("Menu", ["Cadastrar Cliente", "Ver Clientes"])

if option == "Cadastrar Cliente":
    st.header("Cadastro de Cliente")
    
    nome = st.text_input("Nome")
    cpf = st.text_input("CPF")
    telefone = st.text_input("Telefone")
    
    if st.button("Cadastrar"):
        if nome and cpf and telefone:
            dados = {"nome": nome, "cpf": cpf, "telefone": telefone}
            try:
                response = requests.post(f"{API_URL}/clientes/", json=dados)
                if response.status_code == 201:
                    st.success("Cliente cadastrado!")
                else:
                    st.error(f"Erro: {response.json()}")
            except:
                st.error("API offline")

else:
    st.header("Clientes Cadastrados")
    try:
        response = requests.get(f"{API_URL}/clientes/")
        if response.status_code == 200:
            clientes = response.json()
            if clientes:
                df = pd.DataFrame(clientes)
                st.dataframe(df)
            else:
                st.info("Nenhum cliente")
    except:
        st.error("API offline")