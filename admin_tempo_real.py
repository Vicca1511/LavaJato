import streamlit as st
import requests
import pandas as pd
import json
import time
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# Configuração da página
st.set_page_config(
    page_title="Painel Admin - Tempo Real",
    page_icon="🚗",
    layout="wide"
)

# CSS para melhorar visualização
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-card {
        padding: 1rem;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin: 0.5rem 0;
    }
    .progress-bar {
        height: 20px;
        background-color: #e0e0e0;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .progress-fill {
        height: 100%;
        border-radius: 10px;
        background-color: #1f77b4;
        transition: width 0.5s ease-in-out;
    }
</style>
""", unsafe_allow_html=True)

class PainelAdminTempoReal:
    def __init__(self):
        self.api_base = "http://localhost:8000/api"
        self.ordens_data = []
        self.estatisticas = {}
        
    def fazer_requisicao(self, endpoint, metodo="GET", dados=None):
        try:
            url = f"{self.api_base}{endpoint}"
            if metodo == "GET":
                response = requests.get(url)
            elif metodo == "POST":
                response = requests.post(url, json=dados)
            elif metodo == "PUT":
                response = requests.put(url, json=dados)
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Erro na requisição: {response.status_code}")
                return None
        except Exception as e:
            st.error(f"Erro de conexão: {e}")
            return None
    
    def carregar_dados_iniciais(self):
        """Carrega dados iniciais do sistema"""
        self.ordens_data = self.fazer_requisicao("/ordens-servico") or []
        self.carregar_estatisticas()
    
    def carregar_estatisticas(self):
        """Carrega estatísticas do sistema"""
        # Simulação - na implementação real viria da API
        self.estatisticas = {
            'total_ordens': len(self.ordens_data),
            'ordens_andamento': len([o for o in self.ordens_data if o.get('status') == 'EM_ANDAMENTO']),
            'ordens_hoje': len([o for o in self.ordens_data if o.get('data_entrada') and o.get('data_entrada').startswith(datetime.now().strftime('%Y-%m-%d'))]),
            'faturamento_hoje': sum([o.get('valor_total', 0) for o in self.ordens_data if o.get('status') == 'FINALIZADO' and o.get('data_entrada') and o.get('data_entrada').startswith(datetime.now().strftime('%Y-%m-%d'))])
        }
    
    def mostrar_header(self):
        """Mostra o cabeçalho do painel"""
        st.markdown('<h1 class="main-header">🚗 Painel Admin - Lava Jato</h1>', unsafe_allow_html=True)
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Ordens", self.estatisticas.get('total_ordens', 0))
        
        with col2:
            st.metric("Em Andamento", self.estatisticas.get('ordens_andamento', 0))
        
        with col3:
            st.metric("Ordens Hoje", self.estatisticas.get('ordens_hoje', 0))
        
        with col4:
            st.metric("Faturamento Hoje", f"R$ {self.estatisticas.get('faturamento_hoje', 0):.2f}")
    
    def mostrar_ordens_tempo_real(self):
        """Mostra as ordens em tempo real"""
        st.subheader("📊 Ordens de Serviço - Tempo Real")
        
        if not self.ordens_data:
            st.info("Nenhuma ordem de serviço encontrada.")
            return
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        with col1:
            filtro_status = st.selectbox("Filtrar por Status", ["Todos", "SOLICITADO", "EM_ANDAMENTO", "FINALIZADO", "CANCELADO"])
        with col2:
            filtro_data = st.date_input("Filtrar por Data")
        with col3:
            st.write("")  # Espaçamento
            if st.button("🔄 Atualizar Dados"):
                self.carregar_dados_iniciais()
                st.rerun()
        
        # Aplicar filtros
        ordens_filtradas = self.ordens_data
        if filtro_status != "Todos":
            ordens_filtradas = [o for o in ordens_filtradas if o.get('status') == filtro_status]
        
        # Mostrar ordens
        for ordem in ordens_filtradas:
            self.mostrar_card_ordem(ordem)
    
    def mostrar_card_ordem(self, ordem):
        """Mostra um card individual de ordem"""
        status_config = {
            'SOLICITADO': {'cor': '#FFA500', 'icone': '⏳'},
            'EM_ANDAMENTO': {'cor': '#1f77b4', 'icone': '🚗'},
            'FINALIZADO': {'cor': '#2E8B57', 'icone': '✅'},
            'CANCELADO': {'cor': '#FF4500', 'icone': '❌'}
        }
        
        config = status_config.get(ordem.get('status', 'SOLICITADO'), status_config['SOLICITADO'])
        
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                st.write(f"**{ordem.get('veiculo', 'N/A')}** - {ordem.get('placa', 'N/A')}")
                st.write(f"Cliente ID: {ordem.get('cliente_id', 'N/A')}")
                if ordem.get('observacoes'):
                    st.write(f"Obs: {ordem.get('observacoes')}")
            
            with col2:
                st.write(f"**Status:** {config['icone']} {ordem.get('status', 'N/A')}")
                st.write(f"**Valor:** R$ {ordem.get('valor_total', 0):.2f}")
            
            with col3:
                # Barra de progresso
                progresso = self.calcular_progresso(ordem.get('status'))
                st.write(f"Progresso: {progresso}%")
                st.progress(progresso / 100)
            
            with col4:
                # Ações
                if ordem.get('status') == 'SOLICITADO':
                    if st.button("▶️ Iniciar", key=f"iniciar_{ordem['id']}"):
                        self.atualizar_status(ordem['id'], 'EM_ANDAMENTO')
                elif ordem.get('status') == 'EM_ANDAMENTO':
                    if st.button("✅ Finalizar", key=f"finalizar_{ordem['id']}"):
                        self.atualizar_status(ordem['id'], 'FINALIZADO')
                
                if st.button("📱 WhatsApp", key=f"whatsapp_{ordem['id']}"):
                    self.enviar_notificacao_whatsapp(ordem['id'])
            
            st.markdown("---")
    
    def calcular_progresso(self, status):
        """Calcula o progresso baseado no status"""
        progresso_map = {
            'SOLICITADO': 25,
            'EM_ANDAMENTO': 60,
            'FINALIZADO': 100,
            'CANCELADO': 0
        }
        return progresso_map.get(status, 0)
    
    def atualizar_status(self, ordem_id, novo_status):
        """Atualiza o status de uma ordem"""
        dados = {'status': novo_status}
        resultado = self.fazer_requisicao(f"/ordens-servico/{ordem_id}", "PUT", dados)
        if resultado:
            st.success(f"Ordem {ordem_id} atualizada para {novo_status}")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Erro ao atualizar ordem")
    
    def enviar_notificacao_whatsapp(self, ordem_id):
        """Envia notificação via WhatsApp"""
        resultado = self.fazer_requisicao(f"/whatsapp/ordem/{ordem_id}/notificar", "POST")
        if resultado:
            st.success("Notificação WhatsApp enviada!")
        else:
            st.error("Erro ao enviar notificação WhatsApp")
    
    def mostrar_graficos(self):
        """Mostra gráficos e visualizações"""
        st.subheader("📈 Métricas e Gráficos")
        
        if not self.ordens_data:
            return
        
        # Preparar dados para gráficos
        df = pd.DataFrame(self.ordens_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de status
            if 'status' in df.columns:
                status_count = df['status'].value_counts()
                fig_status = px.pie(
                    values=status_count.values,
                    names=status_count.index,
                    title="Distribuição por Status"
                )
                st.plotly_chart(fig_status, use_container_width=True)
        
        with col2:
            # Gráfico de faturamento por status
            if 'status' in df.columns and 'valor_total' in df.columns:
                faturamento_status = df.groupby('status')['valor_total'].sum()
                fig_faturamento = px.bar(
                    x=faturamento_status.index,
                    y=faturamento_status.values,
                    title="Faturamento por Status",
                    labels={'x': 'Status', 'y': 'Faturamento (R$)'}
                )
                st.plotly_chart(fig_faturamento, use_container_width=True)
    
    def mostrar_logs_auditoria(self):
        """Mostra logs de auditoria LGPD"""
        st.subheader("🔒 Logs de Auditoria LGPD")
        
        # Simulação de logs de auditoria
        logs = [
            {"timestamp": "2024-01-15 10:30:00", "acao": "CONSULTA", "tipo_dado": "telefone", "usuario": "admin"},
            {"timestamp": "2024-01-15 11:15:00", "acao": "ATUALIZACAO", "tipo_dado": "email", "usuario": "operador"},
            {"timestamp": "2024-01-15 14:20:00", "acao": "CRIPTOGRAFIA", "tipo_dado": "cpf", "usuario": "sistema"},
        ]
        
        for log in logs:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                with col1:
                    st.write(f"**{log['timestamp']}**")
                with col2:
                    st.write(f"`{log['acao']}`")
                with col3:
                    st.write(log['tipo_dado'])
                with col4:
                    st.write(log['usuario'])
                st.markdown("---")

def main():
    # Verificação de segurança
    if 'autenticado' not in st.session_state:
        st.session_state.autenticado = False
    
    if not st.session_state.autenticado:
        st.title("🔒 Acesso Administrativo")
        senha = st.text_input("Senha Administrativa", type="password")
        
        if st.button("Acessar"):
            # Em produção, usar hash seguro
            if senha == "admin123":  # Senha padrão - alterar em produção
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Senha incorreta!")
        return
    
    # Painel principal
    painel = PainelAdminTempoReal()
    painel.carregar_dados_iniciais()
    
    # Sidebar
    with st.sidebar:
        st.title("Menu Admin")
        st.markdown("---")
        
        if st.button("🚪 Sair"):
            st.session_state.autenticado = False
            st.rerun()
        
        st.markdown("### Navegação")
        pagina = st.radio(
            "Selecione a página:",
            ["📊 Dashboard Tempo Real", "📈 Métricas", "🔒 Auditoria LGPD"]
        )
    
    # Conteúdo baseado na seleção
    if pagina == "📊 Dashboard Tempo Real":
        painel.mostrar_header()
        painel.mostrar_ordens_tempo_real()
    
    elif pagina == "📈 Métricas":
        painel.mostrar_header()
        painel.mostrar_graficos()
    
    elif pagina == "🔒 Auditoria LGPD":
        st.title("🔒 Auditoria LGPD/RGPD")
        painel.mostrar_logs_auditoria()

if __name__ == "__main__":
    main()