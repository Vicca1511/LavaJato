from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importações
try:
    from app.api.whatsapp_routes import router as whatsapp_router
    has_whatsapp = True
except ImportError as e:
    has_whatsapp = False
    print(f"Aviso: Rotas WhatsApp não disponíveis: {e}")

try:
    from app.api import clientes, veiculos, servicos, categorias, agendamentos
    has_core_routes = True
except ImportError as e:
    has_core_routes = False
    print(f"Aviso: Rotas principais não disponíveis: {e}")

app = FastAPI(title="LavaJato System", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
if has_whatsapp:
    app.include_router(whatsapp_router, prefix="/api/whatsapp", tags=["whatsapp"])
    print("✅ Rotas WhatsApp carregadas")

if has_core_routes:
    app.include_router(clientes.router, prefix="/api", tags=["clientes"])
    app.include_router(veiculos.router, prefix="/api", tags=["veiculos"])
    app.include_router(servicos.router, prefix="/api", tags=["servicos"])
    app.include_router(categorias.router, prefix="/api", tags=["categorias"])
    app.include_router(agendamentos.router, prefix="/api", tags=["agendamentos"])
    print("✅ Rotas principais carregadas")

@app.get("/")
async def root():
    return {"message": "LavaJato System API", "status": "running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "whatsapp_available": has_whatsapp,
        "core_routes_available": has_core_routes
    }

# Rota para teste rápido
@app.get("/api/test")
async def test_route():
    return {"message": "API funcionando!"}
