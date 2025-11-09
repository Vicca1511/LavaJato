from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import json
import uuid
import logging
from ..database import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
router = APIRouter()

# Serviço simples de tempo real (sem dependência externa)
class SimpleTempoRealService:
    def __init__(self):
        self.connected_clients = {}
    
    async def connect(self, client_id: str, websocket):
        self.connected_clients[client_id] = websocket
        logger.info(f"Client {client_id} conectado. Total: {len(self.connected_clients)}")
    
    async def disconnect(self, client_id: str):
        if client_id in self.connected_clients:
            del self.connected_clients[client_id]
            logger.info(f"Client {client_id} desconectado. Total: {len(self.connected_clients)}")
    
    async def broadcast_message(self, message: dict):
        disconnected_clients = []
        for client_id, websocket in self.connected_clients.items():
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Erro enviando para {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        for client_id in disconnected_clients:
            await self.disconnect(client_id)

tempo_real_service = SimpleTempoRealService()

@router.websocket("/ws/tempo-real")
async def websocket_tempo_real(websocket: WebSocket, db: Session = Depends(get_db)):
    client_id = str(uuid.uuid4())
    
    await websocket.accept()
    await tempo_real_service.connect(client_id, websocket)
    
    try:
        # Mensagem de boas-vindas
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "client_id": client_id,
            "message": "Conectado ao serviço de tempo real"
        }))
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get('type') == 'ping':
                await websocket.send_text(json.dumps({'type': 'pong'}))
            
            elif message.get('type') == 'get_stats':
                # Enviar estatísticas básicas
                from ..models.ordens_servico import OrdemServico
                stats = {
                    'total_ordens': db.query(OrdemServico).count(),
                    'ordens_andamento': db.query(OrdemServico).filter(OrdemServico.status == 'EM_ANDAMENTO').count(),
                    'ordens_finalizadas': db.query(OrdemServico).filter(OrdemServico.status == 'FINALIZADO').count(),
                    'type': 'stats_update'
                }
                await websocket.send_text(json.dumps(stats))
                
    except WebSocketDisconnect:
        await tempo_real_service.disconnect(client_id)
    except Exception as e:
        logger.error(f"Erro WebSocket: {e}")
        await tempo_real_service.disconnect(client_id)