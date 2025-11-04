# -*- coding: utf-8 -*-
import asyncio
import logging
import os
from playwright.async_api import async_playwright
import time

logger = logging.getLogger(__name__)

class WhatsAppWeb:
    """
    WhatsApp Web - Usando XPath especifico do botao enviar
    """
    
    def __init__(self):
        self.browser = None
        self.page = None
        self.is_connected = False
        self.profile_dir = "./chrome_profile"
        
    async def start_session(self):
        """Inicia sessao WhatsApp Web"""
        try:
            playwright = await async_playwright().start()
            
            # Cria diretorio do perfil se nao existir
            os.makedirs(self.profile_dir, exist_ok=True)
            
            self.browser = await playwright.chromium.launch_persistent_context(
                user_data_dir=self.profile_dir,
                headless=False,
                viewport={'width': 1200, 'height': 800},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-extensions'
                ]
            )
            
            # Pega a primeira pagina
            pages = self.browser.pages
            if pages:
                self.page = pages[0]
            else:
                self.page = await self.browser.new_page()
            
            # Navega para WhatsApp Web
            await self.page.goto('https://web.whatsapp.com', wait_until='networkidle')
            
            logger.info("WhatsApp Web iniciado - Escaneie o QR Code")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao iniciar WhatsApp Web: {e}")
            return False
    
    async def wait_for_authentication(self, timeout=120):
        """Aguarda autenticacao do usuario"""
        logger.info("Aguardando autenticacao...")
        
        try:
            seletores = [
                'div[aria-label="Lista de conversas"]',
                'div[role="grid"]', 
                'div[role="row"]',
            ]
            
            for seletor in seletores:
                try:
                    await self.page.wait_for_selector(seletor, timeout=15000)
                    self.is_connected = True
                    logger.info(f"Autenticacao detectada via seletor: {seletor}")
                    return True
                except:
                    continue
            
            logger.error("Nenhum seletor de autenticacao funcionou")
            return False
            
        except Exception as e:
            logger.error(f"Erro na autenticacao: {e}")
            return False
    
    async def check_connection_status(self):
        """Verifica status da conexao"""
        if not self.page:
            return False
            
        try:
            indicators = [
                await self.page.query_selector('div[aria-label="Lista de conversas"]'),
                await self.page.query_selector('div[role="grid"]'),
                await self.page.query_selector('div[role="row"]')
            ]
            
            if any(indicators):
                self.is_connected = True
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Erro ao verificar status: {e}")
            return False
    
    async def send_message(self, phone: str, message: str):
        """Envia mensagem usando o XPath especifico do botao enviar"""
        if not await self.check_connection_status():
            logger.error("Nao conectado ao WhatsApp")
            return False
            
        try:
            print(f"Iniciando envio para {phone}...")
            
            # METODO 1: Tenta abrir conversa via URL (mais rapido quando funciona)
            print("Tentando abrir conversa via URL...")
            chat_url = f'https://web.whatsapp.com/send?phone={phone}&text={message}'
            await self.page.goto(chat_url, wait_until='networkidle')
            
            # Aguarda um tempo generoso para carregar
            print("Aguardando conversa carregar (15 segundos)...")
            await self.page.wait_for_timeout(15000)
            
            # METODO 2: Se a URL nao funcionou, tenta o metodo manual
            if not await self._is_conversation_loaded():
                print("URL direta nao funcionou, tentando metodo manual...")
                success = await self._open_conversation_manually(phone, message)
                if not success:
                    return False
            
            # AGORA USA O XPATH ESPECIFICO PARA ENVIAR
            print("Procurando botao enviar pelo XPath especifico...")
            
            # XPath exato que voce forneceu
            xpath_envio = '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[4]/div/span/div/div/div[1]/div[1]/span'
            
            # Tenta encontrar o botao pelo XPath
            send_button = await self.page.query_selector(f'xpath={xpath_envio}')
            
            if send_button:
                print("BOTAO ENCONTRADO PELO XPATH! Clicando...")
                await send_button.click()
                await self.page.wait_for_timeout(3000)
                print("SUCESSO: Mensagem enviada via XPath!")
                return True
            else:
                print("XPath nao encontrado, tentando seletores alternativos...")
                
                # Fallback: outros seletores de botao enviar
                send_selectors = [
                    'button[data-testid="compose-btn-send"]',
                    'span[data-testid="send"]',
                    'button[aria-label="Enviar"]',
                    'button[title="Enviar"]',
                    'div[role="button"][tabindex="0"]'  # Botao generico
                ]
                
                for selector in send_selectors:
                    button = await self.page.query_selector(selector)
                    if button:
                        print(f"Botao encontrado: {selector}")
                        await button.click()
                        await self.page.wait_for_timeout(3000)
                        print(f"SUCESSO: Mensagem enviada via {selector}!")
                        return True
                
                # Ultima tentativa: Enter
                print("Tentando enviar via Enter...")
                await self.page.keyboard.press('Enter')
                await self.page.wait_for_timeout(3000)
                print("Mensagem enviada via Enter!")
                return True
                
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
            return False
    
    async def _is_conversation_loaded(self):
        """Verifica se a conversa esta carregada"""
        try:
            # Verifica se existe algum elemento da conversa
            conversation_indicators = [
                'div[data-testid="conversation-panel-wrapper"]',
                'div[title="Digite uma mensagem"]',
                'div[role="textbox"]'
            ]
            
            for selector in conversation_indicators:
                element = await self.page.query_selector(selector)
                if element:
                    return True
            return False
        except:
            return False
    
    async def _open_conversation_manually(self, phone: str, message: str):
        """Abre conversa manualmente"""
        try:
            print("Abrindo conversa manualmente...")
            
            # Clica no botao nova conversa
            new_chat_selectors = [
                'button[aria-label="Nova conversa"]',
                'div[title="Nova conversa"]',
                'span[data-testid="chat"]'
            ]
            
            for selector in new_chat_selectors:
                button = await self.page.query_selector(selector)
                if button:
                    await button.click()
                    await self.page.wait_for_timeout(2000)
                    break
            
            # Procura campo de pesquisa
            search_box = await self.page.query_selector('div[title="Caixa de pesquisa de texto"]') or await self.page.query_selector('input[type="text"]')
            if search_box:
                await search_box.click()
                await self.page.wait_for_timeout(1000)
                await search_box.type(phone, delay=100)
                await self.page.wait_for_timeout(3000)
                await self.page.keyboard.press('Enter')
                await self.page.wait_for_timeout(3000)
                
                # Digita a mensagem
                message_box = await self.page.query_selector('div[title="Digite uma mensagem"]') or await self.page.query_selector('div[role="textbox"]')
                if message_box:
                    await message_box.click()
                    await self.page.wait_for_timeout(1000)
                    await message_box.type(message, delay=50)
                    await self.page.wait_for_timeout(2000)
                    return True
            
            return False
            
        except Exception as e:
            print(f"Erro no metodo manual: {e}")
            return False
    
    async def close(self):
        """Fecha a sessao"""
        if self.browser:
            await self.browser.close()
