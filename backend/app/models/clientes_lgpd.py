from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
from ..database import Base
from ..core.security import lgpd_encryption, SENSITIVE_FIELDS

class ClienteLGPD(Base):
    __tablename__ = 'clientes_lgpd'
    
    id = Column(Integer, primary_key=True)
    
    # Campos não sensíveis
    nome = Column(String(100), nullable=False)
    data_cadastro = Column(DateTime, default=datetime.now)
    
    # Campos sensíveis (criptografados)
    _telefone = Column('telefone', Text, nullable=False)
    _email = Column('email', Text)
    _cpf = Column('cpf', Text)
    _endereco = Column('endereco', Text)
    
    @hybrid_property
    def telefone(self):
        return lgpd_encryption.decrypt_field(self._telefone) if self._telefone else None
    
    @telefone.setter
    def telefone(self, value):
        self._telefone = lgpd_encryption.encrypt_field(value) if value else None
    
    @hybrid_property
    def email(self):
        return lgpd_encryption.decrypt_field(self._email) if self._email else None
    
    @email.setter
    def email(self, value):
        self._email = lgpd_encryption.encrypt_field(value) if value else None
    
    @hybrid_property
    def cpf(self):
        return lgpd_encryption.decrypt_field(self._cpf) if self._cpf else None
    
    @cpf.setter
    def cpf(self, value):
        self._cpf = lgpd_encryption.encrypt_field(value) if value else None
    
    @hybrid_property
    def endereco(self):
        return lgpd_encryption.decrypt_field(self._endereco) if self._endereco else None
    
    @endereco.setter
    def endereco(self, value):
        self._endereco = lgpd_encryption.encrypt_field(value) if value else None