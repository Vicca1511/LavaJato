from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importacoes
try:
    from app.api.whatsapp_routes import router as whatsapp_router
    has_whatsapp = True
except ImportError as e:
    has_whatsapp = False
    print(f"Aviso: Rotas WhatsApp nao disponiveis: {e}")

# Criar app FastAPI
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
    print("CHECK Rotas WhatsApp carregadas")

# Incluir rotas principais
try:
    from app.api.clientes import router as clientes_router
    from app.api.veiculos import router as veiculos_router
    from app.api.servicos import router as servicos_router
    from app.api.categorias import router as categorias_router
    from app.api.ordens_servico import router as ordens_servico_router
    
    app.include_router(clientes_router, prefix="/api/clientes", tags=["clientes"])
    app.include_router(veiculos_router, prefix="/api/veiculos", tags=["veiculos"])
    app.include_router(servicos_router, prefix="/api/servicos", tags=["servicos"])
    app.include_router(categorias_router, prefix="/api/categorias", tags=["categorias"])
    app.include_router(ordens_servico_router, prefix="/api/ordens-servico", tags=["ordens_servico"])
    print("CHECK Rotas principais carregadas")
except ImportError as e:
    print(f"Aviso: Algumas rotas nao disponiveis: {e}")

@app.get("/")
async def root():
    return {"message": "LavaJato System API", "status": "running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "whatsapp_available": has_whatsapp,
        "api": "running"
    }

@app.get("/api/test")
async def test_route():
    return {"message": "API funcionando!"}

# Startup event para melhor performance
@app.on_event("startup")
async def startup_event():
    """Pre-carrega dependencias para melhor performance"""
    try:
        from app.database import SessionLocal
        from app.models.clientes import Cliente
        
        # Forcar inicializacao do ORM
        db = SessionLocal()
        try:
            db.query(Cliente).limit(1).all()
        except:
            pass
        finally:
            db.close()
        print("CHECK Dependencias pre-carregadas - API otimizada!")
    except Exception as e:
        print(f"Aviso no startup: {e}")
