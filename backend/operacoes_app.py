import streamlit as st
import requests
import json

st.set_page_config(page_title="Operações - LavaJato", page_icon="���", layout="wide")

st.title("��� Área de Operações - LavaJato")
st.markdown("Controle da fila de serviços e geração de PIX")

# Configuração da API
API_URL = "http://localhost:8000"

st.warning("⚠️ App de Operações em desenvolvimento")
st.info("��� Esta funcionalidade será implementada após os testes iniciais")

st.subheader("Próximas Implementações:")
st.write("✅ Controle de fila de serviços")
st.write("✅ Geração de QR Code PIX") 
st.write("✅ Confirmação de pagamentos")
st.write("✅ Integração com WhatsApp")

st.success("��� Execute os testes no Admin App e Cliente App primeiro!")
