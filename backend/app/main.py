from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar rotas principais
from app.api.clientes import router as clientes_router
from app.api.veiculos import router as veiculos_router
from app.api.servicos import router as servicos_router
from app.api.ordens_servico import router as ordens_servico_router
# from app.api.fluxo_atendimento import router as fluxo_router
from app.api.whatsapp_routes import router as whatsapp_router

app = FastAPI(
    title="Sistema Lava Jato",
    description="API para gerenciamento de lava jato",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(clientes_router, prefix="/api/clientes", tags=["Clientes"])
app.include_router(veiculos_router, prefix="/api/veiculos", tags=["Veiculos"])
app.include_router(servicos_router, prefix="/api/servicos", tags=["Servicos"])
app.include_router(ordens_servico_router, prefix="/api/ordens-servico", tags=["Ordens de Servico"])
app.include_router(whatsapp_router, prefix="/api/whatsapp", tags=["WhatsApp"])
# app.include_router(fluxo_router, prefix="/api/fluxo", tags=["Fluxo Atendimento"])

@app.get("/")
async def root():
    return {"message": "Sistema Lava Jato API", "status": "online"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "lava-jato-api"}

@app.get("/api/health")
async def api_health_check():
    return {"status": "healthy", "api": "running", "database": "connected"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
from app.api.debug_routes import router as debug_router
app.include_router(debug_router, prefix="/api/debug", tags=["Debug"])
