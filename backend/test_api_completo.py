#!/usr/bin/env python3
"""
Testa TODOS os endpoints da API
"""
import requests
import time

BASE_URL = "http://localhost:8000/api"

endpoints = [
    "/health",
    "/ordens-servico",
    "/clientes", 
    "/veiculos",
    "/servicos",
    "/categorias",
    "/fluxo-atendimento",
    "/whatsapp/status"
]

def test_all_endpoints():
    print("🧪 TESTE COMPLETO DA API")
    print("=" * 60)
    
    for endpoint in endpoints:
        url = BASE_URL + endpoint
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"✅ {endpoint:25} {len(data):2} itens  ({response_time:.0f}ms)")
                else:
                    print(f"✅ {endpoint:25} OK        ({response_time:.0f}ms)")
            else:
                print(f"❌ {endpoint:25} ERRO {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {endpoint:25} API OFFLINE")
        except Exception as e:
            print(f"❌ {endpoint:25} Erro: {str(e)[:30]}...")

def test_frontend_connectivity():
    print("\n🌐 TESTE DE CONECTIVIDADE DO FRONTEND")
    print("=" * 60)
    
    frontend_urls = [
        ("Admin", "http://localhost:8501"),
        ("Operações", "http://localhost:8502"), 
        ("Cliente", "http://localhost:8503"),
        ("API Docs", "http://localhost:8000/docs")
    ]
    
    for name, url in frontend_urls:
        try:
            response = requests.get(url, timeout=5)
            status = "✅ ONLINE" if response.status_code == 200 else f"❌ {response.status_code}"
            print(f"{name:12} {url:25} {status}")
        except:
            print(f"{name:12} {url:25} ❌ OFFLINE")

if __name__ == "__main__":
    # Primeiro inicie o sistema com o script
    print("🚀 Inicie o sistema primeiro com: python scripts/iniciar_sistema.py")
    print("   Depois execute este teste em outro terminal\n")
    
    input("Pressione Enter quando o sistema estiver rodando...")
    
    test_all_endpoints()
    test_frontend_connectivity()