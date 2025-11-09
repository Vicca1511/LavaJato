# correcao_encoding.py
import os
import chardet

def detectar_encoding(arquivo):
    """Detecta o encoding de um arquivo"""
    with open(arquivo, 'rb') as f:
        raw_data = f.read()
    return chardet.detect(raw_data)['encoding']

def corrigir_encoding_arquivos():
    """Corrige problemas de encoding nos arquivos"""
    arquivos = ['operacoes_app_final.py', 'cliente_app.py']
    
    for arquivo in arquivos:
        if os.path.exists(arquivo):
            try:
                # Detectar encoding
                encoding = detectar_encoding(arquivo)
                print(f"📄 {arquivo}: Encoding detectado = {encoding}")
                
                # Ler com encoding correto
                with open(arquivo, 'r', encoding=encoding) as f:
                    conteudo = f.read()
                
                # Salvar com UTF-8
                with open(arquivo, 'w', encoding='utf-8') as f:
                    f.write(conteudo)
                
                print(f"✅ {arquivo}: Convertido para UTF-8")
                
            except Exception as e:
                print(f"❌ Erro ao corrigir {arquivo}: {e}")
        else:
            print(f"⚠️  Arquivo {arquivo} não encontrado")

def adicionar_pandas_cliente_app():
    """Adiciona import do pandas no cliente_app.py"""
    arquivo = 'cliente_app.py'
    
    if os.path.exists(arquivo):
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                linhas = f.readlines()
            
            # Verificar se pandas já está importado
            tem_pandas = any('import pandas' in linha for linha in linhas)
            
            if not tem_pandas:
                # Encontrar linha dos imports e adicionar pandas
                for i, linha in enumerate(linhas):
                    if 'import requests' in linha:
                        linhas.insert(i + 1, 'import pandas as pd\n')
                        break
                
                # Salvar arquivo atualizado
                with open(arquivo, 'w', encoding='utf-8') as f:
                    f.writelines(linhas)
                
                print("✅ pandas adicionado ao cliente_app.py")
            else:
                print("✅ pandas já está no cliente_app.py")
                
        except Exception as e:
            print(f"❌ Erro ao adicionar pandas: {e}")
    else:
        print(f"⚠️  Arquivo {arquivo} não encontrado")

if __name__ == "__main__":
    print("🛠️  CORRIGINDO PROBLEMAS DE ENCODING E IMPORTS")
    print("="*50)
    
    corrigir_encoding_arquivos()
    print()
    adicionar_pandas_cliente_app()
    
    print("\n🎉 CORREÇÕES CONCLUÍDAS!")