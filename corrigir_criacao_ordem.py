# Corrigir função criar_ordem_servico
with open('backend/app/api/ordens_servico.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Encontrar e corrigir a função criar_ordem_servico
import re

# Nova implementação da função
nova_funcao = '''
@router.post("/", response_model=OrdemServicoResponse)
def criar_ordem_servico(ordem: OrdemServicoCreate, db: Session = Depends(get_db)):
    """Cria nova ordem de serviço"""
    try:
        # Verificar se veículo existe
        veiculo = db.query(Veiculo).filter(Veiculo.id == ordem.veiculo_id).first()
        if not veiculo:
            raise HTTPException(status_code=404, detail="Veículo não encontrado")

        # Verificar se serviço existe
        servico = db.query(Servico).filter(Servico.id == ordem.servico_id).first()
        if not servico:
            raise HTTPException(status_code=404, detail="Serviço não encontrado")

        # Criar ordem com campos que existem no modelo
        db_ordem = OrdemServico(
            cliente_id=1,  # Usar cliente padrão por enquanto
            veiculo=veiculo.modelo,
            placa=veiculo.placa,
            servico_id=ordem.servico_id,
            valor_total=servico.valor_base,
            observacoes=ordem.observacoes or "",
            status="SOLICITADO"
        )

        db.add(db_ordem)
        db.commit()
        db.refresh(db_ordem)
        return db_ordem

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar ordem: {str(e)}")'''

# Substituir a função antiga
pattern = r'@router\.post\("/", response_model=OrdemServicoResponse\)\s*def criar_ordem_servico.*?raise HTTPException\(status_code=500, detail=f"Erro ao criar ordem: \{str\(e\)\}"\)'
new_content = re.sub(pattern, nova_funcao, content, flags=re.DOTALL)

with open('backend/app/api/ordens_servico.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Função criar_ordem_servico corrigida!")
