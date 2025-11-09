import re

# Correções para cada arquivo
correcoes = {
    'backend/app/api/veiculos.py': {
        'old': 'router = APIRouter(tags=["veiculos"])',
        'new': 'router = APIRouter(tags=["Veículos"])'
    },
    'backend/app/api/servicos.py': {
        'old': 'router = APIRouter(tags=["servicos"])', 
        'new': 'router = APIRouter(tags=["Serviços"])'
    },
    'backend/app/api/clientes.py': {
        'old': 'router = APIRouter()',
        'new': 'router = APIRouter(tags=["Clientes"])'
    },
    'backend/app/api/ordens_servico.py': {
        'old': 'router = APIRouter()',
        'new': 'router = APIRouter(tags=["Ordens de Serviço"])'
    },
    'backend/app/api/whatsapp_routes.py': {
        'old': 'router = APIRouter()',
        'new': 'router = APIRouter(tags=["WhatsApp"])'
    },
    'backend/app/api/fluxo_atendimento.py': {
        'old': 'router = APIRouter()',
        'new': 'router = APIRouter(tags=["Fluxo Atendimento"])'
    }
}

for arquivo, correcao in correcoes.items():
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if correcao['old'] in content:
            new_content = content.replace(correcao['old'], correcao['new'])
            with open(arquivo, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ {arquivo}: Tags corrigidas")
        else:
            print(f"⚠️  {arquivo}: Padrão não encontrado, verificar manualmente")
    except Exception as e:
        print(f"❌ {arquivo}: Erro - {e}")

print("\\n��� Correção de tags concluída!")
