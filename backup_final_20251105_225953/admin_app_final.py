import streamlit as st
import requests
import pandas as pd

# Configuracao da pagina
st.set_page_config(
    page_title="LavaJato Admin",
    layout="wide"
)

# Configuracoes
API_URL = "http://localhost:8000"
st.title("LavaJato Express - Painel Administrativo")
st.markdown("---")

# Variavel global para senha de administrador (apenas para delecoes)
SENHA_ADMIN = "admin123"

# Funcoes auxiliares
def fazer_requisicao(endpoint, metodo="GET", dados=None):
    try:
        url = f"{API_URL}{endpoint}"
        if metodo == "GET":
            response = requests.get(url)
        elif metodo == "POST":
            response = requests.post(url, json=dados)
        elif metodo == "DELETE":
            response = requests.delete(url)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            st.error(f"Erro {response.status_code}: {response.text}")
            return None
    except Exception as e:
        st.error(f"Erro de conexao: {e}")
        return None

def verificar_senha_admin():
    """Verifica se o usuario tem permissao para exclusoes"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("Acoes Administrativas")
    senha = st.sidebar.text_input("Senha para Exclusoes:", type="password")
    return senha == SENHA_ADMIN

# Sidebar com menu
st.sidebar.title("Menu Administrativo")
menu = st.sidebar.selectbox(
    "Selecione a secao:",
    ["Dashboard", "Clientes", "Veiculos", "Servicos", "Categorias", "Ordens de Servico"]
)

# Verificar permissoes de administrador (apenas para exclusoes)
is_admin = verificar_senha_admin()

# DASHBOARD
if menu == "Dashboard":
    st.header("Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Metricas
    with col1:
        clientes = fazer_requisicao("/api/clientes/") or []
        st.metric("Total Clientes", len(clientes))
    
    with col2:
        veiculos = fazer_requisicao("/api/veiculos/") or []
        st.metric("Total Veiculos", len(veiculos))
    
    with col3:
        servicos = fazer_requisicao("/api/servicos/") or []
        st.metric("Servicos", len(servicos))
    
    with col4:
        ordens = fazer_requisicao("/api/ordens-servico/") or []
        st.metric("Ordens na Fila", len(ordens))

# CLIENTES
elif menu == "Clientes":
    st.header("Gestao de Clientes")
    
    tab1, tab2 = st.tabs(["Lista de Clientes", "Novo Cliente"])
    
    with tab1:
        clientes = fazer_requisicao("/api/clientes/") or []
        if clientes:
            df_clientes = pd.DataFrame(clientes)
            st.dataframe(df_clientes, use_container_width=True)
            
            # Opcao de exclusao apenas com senha
            if is_admin:
                st.subheader("Excluir Cliente")
                cliente_excluir = st.selectbox(
                    "Selecione o cliente para excluir:",
                    [f"{c['id']} - {c['nome']} ({c['cpf']})" for c in clientes],
                    key="excluir_cliente"
                )
                
                if st.button("Excluir Cliente", type="secondary"):
                    if cliente_excluir:
                        cliente_id = cliente_excluir.split(" - ")[0]
                        if fazer_requisicao(f"/api/clientes/{cliente_id}", "DELETE"):
                            st.success("Cliente excluido com sucesso!")
                            st.rerun()
            else:
                st.info("Acesso restrito: Funcao de exclusao disponivel apenas com senha de administrador")
        else:
            st.info("Nenhum cliente cadastrado.")
    
    with tab2:
        with st.form("novo_cliente"):
            nome = st.text_input("Nome completo*")
            cpf = st.text_input("CPF*", placeholder="000.000.000-00")
            telefone = st.text_input("Telefone*", placeholder="(11) 99999-9999")
            email = st.text_input("Email", placeholder="cliente@email.com")
            
            if st.form_submit_button("Cadastrar Cliente"):
                if nome and cpf and telefone:
                    dados = {"nome": nome, "cpf": cpf, "telefone": telefone, "email": email}
                    if fazer_requisicao("/api/clientes/", "POST", dados):
                        st.success("Cliente cadastrado com sucesso!")
                        st.rerun()
                else:
                    st.error("Preencha os campos obrigatorios")

# VEICULOS
elif menu == "Veiculos":
    st.header("Gestao de Veiculos")
    
    tab1, tab2 = st.tabs(["Lista de Veiculos", "Novo Veiculo"])
    
    with tab1:
        veiculos = fazer_requisicao("/api/veiculos/") or []
        clientes = fazer_requisicao("/api/clientes/") or []
        
        if veiculos:
            veiculos_com_cliente = []
            for veiculo in veiculos:
                veiculo_info = veiculo.copy()
                cliente_info = next((c for c in clientes if c['id'] == veiculo['cliente_id']), None)
                veiculo_info['cliente_nome'] = cliente_info['nome'] if cliente_info else "N/A"
                veiculos_com_cliente.append(veiculo_info)
            
            df_veiculos = pd.DataFrame(veiculos_com_cliente)
            colunas_importantes = ['id', 'placa', 'modelo', 'cor', 'porte', 'cliente_nome']
            colunas_disponiveis = [col for col in colunas_importantes if col in df_veiculos.columns]
            
            st.dataframe(df_veiculos[colunas_disponiveis], use_container_width=True)
            
            # Opcao de exclusao apenas com senha
            if is_admin:
                st.subheader("Excluir Veiculo")
                veiculo_excluir = st.selectbox(
                    "Selecione o veiculo para excluir:",
                    [f"{v['id']} - {v['placa']} ({v['modelo']})" for v in veiculos],
                    key="excluir_veiculo"
                )
                
                if st.button("Excluir Veiculo", type="secondary"):
                    if veiculo_excluir:
                        veiculo_id = veiculo_excluir.split(" - ")[0]
                        if fazer_requisicao(f"/api/veiculos/{veiculo_id}", "DELETE"):
                            st.success("Veiculo excluido com sucesso!")
                            st.rerun()
            else:
                st.info("Acesso restrito: Funcao de exclusao disponivel apenas com senha de administrador")
        else:
            st.info("Nenhum veiculo cadastrado.")
    
    with tab2:
        clientes = fazer_requisicao("/api/clientes/") or []
        if clientes:
            with st.form("novo_veiculo"):
                cliente_id = st.selectbox(
                    "Cliente*",
                    [f"{c['id']} - {c['nome']} ({c['cpf']})" for c in clientes]
                )
                placa = st.text_input("Placa*", placeholder="ABC1D23").upper()
                marca = st.text_input("Marca*", placeholder="Toyota")
                modelo = st.text_input("Modelo*", placeholder="Corolla")
                ano = st.number_input("Ano", min_value=1990, max_value=2024, value=2020)
                cor = st.text_input("Cor", placeholder="Prata")
                porte = st.selectbox("Porte", ["P", "M", "G"])
                observacoes = st.text_area("Observacoes")
                
                if st.form_submit_button("Cadastrar Veiculo"):
                    if placa and marca and modelo and cliente_id:
                        dados = {
                            "placa": placa,
                            "marca": marca,
                            "modelo": modelo,
                            "ano": ano,
                            "cor": cor,
                            "porte": porte,
                            "observacoes": observacoes,
                            "cliente_id": int(cliente_id.split(" - ")[0])
                        }
                        if fazer_requisicao("/api/veiculos/", "POST", dados):
                            st.success("Veiculo cadastrado com sucesso!")
                            st.rerun()
                    else:
                        st.error("Preencha os campos obrigatorios")
        else:
            st.warning("Cadastre um cliente primeiro!")

# SERVICOS
elif menu == "Servicos":
    st.header("Gestao de Servicos")
    
    tab1, tab2 = st.tabs(["Lista de Servicos", "Novo Servico"])
    
    with tab1:
        servicos = fazer_requisicao("/api/servicos/") or []
        if servicos:
            df_servicos = pd.DataFrame(servicos)
            st.dataframe(df_servicos, use_container_width=True)
            
            # Opcao de exclusao apenas com senha
            if is_admin:
                st.subheader("Excluir Servico")
                servico_excluir = st.selectbox(
                    "Selecione o servico para excluir:",
                    [f"{s['id']} - {s['nome']} (R$ {s['valor_base']})" for s in servicos],
                    key="excluir_servico"
                )
                
                if st.button("Excluir Servico", type="secondary"):
                    if servico_excluir:
                        servico_id = servico_excluir.split(" - ")[0]
                        if fazer_requisicao(f"/api/servicos/{servico_id}", "DELETE"):
                            st.success("Servico excluido com sucesso!")
                            st.rerun()
            else:
                st.info("Acesso restrito: Funcao de exclusao disponivel apenas com senha de administrador")
        else:
            st.info("Nenhum servico cadastrado.")
    
    with tab2:
        # Primeiro precisamos das categorias
        categorias = fazer_requisicao("/api/categorias/") or []
        
        if categorias:
            with st.form("novo_servico"):
                nome = st.text_input("Nome do Servico*")
                descricao = st.text_area("Descricao")
                
                # Selecionar categoria
                categoria_id = st.selectbox(
                    "Categoria*",
                    [f"{cat['id']} - {cat['nome']}" for cat in categorias]
                )
                
                valor_base = st.number_input(
                    "Valor Base Padrao (R$)*", 
                    min_value=0.0, 
                    value=30.0,
                    step=5.0,
                    format="%.2f"
                )
                
                duracao_estimada = st.number_input(
                    "Duracao Estimada (min)*", 
                    min_value=1, 
                    value=30,
                    step=5
                )
                
                st.subheader("Multiplicadores por Porte")
                st.info("O valor final sera: Valor Base x Multiplicador")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write("Porte P")
                    st.metric("Valor Final", f"R$ {valor_base * 0.8:.2f}")
                    mult_p = st.number_input(
                        "Multiplicador", 
                        min_value=0.1, 
                        max_value=2.0,
                        value=0.8,
                        step=0.1,
                        format="%.1f",
                        key="mult_p"
                    )
                
                with col2:
                    st.write("Porte M")
                    st.metric("Valor Final", f"R$ {valor_base * 1.0:.2f}")
                    mult_m = st.number_input(
                        "Multiplicador", 
                        min_value=0.1, 
                        max_value=2.0,
                        value=1.0,
                        step=0.1,
                        format="%.1f",
                        key="mult_m"
                    )
                
                with col3:
                    st.write("Porte G")
                    st.metric("Valor Final", f"R$ {valor_base * 1.2:.2f}")
                    mult_g = st.number_input(
                        "Multiplicador", 
                        min_value=0.1, 
                        max_value=2.0,
                        value=1.2,
                        step=0.1,
                        format="%.1f",
                        key="mult_g"
                    )
                
                if st.form_submit_button("Cadastrar Servico"):
                    if nome and categoria_id:
                        # Calcular valores finais baseados nos multiplicadores
                        dados = {
                            "nome": nome,
                            "descricao": descricao,
                            "valor_base": float(valor_base),
                            "duracao_estimada": int(duracao_estimada),
                            "categoria_id": int(categoria_id.split(" - ")[0]),
                            "portes_preco": [
                                {"porte": "P", "valor": float(valor_base * mult_p), "multiplicador": float(mult_p)},
                                {"porte": "M", "valor": float(valor_base * mult_m), "multiplicador": float(mult_m)},
                                {"porte": "G", "valor": float(valor_base * mult_g), "multiplicador": float(mult_g)}
                            ]
                        }
                        resultado = fazer_requisicao("/api/servicos/", "POST", dados)
                        if resultado:
                            st.success("Servico cadastrado com sucesso!")
                            st.rerun()
                    else:
                        st.error("Preencha os campos obrigatorios")
        else:
            st.warning("Cadastre uma categoria primeiro!")

# CATEGORIAS
elif menu == "Categorias":
    st.header("Gestao de Categorias")
    
    tab1, tab2 = st.tabs(["Lista de Categorias", "Nova Categoria"])
    
    with tab1:
        categorias = fazer_requisicao("/api/categorias/") or []
        if categorias:
            df_categorias = pd.DataFrame(categorias)
            st.dataframe(df_categorias, use_container_width=True)
            
            # Opcao de exclusao apenas com senha
            if is_admin:
                st.subheader("Excluir Categoria")
                categoria_excluir = st.selectbox(
                    "Selecione a categoria para excluir:",
                    [f"{c['id']} - {c['nome']}" for c in categorias],
                    key="excluir_categoria"
                )
                
                if st.button("Excluir Categoria", type="secondary"):
                    if categoria_excluir:
                        categoria_id = categoria_excluir.split(" - ")[0]
                        if fazer_requisicao(f"/api/categorias/{categoria_id}", "DELETE"):
                            st.success("Categoria excluida com sucesso!")
                            st.rerun()
            else:
                st.info("Acesso restrito: Funcao de exclusao disponivel apenas com senha de administrador")
        else:
            st.info("Nenhuma categoria cadastrada.")
    
    with tab2:
        with st.form("nova_categoria"):
            nome = st.text_input("Nome da Categoria*")
            descricao = st.text_area("Descricao")
            
            if st.form_submit_button("Cadastrar Categoria"):
                if nome:
                    dados = {"nome": nome, "descricao": descricao}
                    if fazer_requisicao("/api/categorias/", "POST", dados):
                        st.success("Categoria cadastrada com sucesso!")
                        st.rerun()
                else:
                    st.error("Preencha o nome da categoria")

# ORDENS DE SERVICO
elif menu == "Ordens de Servico":
    st.header("Gestao de Ordens de Servico")
    
    tab1, tab2 = st.tabs(["Fila de Servicos", "Nova Ordem"])
    
    with tab1:
        ordens = fazer_requisicao("/api/ordens-servico/") or []
        if ordens:
            df_ordens = pd.DataFrame(ordens)
            st.dataframe(df_ordens, use_container_width=True)
            
            # Controles para a fila
            st.subheader("Controle da Fila")
            
            col1, col2 = st.columns(2)
            
            with col1:
                ordem_executar = st.selectbox(
                    "Selecionar ordem para executar:",
                    [f"{o['id']} - {o['cliente_nome']} - {o['servico_nome']}" for o in ordens if o['status'] == 'agendado'],
                    key="executar_ordem"
                )
                if st.button("Iniciar Execucao"):
                    if ordem_executar:
                        ordem_id = ordem_executar.split(" - ")[0]
                        if fazer_requisicao(f"/api/ordens-servico/{ordem_id}/status", "PUT", {"status": "em_execucao"}):
                            st.success("Ordem em execucao!")
                            st.rerun()
            
            with col2:
                ordem_concluir = st.selectbox(
                    "Selecionar ordem para concluir:",
                    [f"{o['id']} - {o['cliente_nome']} - {o['servico_nome']}" for o in ordens if o['status'] == 'em_execucao'],
                    key="concluir_ordem"
                )
                if st.button("Concluir Servico"):
                    if ordem_concluir:
                        ordem_id = ordem_concluir.split(" - ")[0]
                        if fazer_requisicao(f"/api/ordens-servico/{ordem_id}/status", "PUT", {"status": "concluido"}):
                            st.success("Servico concluido!")
                            st.rerun()
        else:
            st.info("Nenhuma ordem de servico na fila")
    
    with tab2:
        st.subheader("Criar Nova Ordem de Servico")
        st.info("Para clientes que chegam sem cadastro previo")
        
        clientes = fazer_requisicao("/api/clientes/") or []
        veiculos = fazer_requisicao("/api/veiculos/") or []
        servicos = fazer_requisicao("/api/servicos/") or []
        
        if clientes and veiculos and servicos:
            with st.form("nova_ordem"):
                cliente_id = st.selectbox(
                    "Cliente*",
                    [f"{c['id']} - {c['nome']}" for c in clientes]
                )
                
                veiculo_id = st.selectbox(
                    "Veiculo*",
                    [f"{v['id']} - {v['placa']} ({v['modelo']})" for v in veiculos]
                )
                
                servico_id = st.selectbox(
                    "Servico*",
                    [f"{s['id']} - {s['nome']} (R$ {s['valor_base']})" for s in servicos]
                )
                
                observacoes = st.text_area("Observacoes")
                
                if st.form_submit_button("Criar Ordem de Servico"):
                    if cliente_id and veiculo_id and servico_id:
                        dados = {
                            "cliente_id": int(cliente_id.split(" - ")[0]),
                            "veiculo_id": int(veiculo_id.split(" - ")[0]),
                            "servico_id": int(servico_id.split(" - ")[0]),
                            "observacoes": observacoes
                        }
                        if fazer_requisicao("/api/ordens-servico/", "POST", dados):
                            st.success("Ordem de servico criada com sucesso! Entrou na fila.")
                            st.rerun()
                    else:
                        st.error("Preencha todos os campos obrigatorios")
        else:
            st.warning("E necessario ter clientes, veiculos e servicos cadastrados")

# Informacoes da senha
st.sidebar.markdown("---")
st.sidebar.info("Senha para exclusoes: admin123")
st.sidebar.caption("Apenas exclusoes requerem senha de administrador")

# Rodape
st.markdown("---")
st.caption("Sistema LavaJato Express - Modo Fila por Ordem de Chegada")
