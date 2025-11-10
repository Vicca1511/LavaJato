#!/usr/bin/env python3
"""
Alternativa para corrigir encoding problemático
"""
def corrigir_com_backup():
    arquivo_orig = 'frontend/operacoes/app.py.backup'
    arquivo_dest = 'frontend/operacoes/app.py'
    
    # Lê o backup em modo binário e tenta múltiplos encodings
    with open(arquivo_orig, 'rb') as f:
        raw_data = f.read()
    
    encodings_tentados = ['macroman', 'latin-1', 'iso-8859-1', 'cp1252', 'utf-8']
    
    for encoding in encodings_tentados:
        try:
            texto = raw_data.decode(encoding)
            print(f"✅ Decodificado com {encoding}")
            
            # Salva em UTF-8
            with open(arquivo_dest, 'w', encoding='utf-8') as f:
                f.write(texto)
            print(f"✅ Arquivo salvo em UTF-8 a partir de {encoding}")
            break
        except UnicodeDecodeError:
            continue
    else:
        print("❌ Não foi possível decodificar com nenhum encoding comum")
        # Última tentativa com replace
        texto = raw_data.decode('utf-8', errors='replace')
        with open(arquivo_dest, 'w', encoding='utf-8') as f:
            f.write(texto)
        print("✅ Arquivo salvo com substituição de caracteres inválidos")

if __name__ == "__main__":
    corrigir_com_backup()