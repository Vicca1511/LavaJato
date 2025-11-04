import logging
from typing import Dict, Any, Optional
from ..core.settings import settings

logger = logging.getLogger(__name__)

class WhatsAppService:
    """
    Servico WhatsApp - Modo SIMULACAO
    """
    
    def __init__(self):
        self.mode = "SIMULATION"
        logger.info("WhatsAppService em modo SIMULATION")

    def enviar_mensagem(self, telefone: str, mensagem: str, force_mode: Optional[str] = None) -> Dict[str, Any]:
        """
        Envia mensagem - SEMPRE modo simulacao
        """
        telefone_formatado = self._formatar_telefone(telefone)

        print("=" * 60)
        print("WHATSAPP SIMULATION")
        print(f"Para: {telefone_formatado}")
        print(f"Mensagem: {mensagem}")
        print(f"Custo: GRATUITO")
        print("=" * 60)

        return {
            "success": True,
            "mode": "SIMULATION",
            "telefone": telefone_formatado,
            "custo": "GRATUITO",
            "observacao": "Mensagem simulada - Sistema pronto para API real"
        }

    def _formatar_telefone(self, telefone: str) -> str:
        numeros = ''.join(filter(str.isdigit, str(telefone)))
        if len(numeros) <= 11:
            numeros = "55" + numeros
        return numeros

    def testar_conexao(self, telefone_teste: str = "41988548538") -> Dict[str, Any]:
        from .mensagem_templates import MensagemTemplates
        mensagem_teste = MensagemTemplates.teste_conexao()
        resultado = self.enviar_mensagem(telefone_teste, mensagem_teste)
        
        return {
            "modo_utilizado": resultado.get("mode"),
            "custo": resultado.get("custo", "GRATUITO"),
            "sucesso": resultado.get("success", False),
            "telefone_testado": telefone_teste
        }

    def get_status(self) -> Dict[str, Any]:
        return {
            "servico": "WhatsApp",
            "modo": "SIMULATION",
            "status": "ATIVO",
            "custo": "GRATUITO",
            "observacao": "Modo desenvolvimento - Sem bloqueios do WhatsApp"
        }

whatsapp_service = WhatsAppService()
