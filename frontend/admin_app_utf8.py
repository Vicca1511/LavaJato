import streamlit as st
import requests
import pandas as pd

# Configura√ß√£o da p√°gina
st.set_page_config(
    page_title="LavaJato Admin",
    page_icon="Ì∫ó",
    layout="wide"
)

# URL da API
API_BASE = "http://localhost:8000/api"

st.title("Ì∫ó Sistema LavaJato - Painel do Propriet√°rio")
st.markdown("---")

# Fun√ß√µes para API
def get_clientes():
    try:
        response = requests.get(f"{API_BASE}/clientes/")
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

# Sidebar para navega√ß√£o
st.sidebar.title("Ì≥ä Menu Admin")
opcao = st.sidebar.selectbox(
    "Selecione a se√ß√£o:",
    ["Ì≥à Dashboard", "Ì±• Clientes", "Ì∫ó Veiculos", "Ìª†Ô∏è Servicos", "Ì≥ã Categorias"]
)

if opcao == "Ì≥à Dashboard":
    st.header("Ì≥à Dashboard Geral")
    
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
    
    st.subheader("Ì≥ä Visao Geral")
    if servicos:
        df_servicos = pd.DataFrame(servicos)
        st.dataframe(df_servicos[['nome', 'valor_base', 'preco_medio']])

elif opcao == "Ì±• Clientes":
    st.header("Ì±• Gerenciar Clientes")
    
    # Formulario para novo cliente
    with st.form("novo_cliente"):
        st.subheader("‚ûï Novo Cliente")
        nome = st.text_input("Nome")
        cpf = st.text_input("CPF")
        telefone = st.text_input("Telefone")
        email = st.text_input("Email")
        
        if st.form_submit_button("Cadastrar Cliente"):
            if nome and cpf and telefone:
                try:
                    response = requests.post(f"{API_BASE}/clientes/", json={
                        "nome": nome,
                        "cpf": cpf,
                        "telefone": telefone,
                        "email": email
                    })
                    if response.status_code == 200:
                        st.success("‚úÖ Cliente cadastrado com sucesso!")
                    else:
                        st.error("‚ùå Erro ao cadastrar cliente")
                except:
                    st.error("‚ùå Erro de conexao com a API")
    
    # Lista de clientes
    st.subheader("Ì≥ã Clientes Cadastrados")
    clientes = get_clientes()
    if clientes:
        st.dataframe(pd.DataFrame(clientes))
    else:
        st.info("Ì≥ù Nenhum cliente cadastrado")

elif opcao == "Ì∫ó Veiculos":
    st.header("Ì∫ó Gerenciar Veiculos")
    
    # Formulario para novo veiculo
    with st.form("novo_veiculo"):
        st.subheader("‚ûï Novo Veiculo")
        clientes = get_clientes()
        if clientes:
            cliente_options = {f"{c['id']} - {c['nome']}": c['id'] for c in clientes}
            cliente_selecionado = st.selectbox("Cliente", list(cliente_options.keys()))
        
        placa = st.text_input("Placa")
        modelo = st.text_input("Modelo")
        cor = st.text_input("Cor")
        porte = st.selectbox("Porte", ["P", "M", "G"])
        observacoes = st.text_area("Observacoes")
        
        if st.form_submit_button("Cadastrar Veiculo"):
            if placa and modelo and cor:
                try:
                    cliente_id = cliente_options[cliente_selecionado]
                    response = requests.post(f"{API_BASE}/veiculos/", json={
                        "placa": placa,
                        "modelo": modelo,
                        "cor": cor,
                        "porte": porte,
                        "observacoes": observacoes,
                        "cliente_id": cliente_id
                    })
                    if response.status_code == 200:
                        st.success("‚úÖ Veiculo cadastrado com sucesso!")
                    else:
                        st.error("‚ùå Erro ao cadastrar veiculo")
                except:
                    st.error("‚ùå Erro de conexao com a API")
        else:
            st.warning("‚ö†Ô∏è Cadastre clientes primeiro")
    
    # Lista de veiculos
    st.subheader("Ì≥ã Veiculos Cadastrados")
    veiculos = get_veiculos()
    if veiculos:
        st.dataframe(pd.DataFrame(veiculos))
    else:
        st.info("Ì≥ù Nenhum veiculo cadastrado")

elif opcao == "Ìª†Ô∏è Servicos":
    st.header("Ìª†Ô∏è Gerenciar Servicos")
    
    # Formulario para novo servico
    with st.form("novo_servico"):
        st.subheader("‚ûï Novo Servico")
        
        categorias = get_categorias()
        if categorias:
            categoria_options = {f"{c['id']} - {c['nome']}": c['id'] for c in categorias}
            categoria_selecionada = st.selectbox("Categoria", list(categoria_options.keys()))
        
        nome = st.text_input("Nome do Servico")
        descricao = st.text_area("Descricao")
        valor_base = st.number_input("Valor Base (R$)", min_value=0.0, step=0.5)
        duracao = st.number_input("Duracao Estimada (minutos)", min_value=0)
        
        st.subheader("Ì≤≤ Precos por Porte")
        col1, col2, col3 = st.columns(3)
        with col1:
            mult_p = st.number_input("Multiplicador P", min_value=1.0, value=1.0, step=0.1)
        with col2:
            mult_m = st.number_input("Multiplicador M", min_value=1.0, value=1.2, step=0.1)
        with col3:
            mult_g = st.number_input("Multiplicador G", min_value=1.0, value=1.4, step=0.1)
        
        if st.form_submit_button("Cadastrar Servico"):
            if nome and valor_base > 0 and categorias:
                try:
                    categoria_id = categoria_options[categoria_selecionada]
                    portes_preco = [
                        {"porte": "P", "multiplicador": mult_p},
                        {"porte": "M", "multiplicador": mult_m},
                        {"porte": "G", "multiplicador": mult_g}
                    ]
                    
                    response = requests.post(f"{API_BASE}/servicos/", json={
                        "nome": nome,
                        "descricao": descricao,
                        "valor_base": valor_base,
                        "duracao_estimada": duracao,
                        "categoria_id": categoria_id,
                        "portes_preco": portes_preco
                    })
                    
                    if response.status_code == 200:
                        st.success("‚úÖ Servico cadastrado com sucesso!")
                    else:
                        st.error("‚ùå Erro ao cadastrar servico")
                except Exception as e:
                    st.error(f"‚ùå Erro: {e}")
            else:
                st.warning("‚ö†Ô∏è Cadastre categorias primeiro")
    
    # Lista de servicos
    st.subheader("Ì≥ã Servicos Cadastrados")
    servicos = get_servicos()
    if servicos:
        for servico in servicos:
            with st.expander(f"Ìª†Ô∏è {servico['nome']} - R$ {servico['valor_base']}"):
                st.write(f"**Descricao:** {servico['descricao']}")
                st.write(f"**Duracao:** {servico['duracao_estimada']} min")
                st.write(f"**Preco Medio:** R$ {servico['preco_medio']}")
                st.write("**Precos por Porte:**")
                for porte in servico['portes_preco']:
                    st.write(f"  - {porte['porte']}: R$ {porte['valor_final']} (x{porte['multiplicador']})")
    else:
        st.info("Ì≥ù Nenhum servico cadastrado")

elif opcao == "Ì≥ã Categorias":
    st.header("Ì≥ã Gerenciar Categorias")
    
    # Formulario para nova categoria
    with st.form("nova_categoria"):
        st.subheader("‚ûï Nova Categoria")
        nome = st.text_input("Nome da Categoria")
        descricao = st.text_area("Descricao")
        ordem = st.number_input("Ordem de Exibicao", min_value=0, value=0)
        
        if st.form_submit_button("Cadastrar Categoria"):
            if nome:
                try:
                    response = requests.post(f"{API_BASE}/categorias/", json={
                        "nome": nome,
                        "descricao": descricao,
                        "ordem_exibicao": ordem
                    })
                    if response.status_code == 200:
                        st.success("‚úÖ Categoria cadastrada com sucesso!")
                    else:
                        st.error("‚ùå Erro ao cadastrar categoria")
                except:
                    st.error("‚ùå Erro de conexao com a API")
    
    # Lista de categorias
    st.subheader("Ì≥ã Categorias Cadastradas")
    categorias = get_categorias()
    if categorias:
        st.dataframe(pd.DataFrame(categorias))
    else:
        st.info("Ì≥ù Nenhuma categoria cadastrada")

# Rodape
st.markdown("---")
st.markdown("Ì∫ó **Sistema LavaJato** - Desenvolvido para otimizar seu negocio!")
