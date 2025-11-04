with open('./backend/app/api/__init__.py', 'w') as f:
    f.write('''from .clientes import router as clientes_router
from .veiculos import router as veiculos_router
from .servicos import router as servicos_router
from .categorias import router as categorias_router
from .ordens_servico import router as ordens_servico_router
from .whatsapp_routes import router as whatsapp_router

__all__ = [
    "clientes_router", 
    "veiculos_router", 
    "servicos_router", 
    "categorias_router",
    "ordens_servico_router",
    "whatsapp_router"
]
''')
print("✅ api/__init__.py corrigido")
