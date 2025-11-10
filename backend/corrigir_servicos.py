#!/usr/bin/env python3
"""
Corrige os preços dos serviços
"""
import sys
import os
sys.path.append('.')

from app.database import get_db
from app.models.servicos import Servico

def corrigir_servicos():
    db = next(get_db())
    
    try:
        servicos = db.query(Servico).all()
        precos = [45.00, 85.00, 120.00, 200.00]
        
        for i, servico in enumerate(servicos):
            preco = precos[i % len(precos)]
            servico.preco = preco
            print(f"💰 {servico.nome}: R$ {preco:.2f}")
        
        db.commit()
        print("✅ Preços dos serviços corrigidos!")
        
    except Exception as e:
        print(f"❌ Erro ao corrigir serviços: {e}")
        db.rollback()

if __name__ == "__main__":
    corrigir_servicos()