import os
from typing import Optional

class WhatsAppConfig:
    # Configuracoes do numero da loja
    NUMERO_LOJA = "41988548538"  # Numero fixo da loja
    NOME_LOJA = "LavaJato Express"
    
    # Configuracoes de sessao
    SESSION_DIR = "./whatsapp_session"
    
    @staticmethod
    def get_numero_formatado() -> str:
        numeros = ''.join(filter(str.isdigit, WhatsAppConfig.NUMERO_LOJA))
        if len(numeros) <= 11:
            numeros = "55" + numeros
        return numeros

config = WhatsAppConfig()
