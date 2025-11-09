# Corrigir tags no main.py para padronizar
with open('backend/app/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Substituir tags com acentos por tags sem acentos
correcoes = {
    'tags=["Clientes"]': 'tags=["Clientes"]',
    'tags=["Veículos"]': 'tags=["Veiculos"]', 
    'tags=["Serviços"]': 'tags=["Servicos"]',
    'tags=["Ordens"]': 'tags=["Ordens de Servico"]',
    'tags=["WhatsApp"]': 'tags=["WhatsApp"]',
    'tags=["Fluxo Atendimento"]': 'tags=["Fluxo Atendimento"]'
}

for old, new in correcoes.items():
    content = content.replace(old, new)

with open('backend/app/main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Tags no main.py padronizadas!")
