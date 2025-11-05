import requests
base_url = 'http://localhost:8000/api/clientes'

# Primeiro criar um cliente para testar update
novo_cliente = {
    'nome': 'Cliente Para Update',
    'cpf': '98765432100',
    'telefone': '11988888888', 
    'email': 'update@teste.com'
}
response = requests.post(f'{base_url}/', json=novo_cliente)
if response.status_code == 201:
    cliente_id = response.json()['id']
    print(f'Cliente criado ID: {cliente_id}')
    
    # Tentar atualizar (mesmo sem endpoint PUT ainda)
    dados_update = {
        'nome': 'Cliente Atualizado',
        'cpf': '98765432100',
        'telefone': '11977777777',
        'email': 'atualizado@teste.com'
    }
    response = requests.put(f'{base_url}/{cliente_id}', json=dados_update)
    print(f'Tentativa PUT: {response.status_code}')
    if response.status_code != 200:
        print('PUT não implementado ainda (esperado)')
else:
    print('Erro ao criar cliente:', response.json())
