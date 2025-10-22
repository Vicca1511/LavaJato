import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_criar_cliente():
 response =client.post("/clientes/", json={
        "nome": "João Silva",
        "cpf": "12345678900",
        "telefone": "(11) 99999-9999"
    })
 assert response.status_code == 201
 assert response.json()["nome"] == "João Silva" 
    