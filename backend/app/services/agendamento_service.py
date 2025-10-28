from datetime import datetime
from typing import Dict, Any
from .whatsapp_service import whatsapp_service
from .mensagem_templates import MensagemTemplates

class AgendamentoService:
    
    @staticmethod
    def enviar_confirmacao_agendamento(telefone: str, cliente_nome: str, veiculo_placa: str, 
                                     data_hora: str, servico: str) -> Dict[str, Any]:
        mensagem = MensagemTemplates.servico_agendado(
            cliente_nome=cliente_nome,
            veiculo_placa=veiculo_placa,
            data_hora=data_hora,
            servico=servico
        )
        
        return whatsapp_service.enviar_mensagem(telefone, mensagem)
    
    @staticmethod
    def enviar_servico_finalizado(telefone: str, cliente_nome: str, veiculo_placa: str,
                                servico_nome: str, valor: float, codigo_confirmacao: str) -> Dict[str, Any]:
        mensagem = MensagemTemplates.servico_finalizado(
            cliente_nome=cliente_nome,
            veiculo_placa=veiculo_placa,
            servico_nome=servico_nome,
            valor=valor,
            codigo_confirmacao=codigo_confirmacao
        )
        
        return whatsapp_service.enviar_mensagem(telefone, mensagem)
    
    @staticmethod
    def enviar_lembrete_agendamento(telefone: str, cliente_nome: str, data_hora: str, servico: str) -> Dict[str, Any]:
        mensagem = MensagemTemplates.lembrete_agendamento(
            cliente_nome=cliente_nome,
            data_hora=data_hora,
            servico=servico
        )
        
        return whatsapp_service.enviar_mensagem(telefone, mensagem)

agendamento_service = AgendamentoService()
