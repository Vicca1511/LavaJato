from cryptography.fernet import Fernet
import base64
import os
from typing import Any, Dict
import hashlib
import logging

logger = logging.getLogger(__name__)

class LGPDEncryption:
    def __init__(self):
        self.key = self._get_encryption_key()
        self.fernet = Fernet(self.key)
        logger.info("🔒 Serviço de criptografia LGPD inicializado")
    
    def _get_encryption_key(self) -> bytes:
        """Obtém a chave de criptografia do ambiente ou gera uma nova"""
        key_env = os.getenv('ENCRYPTION_KEY')
        if key_env:
            return base64.urlsafe_b64decode(key_env)
        else:
            # Em produção, isso deve vir de variáveis de ambiente
            key = Fernet.generate_key()
            key_encoded = base64.urlsafe_b64encode(key).decode()
            logger.warning(f"⚠️  CHAVE GERADA (SALVE EM .env): ENCRYPTION_KEY={key_encoded}")
            return key
    
    def encrypt_field(self, data: str) -> str:
        """Criptografa um campo de dados sensíveis"""
        if not data:
            return data
        try:
            encrypted = self.fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Erro ao criptografar campo: {e}")
            return data
    
    def decrypt_field(self, encrypted_data: str) -> str:
        """Descriptografa um campo de dados sensíveis"""
        if not encrypted_data:
            return encrypted_data
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception:
            # Retorna original se não for criptografado ou houver erro
            return encrypted_data
    
    def encrypt_sensitive_data(self, data: Dict[str, Any], sensitive_fields: list) -> Dict[str, Any]:
        """Criptografa campos sensíveis de um dicionário"""
        encrypted_data = data.copy()
        for field in sensitive_fields:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encrypt_field(str(encrypted_data[field]))
        return encrypted_data
    
    def decrypt_sensitive_data(self, data: Dict[str, Any], sensitive_fields: list) -> Dict[str, Any]:
        """Descriptografa campos sensíveis de um dicionário"""
        decrypted_data = data.copy()
        for field in sensitive_fields:
            if field in decrypted_data and decrypted_data[field]:
                decrypted_data[field] = self.decrypt_field(decrypted_data[field])
        return decrypted_data

    def hash_data(self, data: str) -> str:
        """Cria hash de dados para auditoria"""
        return hashlib.sha256(data.encode()).hexdigest()

# Campos sensíveis que devem ser criptografados
SENSITIVE_FIELDS = [
    'telefone', 'email', 'cpf', 'rg', 'endereco', 
    'placa', 'chassi', 'numero_cartao', 'vencimento_cartao'
]

# Instância global
lgpd_encryption = LGPDEncryption()