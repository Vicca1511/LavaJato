from fastapi import FastAPI
from .database import engine
from .models import clientes, veiculos, servicos, porte_preco, categorias, agendamentos
from .api import clientes as clientes_router
from .api import veiculos as veiculos_router
from .api import servicos as servicos_router
from .api import categorias as categorias_router
from .api import agendamentos as agendamentos_router

# Criar tabelas no banco de dados
clientes.Base.metadata.create_all(bind=engine)
veiculos.Base.metadata.create_all(bind=engine)
servicos.Base.metadata.create_all(bind=engine)
porte_preco.Base.metadata.create_all(bind=engine)
categorias.Base.metadata.create_all(bind=engine)
agendamentos.Base.metadata.create_all(bind=engine)
# Criar aplicação FastAPI
app = FastAPI(
    title="LavaJato System",
    description="Sistema de gerenciamento para lava-jato",
    version="1.0.0"
)
# Incluir routers
app.include_router(clientes_router.router, prefix="/api/clientes", tags=["clientes"])
app.include_router(veiculos_router.router, prefix="/api/veiculos", tags=["veiculos"])
app.include_router(servicos_router.router, prefix="/api/servicos", tags=["servicos"])
app.include_router(categorias_router.router, prefix="/api/categorias", tags=["categorias"])
app.include_router(agendamentos_router.router, prefix="/api/agendamentos", tags=["agendamentos"])
@app.get("/")
def root():
    return {"message": "LavaJato System API", "status": "running"}
@app.get("/health")
def health_check():
    return {"status": "healthy"}
# WhatsApp Routes
from app.api import whatsapp
app.include_router(whatsapp.router, prefix="/api/whatsapp", tags=["whatsapp"])
