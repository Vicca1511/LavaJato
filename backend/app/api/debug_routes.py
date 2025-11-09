from fastapi import APIRouter, Request
import json

router = APIRouter()

@router.post("/debug/ordens")
async def debug_ordens(request: Request):
    """Endpoint para debug - mostra exatamente o que o frontend envia"""
    body = await request.body()
    headers = dict(request.headers)
    
    print("=== DEBUG FRONTEND REQUEST ===")
    print(f"Content-Type: {headers.get('content-type', 'NOT SET')}")
    print(f"Body raw: {body}")
    
    try:
        json_data = await request.json()
        print(f"Body JSON: {json_data}")
        return {"status": "received", "data": json_data}
    except Exception as e:
        print(f"JSON parse error: {e}")
        return {"status": "error", "error": str(e)}
