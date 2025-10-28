import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class WhatsAppService:
    def __init__(self):
        self.mode = "SIMULATION"
        logger.info("WhatsAppService iniciado em modo SIMULATION")

    def enviar_mensagem(self, telefone: str, mensagem: str, force_mode: Optional[str] = None) -> Dict[str, Any]:
        telefone_formatado = self._formatar_telefone(telefone)

        print("=" * 50)
        print("WHATSAPP SIMULATION")
        print(f"Para: {telefone_formatado}")
        print(f"Mensagem: {mensagem}")
        print(f"Custo: GRATUITO")
        print("=" * 50)

        return {
            "success": True,
            "mode": "SIMULATION",
            "telefone": telefone_formatado,
            "custo": "GRATUITO",
            "mensagem_enviada": mensagem
        }

    def _formatar_telefone(self, telefone: str) -> str:
        numeros = ''.join(filter(str.isdigit, str(telefone)))
        if len(numeros) <= 11:
            numeros = "55" + numeros
        return numeros

    def testar_conexao(self, telefone_teste: str = "41988548538") -> Dict[str, Any]:
        mensagem_teste = "Teste de conexao LavaJato - Sistema OK!"
        resultado = self.enviar_mensagem(telefone_teste, mensagem_teste)

        return {
            "teste_realizado": True,
            "telefone_testado": telefone_teste,
            "resultado": resultado
        }

    def get_status(self) -> Dict[str, Any]:
        return {
            "servico": "WhatsApp",
            "modo": "SIMULATION",
            "status": "ATIVO",
            "custo": "GRATUITO"
        }

whatsapp_service = WhatsAppService()
