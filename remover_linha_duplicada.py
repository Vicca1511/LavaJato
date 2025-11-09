# Ler o arquivo
with open('backend/app/api/ordens_servico.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Encontrar e remover a linha duplicada do posicao_fila
new_lines = []
for line in lines:
    if 'posicao_fila=' in line and 'ultima_posicao' in line:
        print(f"Removendo linha duplicada: {line.strip()}")
        continue  # Pular esta linha
    new_lines.append(line)

# Salvar o arquivo corrigido
with open('backend/app/api/ordens_servico.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ Linha duplicada removida!")
