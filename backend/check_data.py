#!/usr/bin/env python3
"""
Verifica os dados reais no banco via API
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def check_all_data():
    print("📊 DADOS ATUAIS NO SISTEMA")
    print("=" * 50)
    
    endpoints = {
        "Ordens de Serviço": "/ordens-servico",
        "Clientes": "/clientes",
        "Veículos": "/veiculos", 
        "Serviços": "/servicos",
        "Categorias": "/categorias"
    }
    
    for name, endpoint in endpoints.items():
        try:
            response = requests.get(BASE_URL + endpoint, timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"\n{name}:")
                print(f"  📈 Total: {len(data)}")
                if data:
                    for i, item in enumerate(data[:3]):  # Mostra apenas 3 primeiros
                        if name == "Ordens de Serviço":
                            print(f"    {i+1}. #{item.get('id')} - {item.get('veiculo')} ({item.get('status')})")
                        elif name == "Clientes":
                            print(f"    {i+1}. {item.get('nome')} - {item.get('telefone')}")
                        elif name == "Serviços":
                            print(f"    {i+1}. {item.get('nome')} - R$ {item.get('preco')}")
                        else:
                            print(f"    {i+1}. {item}")
                    if len(data) > 3:
                        print(f"    ... e mais {len(data) - 3}")
                else:
                    print("    📭 Nenhum dado")
            else:
                print(f"{name}: ❌ Erro {response.status_code}")
        except Exception as e:
            print(f"{name}: ❌ {e}")

if __name__ == "__main__":
    check_all_data()