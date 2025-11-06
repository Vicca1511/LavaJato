import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Configuracao da pagina
st.set_page_config(
    page_title="LavaJato Admin",
    page_icon=":car:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URL da API
API_BASE = "http://localhost:8000/api"

st.title("Sistema LavaJato - Painel Administrativo")
st.markdown("---")

# Variavel de sessao para controle de acesso
if 'admin_authenticated' not in st.session_state:
    st.session_state.admin_authenticated = False

# Funcoes para API
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

# Funcoes de delecao (protegidas)
def deletar_cliente(cliente_id):
    if not st.session_state.admin_authenticated:
        return False, "Acesso nao autorizado"
    try:
        response = requests.delete(f"{API_BASE}/clientes/{cliente_id}")
        return response.status_code == 200, response.json() if response.status_code == 200 else response.text
    except Exception as e:
        return False, str(e)

def deletar_veiculo(veiculo_id):
    if not st.session_state.admin_authenticated:
        return False, "Acesso nao autorizado"
    try:
        response = requests.delete(f"{API_BASE}/veiculos/{veiculo_id}")
        return response.status_code == 200, response.json() if response.status_code == 200 else response.text
    except Exception as e:
        return False, str(e)

def deletar_servico(servico_id):
    if not st.session_state.admin_authenticated:
        return False, "Acesso nao autorizado"
    try:
        response = requests.delete(f"{API_BASE}/servicos/{servico_id}")
        return response.status_code == 200, response.json() if response.status_code == 200 else response.text
    except Exception as e:
        return False, str(e)

def deletar_categoria(categoria_id):
    if not st.session_state.admin_authenticated:
        return False, "Acesso nao autorizado"
    try:
        response = requests.delete(f"{API_BASE}/categorias/{categoria_id}")
        return response.status_code == 200, response.json() if response.status_code == 200 else response.text
    except Exception as e:
        return False, str(e)

# Sistema de autenticacao para acoes criticas
def autenticar_admin():
    st.sidebar.markdown("---")
    st.sidebar.subheader("Controle de Acesso")
    
    if not st.session_state.admin_authenticated:
        senha = st.sidebar.text_input("Senha Administrativa:", type="password")
        if st.sidebar.button("Autorizar Acoes"):
            # Senha simples para demonstracao - em producao usar sistema seguro
            if senha == "admin123":
                st.session_state.admin_authenticated = True
                st.sidebar.success("Acesso autorizado por 30 minutos")
            else:
                st.sidebar.error("Senha incorreta")
    else:
        st.sidebar.success("Acesso autorizado")
        if st.sidebar.button("Revogar Acesso"):
            st.session_state.admin_authenticated = False
            st.rerun()

# Chamar autenticacao
autenticar_admin()

# Sidebar com menu limpo
st.sidebar.title("Painel de Controle")
menu_option = st.sidebar.radio(
    "Navegacao:",
    ["Dashboard", "Clientes", "Veiculos", "Servicos", "Categorias", "Configuracoes"]
)

# DASHBOARD
if menu_option == "Dashboard":
    st.header("Dashboard - Visao Geral")
    
    # Carregar dados
    clientes = get_clientes()
    veiculos = get_veiculos()
    servicos = get_servicos()
    ordens = get_ordens_servico()
    fila = get_fila()
    
    # Metricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Clientes", len(clientes))
    with col2:
        st.metric("Total Veiculos", len(veiculos))
    with col3:
        st.metric("Servicos Ativos", len(servicos))
    with col4:
        receita_total = sum(ordem.get('valor_cobrado', 0) for ordem in ordens)
        st.metric("Receita Total", f"R$ {receita_total:,.2f}")
    
    st.markdown("---")
    
    # Dados em tabelas
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Ultimos Clientes")
        if clientes:
            df_clientes = pd.DataFrame(clientes)
            st.dataframe(df_clientes[['nome', 'telefone', 'data_cadastro']].head(5), use_container_width=True)
        else:
            st.info("Nenhum cliente cadastrado")
    
    with col2:
        st.subheader("Servicos Disponiveis")
        if servicos:
            df_servicos = pd.DataFrame(servicos)
            st.dataframe(df_servicos[['nome', 'valor_base']].head(5), use_container_width=True)
        else:
            st.info("Nenhum servico cadastrado")
    
    # Fila de servicos
    st.subheader("Fila de Servicos Atuais")
    if fila:
        df_fila = pd.DataFrame(fila)
        st.dataframe(
            df_fila[['posicao_fila', 'veiculo_placa', 'servico_nome', 'status', 'valor_cobrado']],
            use_container_width=True
        )
    else:
        st.success("Nenhum servico na fila")

# CLIENTES
elif menu_option == "Clientes":
    st.header("Gerenciamento de Clientes")
    
    tab1, tab2 = st.tabs(["Lista de Clientes", "Cadastrar Cliente"])
    
    with tab1:
        clientes = get_clientes()
        if clientes:
            df = pd.DataFrame(clientes)
            
            # Adicionar coluna de acoes
            df['Acoes'] = ""

            # Exibir tabela
            st.dataframe(df, use_container_width=True)
            
            # Controles de delecao (apos a tabela)
            st.subheader("Gerenciar Clientes")
            col1, col2 = st.columns([3, 1])
            
            with col1:
                cliente_selecionado = st.selectbox(
                    "Selecionar cliente para exclusao:",
                    options=[f"{c['id']} - {c['nome']}" for c in clientes],
                    key="delete_cliente"
                )
            
            with col2:
                if st.button("Excluir Cliente", type="secondary"):
                    if cliente_selecionado:
                        cliente_id = int(cliente_selecionado.split(" - ")[0])
                        confirmacao = st.checkbox(f"Confirmar exclusao do cliente ID {cliente_id}?")
                        if confirmacao:
                            sucesso, mensagem = deletar_cliente(cliente_id)
                            if sucesso:
                                st.success(f"Cliente excluido com sucesso: {mensagem}")
                                st.rerun()
                            else:
                                st.error(f"Erro ao excluir: {mensagem}")
                    else:
                        st.warning("Selecione um cliente para excluir")
            
            # Acoes de exportacao
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    "Exportar CSV",
                    df.to_csv(index=False),
                    "clientes.csv",
                    "text/csv"
                )
        else:
            st.info("Nenhum cliente cadastrado")
    
    with tab2:
        with st.form("cadastro_cliente"):
            st.subheader("Novo Cliente")
            nome = st.text_input("Nome Completo*")
            cpf = st.text_input("CPF*")
            telefone = st.text_input("Telefone*")
            email = st.text_input("Email")
            
            if st.form_submit_button("Cadastrar Cliente"):
                if nome and cpf and telefone:
                    dados = {
                        "nome": nome,
                        "cpf": cpf.replace(".", "").replace("-", ""),
                        "telefone": telefone,
                        "email": email if email else None
                    }
                    try:
                        response = requests.post(f"{API_BASE}/clientes", json=dados)
                        if response.status_code == 201:
                            st.success("Cliente cadastrado com sucesso!")
                            st.rerun()
                        else:
                            st.error(f"Erro: {response.text}")
                    except Exception as e:
                        st.error(f"Erro de conexao: {e}")
                else:
                    st.warning("Preencha todos os campos obrigatorios")

# VEICULOS
elif menu_option == "Veiculos":
    st.header("Frota de Veiculos")
    
    veiculos = get_veiculos()
    if veiculos:
        df = pd.DataFrame(veiculos)
        st.dataframe(df, use_container_width=True)
        
        # Controles de delecao
        st.subheader("Gerenciar Veiculos")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            veiculo_selecionado = st.selectbox(
                "Selecionar veiculo para exclusao:",
                options=[f"{v['id']} - {v['placa']} ({v['modelo']})" for v in veiculos],
                key="delete_veiculo"
            )
        
        with col2:
            if st.button("Excluir Veiculo", type="secondary"):
                if veiculo_selecionado:
                    veiculo_id = int(veiculo_selecionado.split(" - ")[0])
                    confirmacao = st.checkbox(f"Confirmar exclusao do veiculo ID {veiculo_id}?")
                    if confirmacao:
                        sucesso, mensagem = deletar_veiculo(veiculo_id)
                        if sucesso:
                            st.success(f"Veiculo excluido com sucesso: {mensagem}")
                            st.rerun()
                        else:
                            st.error(f"Erro ao excluir: {mensagem}")
                else:
                    st.warning("Selecione um veiculo para excluir")
    else:
        st.info("Nenhum veiculo cadastrado")

# SERVICOS
elif menu_option == "Servicos":
    st.header("Catalogo de Servicos")
    
    servicos = get_servicos()
    if servicos:
        for servico in servicos:
            with st.expander(f"{servico['nome']} - R$ {servico.get('preco_medio', servico['valor_base']):.2f}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"Descricao: {servico.get('descricao', 'Sem descricao')}")
                    st.write(f"Valor Base: R$ {servico['valor_base']:.2f}")
                    if 'portes_preco' in servico:
                        st.write("Precos por Porte:")
                        for porte in servico['portes_preco']:
                            st.write(f"- {porte['porte']}: R$ {porte.get('valor_final', servico['valor_base'] * porte['multiplicador']):.2f}")
                
                with col2:
                    if st.session_state.admin_authenticated:
                        if st.button(f"Excluir", key=f"del_serv_{servico['id']}", type="secondary"):
                            confirmacao = st.checkbox(f"Confirmar exclusao do servico {servico['nome']}?")
                            if confirmacao:
                                sucesso, mensagem = deletar_servico(servico['id'])
                                if sucesso:
                                    st.success(f"Servico excluido: {mensagem}")
                                    st.rerun()
                                else:
                                    st.error(f"Erro: {mensagem}")
    else:
        st.info("Nenhum servico cadastrado")

# CATEGORIAS
elif menu_option == "Categorias":
    st.header("Categorias de Servicos")
    
    categorias = get_categorias()
    if categorias:
        for categoria in categorias:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**{categoria['nome']}**")
                st.write(categoria.get('descricao', 'Sem descricao'))
            
            with col2:
                if st.session_state.admin_authenticated:
                    if st.button(f"Excluir", key=f"del_cat_{categoria['id']}", type="secondary"):
                        confirmacao = st.checkbox(f"Confirmar exclusao da categoria {categoria['nome']}?")
                        if confirmacao:
                            sucesso, mensagem = deletar_categoria(categoria['id'])
                            if sucesso:
                                st.success(f"Categoria excluida: {mensagem}")
                                st.rerun()
                            else:
                                st.error(f"Erro: {mensagem}")
            
            st.markdown("---")
    else:
        st.info("Nenhuma categoria cadastrada")

# CONFIGURACOES
elif menu_option == "Configuracoes":
    st.header("Configuracoes do Sistema")
    
    st.subheader("Status da API")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            st.success("API Conectada e Funcionando")
        else:
            st.error("API com problemas")
    except:
        st.error("API Offline")
    
    st.subheader("Estatisticas do Sistema")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Clientes", len(get_clientes()))
        st.metric("Veiculos", len(get_veiculos()))
    with col2:
        st.metric("Servicos", len(get_servicos()))
        st.metric("Categorias", len(get_categorias()))

# Status no rodape
st.sidebar.markdown("---")
st.sidebar.info(f"Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
try:
    response = requests.get(f"{API_BASE}/health", timeout=2)
    if response.status_code == 200:
        st.sidebar.success("Sistema Online")
    else:
        st.sidebar.warning("Sistema Instavel")
except:
    st.sidebar.error("Sistema Offline")
