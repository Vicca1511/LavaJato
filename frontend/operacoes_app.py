import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

# Configuracao da pagina
st.set_page_config(
    page_title="LavaJato - Operacoes",
    page_icon=":car:",
    layout="wide"
)

# URL da API
API_BASE = "http://localhost:8000/api"

st.title("LavaJato - Controle de Operacoes")
st.markdown("---")

# Inicializar session state para PIX
if 'pix_data' not in st.session_state:
    st.session_state.pix_data = {}

# Funcoes para API
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

def get_fila():
    try:
        response = requests.get(f"{API_BASE}/agendamentos/fila")
        if response.status_code in [200, 201]:
            return response.json()
        return {"em_espera": [], "em_lavagem": [], "finalizados": []}
    except:
        return {"em_espera": [], "em_lavagem": [], "finalizados": []}

def criar_agendamento(veiculo_id, servico_id, observacoes):
    try:
        response = requests.post(f"{API_BASE}/agendamentos/", json={
            "veiculo_id": veiculo_id,
            "servico_id": servico_id,
            "observacoes": observacoes
        })
        if response.status_code in [200, 201]:
            return response.json()
        return None
    except:
        return None

def iniciar_servico(agendamento_id):
    try:
        response = requests.post(f"{API_BASE}/agendamentos/{agendamento_id}/iniciar")
        return response.status_code in [200, 201]
    except:
        return False

def finalizar_servico(agendamento_id):
    try:
        response = requests.post(f"{API_BASE}/agendamentos/{agendamento_id}/finalizar")
        return response.status_code in [200, 201]
    except:
        return False

def entregar_veiculo(agendamento_id):
    try:
        response = requests.post(f"{API_BASE}/agendamentos/{agendamento_id}/entregar")
        return response.status_code in [200, 201]
    except:
        return False

def gerar_pix(agendamento_id):
    try:
        response = requests.get(f"{API_BASE}/agendamentos/{agendamento_id}/pix")
        if response.status_code in [200, 201]:
            return response.json()
        return None
    except:
        return None

def confirmar_pagamento(agendamento_id):
    try:
        response = requests.post(f"{API_BASE}/agendamentos/{agendamento_id}/confirmar-pagamento")
        return response.status_code in [200, 201]
    except:
        return False

def notificar_whatsapp(agendamento_id):
    try:
        response = requests.post(f"{API_BASE}/agendamentos/{agendamento_id}/notificar-whatsapp")
        if response.status_code in [200, 201]:
            return response.json()
        return None
    except:
        return None

# Sidebar para navegacao
st.sidebar.title("Menu Operacoes")
opcao = st.sidebar.selectbox(
    "Selecione a secao:",
    ["Nova Entrada", "Ver Fila", "Pagamentos", "Relatorios"]
)

if opcao == "Nova Entrada":
    st.header("Nova Entrada na Fila")
    
    with st.form("nova_entrada", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Cliente e Veiculo")
            clientes = get_clientes()
            if clientes:
                cliente_options = {f"{c['id']} - {c['nome']}": c['id'] for c in clientes}
                cliente_selecionado = st.selectbox("Cliente", list(cliente_options.keys()))
                
                # Filtrar veiculos do cliente selecionado
                veiculos_cliente = [v for v in get_veiculos() if v['cliente_id'] == cliente_options[cliente_selecionado]]
                if veiculos_cliente:
                    veiculo_options = {f"{v['id']} - {v['placa']} ({v['modelo']})": v['id'] for v in veiculos_cliente}
                    veiculo_selecionado = st.selectbox("Veiculo", list(veiculo_options.keys()))
                    
                    # Mostrar info do veiculo
                    veiculo_info = next(v for v in veiculos_cliente if v['id'] == veiculo_options[veiculo_selecionado])
                    st.info(f"Porte: {veiculo_info['porte']} | Cor: {veiculo_info['cor']}")
                else:
                    st.warning("Cliente nao possui veiculos cadastrados")
                    veiculo_selecionado = None
            else:
                st.warning("Nenhum cliente cadastrado")
                cliente_selecionado = None
        
        with col2:
            st.subheader("Servico")
            servicos = get_servicos()
            if servicos:
                servico_options = {f"{s['id']} - {s['nome']} (R$ {s['valor_base']})": s['id'] for s in servicos}
                servico_selecionado = st.selectbox("Servico", list(servico_options.keys()))
                
                # Mostrar precos por porte
                servico_info = next(s for s in servicos if s['id'] == servico_options[servico_selecionado])
                st.write("Precos por porte:")
                for porte in servico_info['portes_preco']:
                    st.write(f"- {porte['porte']}: R$ {porte['valor_final']}")
                
                if veiculo_selecionado:
                    porte_veiculo = veiculo_info['porte']
                    preco_final = next(p['valor_final'] for p in servico_info['portes_preco'] if p['porte'] == porte_veiculo)
                    st.success(f"Preco final para este veiculo: R$ {preco_final}")
            else:
                st.warning("Nenhum servico cadastrado")
                servico_selecionado = None
        
        observacoes = st.text_area("Observacoes (opcional)")
        
        submitted = st.form_submit_button("Adicionar na Fila")
        
        if submitted:
            if cliente_selecionado and veiculo_selecionado and servico_selecionado:
                cliente_id = cliente_options[cliente_selecionado]
                veiculo_id = veiculo_options[veiculo_selecionado]
                servico_id = servico_options[servico_selecionado]
                
                resultado = criar_agendamento(veiculo_id, servico_id, observacoes)
                if resultado:
                    st.success(f"Veiculo adicionado na fila! Posicao: {resultado['posicao_fila']}")
                    st.info(f"Codigo de confirmacao: {resultado['codigo_confirmacao']}")
                else:
                    st.error("Erro ao adicionar na fila")
            else:
                st.error("Preencha todos os campos")

elif opcao == "Ver Fila":
    st.header("Fila de Servicos")
    
    # Auto-atualizacao
    if st.button("Atualizar Fila"):
        st.rerun()
    
    fila = get_fila()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Aguardando")
        if fila['em_espera']:
            for agendamento in fila['em_espera']:
                with st.container():
                    # Verificar seguranca para campos que podem nao existir
                    placa = agendamento.get('veiculo', {}).get('placa', f"ID:{agendamento['veiculo_id']}")
                    servico_nome = agendamento.get('servico', {}).get('nome', f"ID:{agendamento['servico_id']}")
                    
                    st.write(f"#{agendamento['posicao_fila']} - {placa}")
                    st.write(f"Servico: {servico_nome}")
                    st.write(f"Valor: R$ {agendamento['valor_cobrado']:.2f}")
                    
                    if st.button(f"Iniciar", key=f"iniciar_{agendamento['id']}"):
                        if iniciar_servico(agendamento['id']):
                            st.success("Servico iniciado!")
                            time.sleep(1)
                            st.rerun()
                    st.markdown("---")
        else:
            st.info("Nenhum veiculo aguardando")
    
    with col2:
        st.subheader("Em Lavagem")
        if fila['em_lavagem']:
            for agendamento in fila['em_lavagem']:
                with st.container():
                    placa = agendamento.get('veiculo', {}).get('placa', f"ID:{agendamento['veiculo_id']}")
                    servico_nome = agendamento.get('servico', {}).get('nome', f"ID:{agendamento['servico_id']}")
                    
                    st.write(f"{placa}")
                    st.write(f"Servico: {servico_nome}")
                    st.write(f"Valor: R$ {agendamento['valor_cobrado']:.2f}")
                    
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button(f"Finalizar", key=f"finalizar_{agendamento['id']}"):
                            if finalizar_servico(agendamento['id']):
                                st.success("Servico finalizado!")
                                time.sleep(1)
                                st.rerun()
                    with col_btn2:
                        # Usar form submit para evitar conflito com session_state
                        with st.form(key=f"pix_form_{agendamento['id']}"):
                            if st.form_submit_button(f"Pix", key=f"pix_btn_{agendamento['id']}"):
                                pix_info = gerar_pix(agendamento['id'])
                                if pix_info and isinstance(pix_info, dict):
                                    st.session_state.pix_data[str(agendamento['id'])] = pix_info
                                    st.rerun()
                                else:
                                    st.error("Erro ao gerar PIX")
                    st.markdown("---")
        else:
            st.info("Nenhum veiculo em lavagem")
    
    with col3:
        st.subheader("Finalizados")
        if fila['finalizados']:
            for agendamento in fila['finalizados']:
                with st.container():
                    placa = agendamento.get('veiculo', {}).get('placa', f"ID:{agendamento['veiculo_id']}")
                    servico_nome = agendamento.get('servico', {}).get('nome', f"ID:{agendamento['servico_id']}")
                    
                    st.write(f"{placa}")
                    st.write(f"Servico: {servico_nome}")
                    st.write(f"Valor: R$ {agendamento['valor_cobrado']:.2f}")
                    st.write(f"Pago: {'Sim' if agendamento['pago'] else 'Nao'}")
                    
                    col_btn1, col_btn2, col_btn3 = st.columns(3)
                    with col_btn1:
                        if not agendamento['pago'] and st.button(f"Pagar", key=f"pagar_{agendamento['id']}"):
                            if confirmar_pagamento(agendamento['id']):
                                st.success("Pagamento confirmado!")
                                time.sleep(1)
                                st.rerun()
                    with col_btn2:
                        if st.button(f"WhatsApp", key=f"whatsapp_{agendamento['id']}"):
                            notificacao = notificar_whatsapp(agendamento['id'])
                            if notificacao:
                                st.success("Notificacao enviada!")
                    with col_btn3:
                        if st.button(f"Entregar", key=f"entregar_{agendamento['id']}"):
                            if entregar_veiculo(agendamento['id']):
                                st.success("Veiculo entregue!")
                                time.sleep(1)
                                st.rerun()
                    st.markdown("---")
        else:
            st.info("Nenhum servico finalizado")
    
    # Mostrar QR Code PIX se gerado - SEPARADO DOS BOT√ïES
    st.markdown("---")
    if st.session_state.pix_data:
        st.subheader("Ì≤∞ QR Codes PIX Gerados")
        for agendamento_id, pix_info in st.session_state.pix_data.items():
            if isinstance(pix_info, dict):
                with st.expander(f"PIX - Agendamento {agendamento_id}"):
                    st.write(f"**Valor:** R$ {pix_info.get('valor', 0):.2f}")
                    st.write(f"**Descricao:** {pix_info.get('descricao', 'N/A')}")
                    st.write(f"**Codigo de confirmacao:** {pix_info.get('codigo_confirmacao', 'N/A')}")
                    st.code(pix_info.get('qr_code', 'QR Code n√£o dispon√≠vel'))
                    
                    if st.button(f"Fechar PIX {agendamento_id}", key=f"close_pix_{agendamento_id}"):
                        del st.session_state.pix_data[agendamento_id]
                        st.rerun()

elif opcao == "Pagamentos":
    st.header("Controle de Pagamentos")
    
    st.info("Relatorios financeiros detalhados")
    
    fila = get_fila()
    total_aguardando_pagamento = sum(a['valor_cobrado'] for a in fila['finalizados'] if not a['pago'])
    total_recebido = sum(a['valor_cobrado'] for a in fila['finalizados'] if a['pago'])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("A Receber", f"R$ {total_aguardando_pagamento:.2f}")
    with col2:
        st.metric("Recebido", f"R$ {total_recebido:.2f}")

elif opcao == "Relatorios":
    st.header("Relatorios do Dia")
    
    hoje = datetime.now().strftime("%d/%m/%Y")
    st.subheader(f"Resumo do Dia - {hoje}")
    
    fila = get_fila()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Aguardando", len(fila['em_espera']))
    with col2:
        st.metric("Em Lavagem", len(fila['em_lavagem']))
    with col3:
        st.metric("Finalizados", len(fila['finalizados']))
    with col4:
        servicos_pagos = len([a for a in fila['finalizados'] if a['pago']])
        st.metric("Pagos", servicos_pagos)
    
    # Detalhamento dos servicos finalizados
    if fila['finalizados']:
        st.subheader("Servicos Finalizados Hoje")
        dados = []
        for agendamento in fila['finalizados']:
            placa = agendamento.get('veiculo', {}).get('placa', f"ID:{agendamento['veiculo_id']}")
            servico_nome = agendamento.get('servico', {}).get('nome', f"ID:{agendamento['servico_id']}")
            
            dados.append({
                "Veiculo": placa,
                "Servico": servico_nome,
                "Valor": f"R$ {agendamento['valor_cobrado']:.2f}",
                "Pago": "Sim" if agendamento['pago'] else "Nao",
                "Codigo": agendamento['codigo_confirmacao']
            })
        st.dataframe(pd.DataFrame(dados))

# Rodape
st.markdown("---")
st.markdown("Sistema LavaJato - Controle completo do seu negocio!")
