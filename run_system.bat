@echo off
chcp 65001 > nul
echo � INICIANDO SISTEMA LAVA-JATO...
echo.

echo � ATIVANDO AMBIENTE...
call venv\Scripts\activate.bat

echo � INICIANDO BACKEND (FastAPI)...
start "LavaJato Backend" cmd /k "cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak > nul

echo �� INICIANDO FRONTEND (Streamlit)...
start "LavaJato Frontend" cmd /k "cd frontend && streamlit run app.py"

echo ✅ SISTEMA INICIADO!
echo.
echo � ACESSOS:
echo Frontend: http://localhost:8501
echo API Docs: http://localhost:8000/docs
echo.
echo ⚠️  Mantenha estas janelas abertas!
echo.
pause
