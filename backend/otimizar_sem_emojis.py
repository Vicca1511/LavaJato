import os

print("APLICANDO OTIMIZACOES DE PERFORMANCE...")

# 1. Otimizar database.py
print("1. Otimizando database.py...")
database_content = '''from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lavajato.db")

# Configuracao OTIMIZADA para performance
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
    echo=False,  # Desativar logs SQL
    future=True   # Modo SQLAlchemy 2.0
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''

with open('app/database.py', 'w') as f:
    f.write(database_content)

# 2. Otimizar main.py com lazy loading
print("2. Aplicando lazy loading no main.py...")
with open('app/main.py', 'r') as f:
    content = f.read()

# Substituir importacao de rotas
old_imports = '''try:
    from app.api import clientes, veiculos, servicos, categorias, ordens_servico
    has_core_routes = True
except ImportError as e:
    has_core_routes = False
    print(f"Aviso: Rotas principais nao disponiveis: {e}")'''

new_imports = '''has_core_routes = True  # Assumir que rotas estao disponiveis'''

# Substituir inclusao de rotas
old_includes = '''if has_core_routes:
    app.include_router(clientes.router, prefix="/api/clientes", tags=["clientes"])
    app.include_router(veiculos.router, prefix="/api/veiculos", tags=["veiculos"])
    app.include_router(servicos.router, prefix="/api/servicos", tags=["servicos"])
    app.include_router(categorias.router, prefix="/api/categorias", tags=["categorias"])
    app.include_router(ordens_servico.router, prefix="/api/ordens-servico", tags=["ordens_servico"])
    print("Rotas principais carregadas")'''

new_includes = '''if has_core_routes:
    # Lazy loading das rotas para melhor performance
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
    print("Rotas principais carregadas (lazy loading)")'''

content = content.replace(old_imports, new_imports)
content = content.replace(old_includes, new_includes)

# 3. Adicionar startup event
print("3. Adicionando startup event...")
startup_code = '''

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
        print("Dependencias pre-carregadas - API otimizada!")
    except Exception as e:
        print(f"Aviso no startup: {e}")

'''

# Encontrar posicao apos CORS
cors_pos = content.find('app.add_middleware')
if cors_pos != -1:
    cors_end = content.find(']', cors_pos) + 1
    cors_end = content.find('\n', cors_end) + 1
    content = content[:cors_end] + startup_code + content[cors_end:]

with open('app/main.py', 'w') as f:
    f.write(content)

print("TODAS AS OTIMIZACOES APLICADAS COM SUCESSO!")
print("Agora reinicie o servidor para ver os resultados!")
