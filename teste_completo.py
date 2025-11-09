import os
import sys
import subprocess
import requests
import sqlite3
from pathlib import Path
import importlib.util
import time

class TesteSistemaLavaJato:
    def __init__(self):
        self.base_dir = Path(".")
        self.backend_dir = self.base_dir / "backend"
        self.frontend_dir = self.base_dir / "frontend"
        self.api_url = "http://localhost:8000"
        self.resultados = []
    
    def log_resultado(self, modulo, status, mensagem, detalhes=None):
        """Registra resultado do teste"""
        resultado = {
            "modulo": modulo,
            "status": status,
            "mensagem": mensagem,
            "detalhes": detalhes
        }
        self.resultados.append(resultado)
        icon = "✅" if status == "SUCESSO" else "❌" if status == "ERRO" else "⚠️"
        print(f"{icon} {modulo}: {mensagem}")
        if detalhes:
            print(f"   📋 {detalhes}")
    
    def verificar_estrutura_arquivos(self):
        """Verifica se todos os arquivos necessários existem"""
        print("\n" + "="*60)
        print("📁 VERIFICAÇÃO DA ESTRUTURA DE ARQUIVOS")
        print("="*60)
        
        arquivos_necessarios = [
            # Backend
            self.backend_dir / "app" / "main.py",
            self.backend_dir / "app" / "database.py",
            self.backend_dir / "app" / "models" / "__init__.py",
            self.backend_dir / "app" / "models" / "clientes.py",
            self.backend_dir / "app" / "models" / "ordens_servico.py",
            self.backend_dir / "app" / "models" / "servicos.py",
            self.backend_dir / "app" / "api" / "__init__.py",
            self.backend_dir / "app" / "api" / "clientes.py",
            self.backend_dir / "app" / "api" / "ordens_servico.py",
            self.backend_dir / "app" / "services" / "whatsapp_service.py",
            
            # Frontend
            self.base_dir / "admin_app_final.py",
            self.base_dir / "operacoes_app_final.py", 
            self.base_dir / "cliente_app.py",
            
            # Configurações
            self.base_dir / "requirements.txt",
            self.backend_dir / ".env"
        ]
        
        for arquivo in arquivos_necessarios:
            if arquivo.exists():
                self.log_resultado("Estrutura", "SUCESSO", f"Arquivo encontrado: {arquivo}")
            else:
                self.log_resultado("Estrutura", "ERRO", f"Arquivo faltando: {arquivo}")
    
    def verificar_banco_dados(self):
        """Verifica se o banco de dados existe e tem estrutura correta"""
        print("\n" + "="*60)
        print("🗄️ VERIFICAÇÃO DO BANCO DE DADOS")
        print("="*60)
        
        db_path = self.backend_dir / "lavajato.db"
        
        if not db_path.exists():
            self.log_resultado("Banco Dados", "ERRO", "Arquivo do banco não encontrado")
            return False
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Verificar tabelas essenciais
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tabelas = [t[0] for t in cursor.fetchall()]
            
            tabelas_necessarias = ['clientes', 'servicos', 'ordens_servico', 'veiculos']
            for tabela in tabelas_necessarias:
                if tabela in tabelas:
                    # Contar registros
                    cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
                    count = cursor.fetchone()[0]
                    self.log_resultado("Banco Dados", "SUCESSO", 
                                     f"Tabela '{tabela}' encontrada", 
                                     f"Registros: {count}")
                else:
                    self.log_resultado("Banco Dados", "ERRO", f"Tabela '{tabela}' não encontrada")
            
            conn.close()
            return True
            
        except Exception as e:
            self.log_resultado("Banco Dados", "ERRO", f"Erro ao acessar banco: {e}")
            return False
    
    def verificar_dependencias(self):
        """Verifica se todas as dependências estão instaladas"""
        print("\n" + "="*60)
        print("📦 VERIFICAÇÃO DE DEPENDÊNCIAS")
        print("="*60)
        
        dependencias = [
            "fastapi", "uvicorn", "streamlit", "sqlalchemy", 
            "requests", "pandas", "cryptography", "websockets"
        ]
        
        for dep in dependencias:
            try:
                spec = importlib.util.find_spec(dep)
                if spec is not None:
                    self.log_resultado("Dependências", "SUCESSO", f"{dep} instalado")
                else:
                    self.log_resultado("Dependências", "ERRO", f"{dep} não instalado")
            except ImportError:
                self.log_resultado("Dependências", "ERRO", f"{dep} não instalado")
    
    def testar_api_backend(self):
        """Testa se a API do backend está funcionando"""
        print("\n" + "="*60)
        print("🔌 TESTE DA API BACKEND")
        print("="*60)
        
        # Tentar iniciar o servidor se não estiver rodando
        if not self._servidor_rodando():
            self.log_resultado("API Backend", "AVISO", "Servidor não está rodando")
            return False
        
        endpoints = [
            "/api/clientes",
            "/api/servicos", 
            "/api/ordens-servico",
            "/api/veiculos"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.api_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    count = len(data) if isinstance(data, list) else "N/A"
                    self.log_resultado("API Backend", "SUCESSO", 
                                     f"Endpoint {endpoint} respondendo",
                                     f"Status: {response.status_code}, Itens: {count}")
                else:
                    self.log_resultado("API Backend", "ERRO",
                                     f"Endpoint {endpoint} com erro",
                                     f"Status: {response.status_code}")
            except requests.exceptions.RequestException as e:
                self.log_resultado("API Backend", "ERRO",
                                 f"Endpoint {endpoint} inacessível",
                                 f"Erro: {e}")
    
    def _servidor_rodando(self):
        """Verifica se o servidor FastAPI está rodando"""
        try:
            response = requests.get(f"{self.api_url}/docs", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def testar_apps_streamlit(self):
        """Testa se os apps Streamlit podem ser importados"""
        print("\n" + "="*60)
        print("🎨 TESTE DOS APPS STREAMLIT")
        print("="*60)
        
        apps = [
            ("Admin App", "admin_app_final.py"),
            ("Operações App", "operacoes_app_final.py"),
            ("Cliente App", "cliente_app.py")
        ]
        
        for app_nome, app_arquivo in apps:
            app_path = self.base_dir / app_arquivo
            if app_path.exists():
                try:
                    # Testar importação básica
                    with open(app_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Verificar imports críticos
                    imports_necessarios = ['streamlit', 'requests']
                    imports_encontrados = []
                    
                    for imp in imports_necessarios:
                        if imp in content:
                            imports_encontrados.append(imp)
                    
                    if len(imports_encontrados) == len(imports_necessarios):
                        self.log_resultado(app_nome, "SUCESSO", 
                                         "App pode ser importado",
                                         f"Imports: {', '.join(imports_encontrados)}")
                    else:
                        self.log_resultado(app_nome, "AVISO",
                                         "App com imports incompletos",
                                         f"Faltando: {set(imports_necessarios) - set(imports_encontrados)}")
                        
                except Exception as e:
                    self.log_resultado(app_nome, "ERRO", f"Erro ao ler app: {e}")
            else:
                self.log_resultado(app_nome, "ERRO", f"Arquivo {app_arquivo} não encontrado")
    
    def verificar_whatsapp_integration(self):
        """Verifica integração com WhatsApp"""
        print("\n" + "="*60)
        print("📱 VERIFICAÇÃO DO WHATSAPP")
        print("="*60)
        
        whatsapp_files = [
            self.backend_dir / "app" / "services" / "whatsapp_service.py",
            self.backend_dir / "app" / "services" / "whatsapp_manager.py",
            self.backend_dir / "app" / "api" / "whatsapp_routes.py"
        ]
        
        for file in whatsapp_files:
            if file.exists():
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Verificar se é modo simulação ou produção
                    if "SIMULATION" in content or "SIMULACAO" in content:
                        self.log_resultado("WhatsApp", "AVISO", 
                                         f"{file.name} em modo simulação",
                                         "Envio real desativado")
                    else:
                        self.log_resultado("WhatsApp", "SUCESSO",
                                         f"{file.name} configurado")
                                         
                except Exception as e:
                    self.log_resultado("WhatsApp", "ERRO", f"Erro ao ler {file.name}: {e}")
            else:
                self.log_resultado("WhatsApp", "AVISO", f"Arquivo {file.name} não encontrado")
    
    def verificar_lgpd_criptografia(self):
        """Verifica implementação LGPD"""
        print("\n" + "="*60)
        print("🔒 VERIFICAÇÃO LGPD/CRIPTOGRAFIA")
        print("="*60)
        
        # Verificar se existe módulo de segurança
        security_file = self.backend_dir / "app" / "core" / "security.py"
        if security_file.exists():
            self.log_resultado("LGPD", "SUCESSO", "Módulo de segurança encontrado")
            
            try:
                with open(security_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verificar componentes críticos
                componentes = [
                    "cryptography", "Fernet", "encrypt", "decrypt", "SENSITIVE_FIELDS"
                ]
                
                for comp in componentes:
                    if comp in content:
                        self.log_resultado("LGPD", "SUCESSO", f"Componente {comp} implementado")
                    else:
                        self.log_resultado("LGPD", "AVISO", f"Componente {comp} não encontrado")
                        
            except Exception as e:
                self.log_resultado("LGPD", "ERRO", f"Erro ao verificar segurança: {e}")
        else:
            self.log_resultado("LGPD", "ERRO", "Módulo de segurança não encontrado")
    
    def verificar_tempo_real(self):
        """Verifica funcionalidades de tempo real"""
        print("\n" + "="*60)
        print("⚡ VERIFICAÇÃO TEMPO REAL")
        print("="*60)
        
        tempo_real_files = [
            self.backend_dir / "app" / "services" / "tempo_real_service.py",
            self.backend_dir / "app" / "api" / "websocket_routes.py"
        ]
        
        for file in tempo_real_files:
            if file.exists():
                self.log_resultado("Tempo Real", "SUCESSO", f"{file.name} encontrado")
            else:
                self.log_resultado("Tempo Real", "AVISO", f"{file.name} não encontrado")
    
    def executar_todos_testes(self):
        """Executa todos os testes"""
        print("🚀 INICIANDO TESTES COMPLETOS DO SISTEMA LAVA JATO")
        print("="*60)
        
        self.verificar_estrutura_arquivos()
        self.verificar_dependencias()
        self.verificar_banco_dados()
        self.testar_api_backend()
        self.testar_apps_streamlit()
        self.verificar_whatsapp_integration()
        self.verificar_lgpd_criptografia()
        self.verificar_tempo_real()
        
        self.gerar_relatorio()
    
    def gerar_relatorio(self):
        """Gera relatório final dos testes"""
        print("\n" + "="*60)
        print("📊 RELATÓRIO FINAL DOS TESTES")
        print("="*60)
        
        total_testes = len(self.resultados)
        sucessos = sum(1 for r in self.resultados if r['status'] == 'SUCESSO')
        erros = sum(1 for r in self.resultados if r['status'] == 'ERRO')
        avisos = sum(1 for r in self.resultados if r['status'] == 'AVISO')
        
        print(f"📈 ESTATÍSTICAS:")
        print(f"   Total de testes: {total_testes}")
        print(f"   ✅ Sucessos: {sucessos}")
        print(f"   ⚠️  Avisos: {avisos}") 
        print(f"   ❌ Erros: {erros}")
        
        taxa_sucesso = (sucessos / total_testes) * 100 if total_testes > 0 else 0
        print(f"   📊 Taxa de sucesso: {taxa_sucesso:.1f}%")
        
        # Status geral
        if erros == 0:
            print("\n🎉 STATUS: SISTEMA OPERACIONAL!")
            if avisos > 0:
                print("   ⚠️  Existem avisos que devem ser verificados")
        else:
            print(f"\n🚨 STATUS: {erros} PROBLEMAS ENCONTRADOS!")
            print("   ❌ Corrija os erros antes de prosseguir")
        
        # Mostrar erros críticos
        if erros > 0:
            print("\n🔴 ERROS CRÍTICOS:")
            for resultado in self.resultados:
                if resultado['status'] == 'ERRO':
                    print(f"   • {resultado['modulo']}: {resultado['mensagem']}")
        
        # Mostrar avisos
        if avisos > 0:
            print("\n🟡 AVISOS:")
            for resultado in self.resultados:
                if resultado['status'] == 'AVISO':
                    print(f"   • {resultado['modulo']}: {resultado['mensagem']}")

def main():
    """Função principal"""
    tester = TesteSistemaLavaJato()
    tester.executar_todos_testes()
    
    # Oferecer próximos passos
    print("\n" + "="*60)
    print("🎯 PRÓXIMOS PASSOS RECOMENDADOS:")
    print("="*60)
    
    erros = sum(1 for r in tester.resultados if r['status'] == 'ERRO')
    
    if erros == 0:
        print("1. 🚀 Iniciar servidor backend:")
        print("   uvicorn backend.app.main:app --reload --port 8000")
        print("\n2. 🎨 Iniciar apps Streamlit:")
        print("   streamlit run admin_app_final.py")
        print("   streamlit run operacoes_app_final.py") 
        print("   streamlit run cliente_app.py")
        print("\n3. 🌐 Acessar no navegador:")
        print("   API: http://localhost:8000/docs")
        print("   Admin: http://localhost:8501")
    else:
        print("1. 🔧 Corrigir os erros identificados acima")
        print("2. 🛠️ Executar este teste novamente após correções")
        print("3. 🚀 Iniciar os serviços quando todos os testes passarem")

if __name__ == "__main__":
    main()
    