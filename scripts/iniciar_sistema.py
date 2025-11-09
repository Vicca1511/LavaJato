import subprocess
import sys
import time
import requests
import webbrowser
from pathlib import Path
import threading

class InicializadorSistema:
    def __init__(self):
        self.base_dir = Path(".")
        self.backend_dir = self.base_dir / "backend"
        self.frontend_dir = self.base_dir / "frontend"
        self.processos = []
    
    def iniciar_backend(self):
        """Inicia o backend FastAPI"""
        print("🔌 INICIANDO BACKEND...")
        
        try:
            # Verificar se já está rodando
            try:
                response = requests.get("http://localhost:8000/health", timeout=2)
                if response.status_code == 200:
                    print("✅ Backend já está rodando")
                    return True
            except:
                pass
            
            # Iniciar backend
            processo = subprocess.Popen([
                sys.executable, "-m", "uvicorn", 
                "app.main:app", "--reload", "--port", "8000"
            ], cwd=self.backend_dir)
            
            self.processos.append(processo)
            print("⏳ Aguardando backend iniciar...")
            
            # Aguardar inicialização
            for i in range(10):
                try:
                    response = requests.get("http://localhost:8000/health", timeout=2)
                    if response.status_code == 200:
                        print("✅ Backend iniciado com sucesso!")
                        return True
                except:
                    pass
                time.sleep(1)
            
            print("❌ Backend não respondeu após 10 segundos")
            return False
                
        except Exception as e:
            print(f"❌ Erro ao iniciar backend: {e}")
            return False
    
    def iniciar_streamlit_app(self, nome, porta):
        """Inicia um app Streamlit"""
        app_path = self.frontend_dir / nome / "app.py"
        
        if not app_path.exists():
            print(f"❌ App {nome} não encontrado: {app_path}")
            return False
        
        try:
            processo = subprocess.Popen([
                sys.executable, "-m", "streamlit", "run",
                str(app_path), "--server.port", str(porta),
                "--server.headless", "true", "--browser.gatherUsageStats", "false"
            ])
            
            self.processos.append(processo)
            print(f"✅ {nome} iniciando na porta {porta}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao iniciar {nome}: {e}")
            return False
    
    def verificar_frontends(self):
        """Verifica se os frontends estão respondendo"""
        print("\n🔍 VERIFICANDO FRONTENDS...")
        
        frontends = {
            "Admin": 8501,
            "Operações": 8502,
            "Cliente": 8503
        }
        
        time.sleep(3)  # Dar tempo para os apps iniciarem
        
        for nome, porta in frontends.items():
            try:
                response = requests.get(f"http://localhost:{porta}/", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {nome}: ONLINE (http://localhost:{porta})")
                else:
                    print(f"⚠️  {nome}: Resposta {response.status_code}")
            except requests.exceptions.ConnectionError:
                print(f"❌ {nome}: OFFLINE - Conexão recusada")
            except Exception as e:
                print(f"❌ {nome}: ERRO - {e}")
    
    def abrir_navegador(self):
        """Abre o navegador nas URLs principais"""
        print("\n🌐 ABRINDO NAVEGADOR...")
        
        urls = [
            "http://localhost:8000/docs",    # API Docs
            "http://localhost:8501",         # Admin
            "http://localhost:8502",         # Operações
            "http://localhost:8503"          # Cliente
        ]
        
        for url in urls:
            try:
                webbrowser.open(url)
                print(f"   📖 {url}")
            except Exception as e:
                print(f"   ❌ Erro ao abrir {url}: {e}")
    
    def parar_sistema(self):
        """Para todos os processos"""
        print("\n🛑 Parando sistema...")
        for processo in self.processos:
            try:
                processo.terminate()
            except:
                pass
    
    def executar(self):
        """Executa todo o sistema"""
        print("🚀 INICIANDO SISTEMA LAVA JATO")
        print("=" * 50)
        
        try:
            # Iniciar backend
            if not self.iniciar_backend():
                print("❌ Não foi possível iniciar o backend")
                return
            
            # Iniciar frontends
            print("\n🎨 INICIANDO FRONTENDS...")
            self.iniciar_streamlit_app("admin", 8501)
            self.iniciar_streamlit_app("operacoes", 8502)
            self.iniciar_streamlit_app("cliente", 8503)
            
            # Verificar status
            self.verificar_frontends()
            
            # Abrir navegador
            self.abrir_navegador()
            
            print("\n🎉 SISTEMA INICIADO!")
            print("=" * 50)
            print("🔌 API: http://localhost:8000/docs")
            print("🎨 Admin: http://localhost:8501") 
            print("🛠️ Operações: http://localhost:8502")
            print("👤 Cliente: http://localhost:8503")
            print("\n⏹️  Pressione Ctrl+C para parar o sistema")
            
            # Manter o script rodando
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Parando sistema...")
        finally:
            self.parar_sistema()

if __name__ == "__main__":
    inicializador = InicializadorSistema()
    inicializador.executar()