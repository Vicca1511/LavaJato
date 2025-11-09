# frontend/cliente/app.py - FOCO: Criação de cliente e solicitação de serviço
import streamlit as st
import requests
import time

API_BASE = "http://localhost:8000/api"

def api_request(endpoint, method="GET", data=None):
    try:
        url = f"{API_BASE}{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        return response.json() if response.status_code in [200, 201] else None
    except:
        return None

def main():
    st.set_page_config(page_title="Solicitar Serviço", page_icon="👤", layout="wide")
    st.title("👤 Área do Cliente - Solicitar Serviço")
    
    tab1, tab2 = st.tabs(["📝 Cadastrar Cliente", "🚗 Solicitar Serviço"])
    
    with tab1:
        st.subheader("Cadastro de Cliente")
        with st.form("cadastro_cliente"):
            nome = st.text_input("Nome Completo")
            cpf = st.text_input("CPF")
            telefone = st.text_input("Telefone")
            email = st.text_input("Email")
            
            if st.form_submit_button("Cadastrar Cliente"):
                if nome and cpf and telefone:
                    cliente_data = {
                        "nome": nome,
                        "cpf": cpf,
                        "telefone": telefone,
                        "email": email
                    }
                    result = api_request("/clientes", "POST", cliente_data)
                    if result:
                        st.success("Cliente cadastrado com sucesso!")
                    else:
                        st.error("Erro ao cadastrar cliente")
    
    with tab2:
        st.subheader("Solicitar Serviço de Lavagem")
        
        # Carregar dados
        clientes = api_request("/clientes") or []
        servicos = api_request("/servicos") or []
        
        with st.form("solicitar_servico"):
            col1, col2 = st.columns(2)
            
            with col1:
                if clientes:
                    cliente_opcoes = [f"{c['id']} - {c['nome']}" for c in clientes]
                    cliente_sel = st.selectbox("Cliente", cliente_opcoes)
                    cliente_id = cliente_sel.split(" - ")[0] if " - " in cliente_sel else None
                else:
                    st.warning("Cadastre um cliente primeiro")
                    cliente_id = None
                
                veiculo_modelo = st.text_input("Modelo do Veículo")
                veiculo_placa = st.text_input("Placa")
                veiculo_cor = st.text_input("Cor")
            
            with col2:
                if servicos:
                    servico_opcoes = [f"{s['id']} - {s['nome']} (R$ {s['valor_base']})" for s in servicos]
                    servico_sel = st.selectbox("Serviço", servico_opcoes)
                    servico_id = servico_sel.split(" - ")[0] if " - " in servico_sel else None
                else:
                    st.warning("Nenhum serviço disponível")
                    servico_id = None
                
                observacoes = st.text_area("Observações")
            
            if st.form_submit_button("🚀 Solicitar Serviço"):
                if cliente_id and veiculo_modelo and veiculo_placa and servico_id:
                    # Primeiro criar veículo
                    veiculo_data = {
                        "cliente_id": int(cliente_id),
                        "modelo": veiculo_modelo,
                        "placa": veiculo_placa.upper(),
                        "cor": veiculo_cor,
                        "porte": "M"
                    }
                    veiculo_result = api_request("/veiculos/", "POST", veiculo_data)
                    
                    if veiculo_result:
                        # Depois criar ordem
                        ordem_data = {
                            "veiculo_id": veiculo_result['id'],
                            "servico_id": int(servico_id),
                            "observacoes": observacoes
                        }
                        ordem_result = api_request("/ordens-servico", "POST", ordem_data)
                        
                        if ordem_result:
                            st.success("✅ Serviço solicitado com sucesso!")
                            st.info(f"Número da ordem: #{ordem_result['id']}")
                        else:
                            st.error("Erro ao criar ordem de serviço")
                    else:
                        st.error("Erro ao cadastrar veículo")
                else:
                    st.error("Preencha todos os campos obrigatórios")

if __name__ == "__main__":
    main()