# frontend/operacoes/app.py - FOCO: Acompanhamento em tempo real e evolução de etapas
import streamlit as st
import requests
import time
from datetime import datetime

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
    st.set_page_config(page_title="Controle Operações", page_icon="🛠️", layout="wide")
    st.title("🛠️ Controle de Operações - Tempo Real")
    
    # Auto-refresh
    if st.button("🔄 Atualizar"):
        st.rerun()
    
    # Carregar dados
    ordens = api_request("/ordens-servico") or []
    fila = api_request("/ordens-servico/fila") or []
    
    tab1, tab2 = st.tabs(["📊 Painel Tempo Real", "⚙️ Controle de Etapas"])
    
    with tab1:
        st.subheader("🎯 Fila de Serviços - Tempo Real")
        
        if fila:
            for ordem in fila:
                # Card de ordem
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])
                    
                    with col1:
                        st.write(f"**Ordem #{ordem['id']}**")
                        st.write(f"🔄 {ordem['veiculo_placa']} - Posição: #{ordem['posicao_fila']}")
                        st.write(f"💵 R$ {ordem['valor_cobrado']:.2f}")
                    
                    with col2:
                        status_color = {
                            'SOLICITADO': '🟡 Aguardando',
                            'EM_ANDAMENTO': '🔵 Em Andamento', 
                            'FINALIZADO': '🟢 Finalizado'
                        }
                        st.write(f"**Status:** {status_color.get(ordem['status'], ordem['status'])}")
                    
                    with col3:
                        if ordem['status'] == 'SOLICITADO':
                            if st.button("▶️ Iniciar", key=f"start_{ordem['id']}"):
                                if api_request(f"/fluxo/ordens/{ordem['id']}/iniciar", "POST"):
                                    st.success("Iniciado!")
                                    time.sleep(1)
                                    st.rerun()
                        elif ordem['status'] == 'EM_ANDAMENTO':
                            if st.button("✅ Finalizar", key=f"end_{ordem['id']}"):
                                if api_request(f"/fluxo/ordens/{ordem['id']}/finalizar", "POST"):
                                    st.success("Finalizado!")
                                    time.sleep(1)
                                    st.rerun()
                    st.markdown("---")
        else:
            st.info("📭 Nenhuma ordem na fila no momento")
    
    with tab2:
        st.subheader("⚙️ Controle Detalhado por Etapa")
        
        ordens_ativas = [o for o in ordens if o['status'] in ['SOLICITADO', 'EM_ANDAMENTO']]
        
        if ordens_ativas:
            for ordem in ordens_ativas:
                with st.expander(f"🔧 Ordem #{ordem['id']} - {ordem['veiculo']} ({ordem['status']})", expanded=True):
                    # Etapas do processo
                    etapas = [
                        {"nome": "📋 Recepção e Avaliação", "key": "recepcao"},
                        {"nome": "💦 Pré-Lavagem", "key": "pre_lavagem"},
                        {"nome": "🚿 Lavagem Externa", "key": "lavagem_ext"},
                        {"nome": "🧽 Lavagem Interna", "key": "lavagem_int"},
                        {"nome": "🌬️ Secagem", "key": "secagem"},
                        {"nome": "✨ Polimento/Enceramento", "key": "polimento"},
                        {"nome": "🎯 Inspeção Final", "key": "inspecao"},
                        {"nome": "✅ Pronto para Entrega", "key": "entrega"}
                    ]
                    
                    # Progresso baseado no status
                    progresso = 0
                    if ordem['status'] == 'SOLICITADO':
                        progresso = 1  # Apenas recepção
                    elif ordem['status'] == 'EM_ANDAMENTO':
                        progresso = 4  # Metade do processo
                    elif ordem['status'] == 'FINALIZADO':
                        progresso = 8  # Completo
                    
                    # Mostrar etapas
                    for i, etapa in enumerate(etapas):
                        col1, col2, col3 = st.columns([1, 3, 2])
                        with col1:
                            if i < progresso:
                                st.success("✅")
                            elif i == progresso:
                                st.warning("🔄")
                            else:
                                st.info("⏳")
                        with col2:
                            st.write(f"**{etapa['nome']}**")
                        with col3:
                            if i == progresso and ordem['status'] != 'FINALIZADO':
                                if st.button("Concluir Etapa", key=f"etapa_{ordem['id']}_{i}"):
                                    # Simular avanço (implementar endpoint real depois)
                                    st.success(f"Etapa '{etapa['nome']}' concluída!")
                                    time.sleep(1)
                                    st.rerun()
                    
                    # Barra de progresso
                    st.progress(progresso / len(etapas))
                    st.write(f"**Progresso: {progresso}/{len(etapas)} etapas**")
        else:
            st.info("🎉 Nenhuma ordem ativa para controle de etapas")

if __name__ == "__main__":
    main()