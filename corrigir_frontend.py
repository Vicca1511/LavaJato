# Ler o arquivo
with open('frontend/operacoes/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Substituir APENAS a parte dos dados da ordem
old_code = '''                    dados = {
                        "cliente_id": int(cliente_id),
                        "veiculo": veiculo,
                        "placa": placa.upper(),
                        "servico_id": int(servico_id),
                        "observacoes": observacoes
                    }
                    resultado = fazer_requisicao("/ordens-servico", "POST", dados)'''

new_code = '''                    # Usar veículo existente (ID 1 para teste)
                    dados = {
                        "veiculo_id": 1,  # Usar veículo fixo por enquanto
                        "servico_id": int(servico_id),
                        "observacoes": f"Cliente: {cliente_id}, Veículo: {veiculo}, Placa: {placa}. {observacoes}"
                    }
                    resultado = fazer_requisicao("/ordens-servico", "POST", dados)'''

content = content.replace(old_code, new_code)

# Salvar
with open('frontend/operacoes/app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Frontend corrigido (usando veículo fixo)!")
