# Ler o arquivo
with open('backend/app/api/ordens_servico.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remover a linha problemática do posicao_fila
content = content.replace("posicao_fila=ultima_posicao + 1,", "")

# Remover a linha que calcula ultima_posicao  
content = content.replace("ultima_posicao = db.query(func.max(OrdemServico.posicao_fila)).scalar() or 0", "")

# Corrigir os campos para usar o modelo correto
content = content.replace("veiculo_id=ordem.veiculo_id,", "cliente_id=1,  # Cliente padrão")
content = content.replace("servico_id=ordem.servico_id,", "veiculo=veiculo.modelo,\n        placa=veiculo.placa,\n        servico_id=ordem.servico_id,")
content = content.replace("status='aguardando',", "status='SOLICITADO',")
content = content.replace("valor_cobrado=servico.valor_base,", "valor_total=servico.valor_base,")

# Salvar
with open('backend/app/api/ordens_servico.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Campos corrigidos para usar modelo existente!")
