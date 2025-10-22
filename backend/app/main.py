from fastapi import FastAPI
from .database import engine
from .models import clientes
from .api import clientes as clientes_router

# Criar tabelas no banco de dados
clientes.Base.metadata.create_all(bind=engine)

# Criar aplicação FastAPI
app = FastAPI(
    title="LavaJato System API",
    description="Sistema de gerenciamento para lava-jato",
    version="1.0.0"
)

# Incluir routers
app.include_router(clientes_router.router)

@app.get("/")
def root():
    return {"message": "LavaJato System API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
