import asyncio
import json
import time
from typing import Dict, List, Any
from datetime import datetime
from sqlalchemy.orm import Session
from ..models.ordens_servico import OrdemServico, StatusOrdemServico

class TempoRealService:
    def __init__(self):
        self.connected_clients = {}
        self.ordem_updates = {}
    
    async def connect(self, client_id: str, websocket):
        """Conecta um cliente ao serviço de tempo real"""
        self.connected_clients[client_id] = websocket
        print(f"Client {client_id} conectado. Total: {len(self.connected_clients)}")
    
    async def disconnect(self, client_id: str):
        """Desconecta um cliente"""
        if client_id in self.connected_clients:
            del self.connected_clients[client_id]
            print(f"Client {client_id} desconectado. Total: {len(self.connected_clients)}")
    
    async def broadcast_ordem_update(self, ordem_id: int, db: Session):
        """Transmite atualização de ordem para todos os clientes conectados"""
        ordem = db.query(OrdemServico).filter(OrdemServico.id == ordem_id).first()
        if not ordem:
            return
        
        ordem_data = {
            'id': ordem.id,
            'cliente_id': ordem.cliente_id,
            'veiculo': ordem.veiculo,
            'placa': ordem.placa,
            'status': ordem.status.value,
            'data_entrada': ordem.data_entrada.isoformat() if ordem.data_entrada else None,
            'data_inicio': ordem.data_inicio.isoformat() if ordem.data_inicio else None,
            'data_fim': ordem.data_fim.isoformat() if ordem.data_fim else None,
            'valor_total': float(ordem.valor_total) if ordem.valor_total else 0.0,
            'observacoes': ordem.observacoes,
            'etapa_atual': self._get_etapa_atual(ordem.status),
            'progresso': self._get_progresso(ordem.status),
            'timestamp': datetime.now().isoformat()
        }
        
        message = {
            'type': 'ordem_update',
            'data': ordem_data
        }
        
        # Envia para todos os clientes conectados
        disconnected_clients = []
        for client_id, websocket in self.connected_clients.items():
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                print(f"Erro enviando para {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Remove clientes desconectados
        for client_id in disconnected_clients:
            await self.disconnect(client_id)
    
    def _get_etapa_atual(self, status: StatusOrdemServico) -> str:
        """Retorna a etapa atual baseada no status"""
        etapas = {
            StatusOrdemServico.SOLICITADO: "Recebimento do Veículo",
            StatusOrdemServico.CONFIRMADO: "Confirmação do Serviço", 
            StatusOrdemServico.EM_ANDAMENTO: "Lavagem em Andamento",
            StatusOrdemServico.AGUARDANDO_PAGAMENTO: "Aguardando Pagamento",
            StatusOrdemServico.FINALIZADO: "Serviço Finalizado",
            StatusOrdemServico.CANCELADO: "Serviço Cancelado"
        }
        return etapas.get(status, "Status Desconhecido")
    
    def _get_progresso(self, status: StatusOrdemServico) -> int:
        """Retorna o progresso percentual baseado no status"""
        progresso = {
            StatusOrdemServico.SOLICITADO: 10,
            StatusOrdemServico.CONFIRMADO: 30,
            StatusOrdemServico.EM_ANDAMENTO: 60,
            StatusOrdemServico.AGUARDANDO_PAGAMENTO: 85,
            StatusOrdemServico.FINALIZADO: 100,
            StatusOrdemServico.CANCELADO: 0
        }
        return progresso.get(status, 0)
    
    async def enviar_estatisticas_tempo_real(self, db: Session):
        """Envia estatísticas em tempo real para os clientes"""
        estatisticas = {
            'ordens_hoje': db.query(OrdemServico).filter(
                OrdemServico.data_entrada >= datetime.now().date()
            ).count(),
            'ordens_andamento': db.query(OrdemServico).filter(
                OrdemServico.status == StatusOrdemServico.EM_ANDAMENTO
            ).count(),
            'ordens_finalizadas_hoje': db.query(OrdemServico).filter(
                OrdemServico.status == StatusOrdemServico.FINALIZADO,
                OrdemServico.data_fim >= datetime.now().date()
            ).count(),
            'faturamento_hoje': self._calcular_faturamento_hoje(db),
            'timestamp': datetime.now().isoformat()
        }
        
        message = {
            'type': 'estatisticas',
            'data': estatisticas
        }
        
        disconnected_clients = []
        for client_id, websocket in self.connected_clients.items():
            try:
                await websocket.send_text(json.dumps(message))
            except Exception:
                disconnected_clients.append(client_id)
        
        for client_id in disconnected_clients:
            await self.disconnect(client_id)
    
    def _calcular_faturamento_hoje(self, db: Session) -> float:
        """Calcula o faturamento do dia"""
        from sqlalchemy import func
        result = db.query(func.sum(OrdemServico.valor_total)).filter(
            OrdemServico.status == StatusOrdemServico.FINALIZADO,
            OrdemServico.data_fim >= datetime.now().date()
        ).scalar()
        return float(result) if result else 0.0

# Instância global do serviço de tempo real
tempo_real_service = TempoRealService()
