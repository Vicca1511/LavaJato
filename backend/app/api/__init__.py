from .clientes import router as clientes_router
from .veiculos import router as veiculos_router
from .servicos import router as servicos_router

__all__ = ["clientes_router", "veiculos_router", "servicos_router"]
