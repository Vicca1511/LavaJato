@echo off
chcp 65001 > nul
echo Ì∫ó INICIANDO SISTEMA LAVA-JATO...
echo.

echo Ì¥ß ATIVANDO AMBIENTE...
call venv\Scripts\activate.bat

echo Ìºê INICIANDO BACKEND (FastAPI)...
start "LavaJato Backend" cmd /k "cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak > nul

echo ÔøΩÔøΩ INICIANDO FRONTEND (Streamlit)...
start "LavaJato Frontend" cmd /k "cd frontend && streamlit run app.py"

echo ‚úÖ SISTEMA INICIADO!
echo.
echo Ìºê ACESSOS:
echo Frontend: http://localhost:8501
echo API Docs: http://localhost:8000/docs
echo.
echo ‚ö†Ô∏è  Mantenha estas janelas abertas!
echo.
pause
