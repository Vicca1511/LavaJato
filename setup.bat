@echo off
chcp 65001 > nul
echo ========================================
echo 🚗 SISTEMA LAVA-JATO - INSTALADOR
echo ========================================
echo.

echo 🔍 VERIFICANDO PRÉ-REQUISITOS...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERRO: Python não encontrado!
    echo 📥 Baixe em: https://www.python.org/downloads/
    echo ⚠️  Marque "Add Python to PATH" durante instalação
    pause
    exit /b 1
)

echo ✅ Python encontrado!

echo 📦 CRIANDO AMBIENTE VIRTUAL...
python -m venv venv
if %errorlevel% neq 0 (
    echo ❌ Erro ao criar ambiente virtual
    pause
    exit /b 1
)

echo 📥 INSTALANDO DEPENDÊNCIAS...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ❌ Erro ao instalar dependências
    pause
    exit /b 1
)

echo 🗄️ CRIANDO BANCO DE DADOS...
cd backend
python -c "from app.database import Base, engine; from app.models import clientes, veiculos; Base.metadata.create_all(bind=engine); print('✅ Banco criado!')"
cd ..

echo.
echo ========================================
echo ✅ CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!
echo ========================================
echo.
echo 🎯 PRÓXIMOS PASSOS:
echo 1. Execute run_system.bat
echo 2. Acesse http://localhost:8501
echo 3. Comece a usar o sistema!
echo.
echo ⚠️  Execute setup.bat apenas na primeira vez!
echo 🚀 Use run_system.bat sempre para iniciar.
echo.
pause