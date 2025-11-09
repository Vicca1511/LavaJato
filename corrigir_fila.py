import re

# Ler o arquivo atual
with open('backend/app/api/ordens_servico.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Nova função obter_fila
nova_funcao = '''@router.get("/fila", response_model=List[FilaResponse])
def obter_fila(db: Session = Depends(get_db)):
    """Obtem fila de ordens (SOLICITADO e EM_ANDAMENTO)"""
    try:
        # Usar status que existem no modelo atual
        ordens = db.query(OrdemServico).filter(
            OrdemServico.status.in_(['SOLICITADO', 'EM_ANDAMENTO'])
        ).order_by(OrdemServico.data_entrada).all()
        
        # Preparar resposta da fila
        fila_response = []
        for i, ordem in enumerate(ordens, 1):
            fila_response.append(FilaResponse(
                id=ordem.id,
                posicao_fila=i,  # Usar índice como posição
                status=ordem.status.value,
                veiculo_placa=ordem.placa,  # Usar placa do modelo
                servico_nome="Lavagem",  # Placeholder
                valor_cobrado=float(ordem.valor_total),
                data_entrada=ordem.data_entrada
            ))
        
        return fila_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar fila: {str(e)}")'''

# Substituir a função obter_fila
pattern = r'@router\.get\("/fila".*?def obter_fila.*?return fila_response.*?except Exception as e:\s*raise HTTPException\(status_code=500, detail=f"Erro ao buscar fila: \{str\(e\)\}"\)'
new_content = re.sub(pattern, nova_funcao, content, flags=re.DOTALL)

# Se não encontrou o padrão completo, tentar substituir apenas a parte interna
if new_content == content:
    pattern2 = r'(@router\.get\("/fila", response_model=List\[FilaResponse\]\)\s*def obter_fila\(db: Session = Depends\(get_db\)\):\s*""".*?"""\s*).*?(?=\n\n@|\n\n#|\Z)'
    new_content = re.sub(pattern2, r'\1' + nova_funcao.split('def obter_fila')[-1], content, flags=re.DOTALL)

# Salvar o arquivo corrigido
with open('backend/app/api/ordens_servico.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Função obter_fila corrigida!")
