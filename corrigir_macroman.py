#!/usr/bin/env python3
"""
Corrige o encoding MacRoman do arquivo frontend/operacoes/app.py
"""
import chardet

def corrigir_macroman():
    arquivo = 'frontend/operacoes/app.py'
    
    print("🔧 Convertendo de MacRoman para UTF-8...")
    
    # Lê o arquivo em modo binário
    with open(arquivo, 'rb') as f:
        conteudo_bin = f.read()
    
    # Tenta decodificar de MacRoman
    try:
        conteudo_texto = conteudo_bin.decode('macroman')
        print("✅ Sucesso na decodificação MacRoman!")
    except UnicodeDecodeError as e:
        print(f"❌ Erro na decodificação MacRoman: {e}")
        print("🔄 Tentando com substituição de caracteres...")
        conteudo_texto = conteudo_bin.decode('macroman', errors='replace')
    
    # Reescreve o arquivo em UTF-8
    try:
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write(conteudo_texto)
        print("✅ Arquivo convertido para UTF-8 com sucesso!")
        
        # Verifica se está legível
        with open(arquivo, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
            print(f"📄 Arquivo tem {len(linhas)} linhas")
            if linhas:
                print("📝 Primeiras linhas:")
                for i, linha in enumerate(linhas[:3]):
                    print(f"  {i+1}: {linha.strip()}")
                    
        return True
        
    except Exception as e:
        print(f"❌ Erro ao salvar: {e}")
        return False

if __name__ == "__main__":
    corrigir_macroman()