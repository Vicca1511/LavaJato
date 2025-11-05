from .clientes import Cliente
from .veiculos import Veiculo
from .categorias import Categoria
from .servicos import Servico
from .porte_preco import PortePreco
from .ordens_servico import OrdemServico

# Importar Base do database
from app.database import Base

__all__ = ["Base", "Cliente", "Veiculo", "Categoria", "Servico", "PortePreco", "OrdemServico"]
