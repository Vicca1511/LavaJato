# -*- coding: utf-8 -*-
import asyncio
import logging
from typing import Dict, List, Optional
from .whatsapp_web import WhatsAppWeb

logger = logging.getLogger(__name__)

class WhatsAppManager:
    """
    Gerenciador principal do WhatsApp para o Lava Jato
    """
    
    def __init__(self):
        self.whatsapp = None
        self.is_initialized = False
        
    async def initialize(self):
        """Inicializa o servico WhatsApp - apenas se nao estiver inicializado"""
        if self.is_initialized and self.whatsapp and self.whatsapp.is_connected:
            print("✅ WhatsApp ja esta inicializado e conectado")
            return True
            
        print("Iniciando sistema WhatsApp...")
        try:
            self.whatsapp = WhatsAppWeb()
            success = await self.whatsapp.start_session()
            if success:
                print("Aguardando autenticacao...")
                authenticated = await self.whatsapp.wait_for_authentication()
                if authenticated:
                    self.is_initialized = True
                    print("Sistema WhatsApp inicializado com sucesso!")
                    return True
                else:
                    print("Falha na autenticacao do WhatsApp")
                    return False
            else:
                print("Falha ao iniciar sessao do WhatsApp")
                return False
        except Exception as e:
            print(f"Erro ao inicializar WhatsApp: {e}")
            return False
    
    async def enviar_resumo_servico(self, numero_cliente: str, nome_cliente: str, servicos: List[Dict], total: float):
        """Envia resumo de servicos para o cliente"""
        # Se ja estiver inicializado, usa a instancia existente
        if not self.is_initialized or not self.whatsapp or not self.whatsapp.is_connected:
            return {
                "success": False, 
                "error": "WhatsApp nao inicializado. Execute 'python iniciar_whatsapp.py' primeiro",
                "solucao": "Execute o WhatsApp em um terminal separado antes de usar a API"
            }
        
        # Formata lista de servicos
        servicos_texto = "\n".join([f"• {s['nome']}: R$ {s['valor']:.2f}" for s in servicos])
        
        mensagem = f"""
LAVA JATO EXPRESS - RESUMO DE SERVICOS

Cliente: {nome_cliente}

SERVICOS REALIZADOS:
{servicos_texto}

TOTAL: R$ {total:.2f}

Formas de pagamento:
• PIX
• Dinheiro
• Cartao

Obrigado pela preferencia!
        """.strip()
        
        try:
            print(f" Enviando mensagem para {numero_cliente}...")
            success = await self.whatsapp.send_message(numero_cliente, mensagem)
            return {
                "success": success, 
                "cliente": nome_cliente, 
                "total": total,
                "telefone": numero_cliente,
                "mensagem_enviada": mensagem if success else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def close(self):
        """Fecha o servico"""
        if self.whatsapp:
            await self.whatsapp.close()
        self.is_initialized = False

# Instancia global para uso em toda aplicacao
whatsapp_manager = WhatsAppManager()
