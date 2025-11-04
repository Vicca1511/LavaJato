from datetime import datetime

class MensagemTemplates:

    @staticmethod
    def servico_agendado(cliente_nome: str, veiculo_placa: str, data_hora: str, servico: str) -> str:
        return f"""LavaJato - OrdemServico Confirmado

Olá {cliente_nome}!

Seu ordem_servico foi confirmado:

Data/Hora: {data_hora}
Veículo: {veiculo_placa}
Serviço: {servico}

Aguardamos você!

Equipe LavaJato"""

    @staticmethod
    def servico_finalizado(cliente_nome: str, veiculo_placa: str, servico_nome: str, valor: float, codigo_confirmacao: str) -> str:
        return f"""LavaJato - Serviço Finalizado

Olá {cliente_nome}!

Seu veículo {veiculo_placa} está pronto!

Serviço: {servico_nome}
Valor: R$ {valor:.2f}
Código: {codigo_confirmacao}

Obrigado pela preferência!

Equipe LavaJato"""

    @staticmethod
    def lembrete_ordem_servico(cliente_nome: str, data_hora: str, servico: str) -> str:
        return f"""LavaJato - Lembrete

Olá {cliente_nome}!

Lembramos do seu ordem_servico:

Data/Hora: {data_hora}
Serviço: {servico}

Te aguardamos!

Equipe LavaJato"""

    @staticmethod
    def teste_conexao() -> str:
        return f"""LavaJato - Teste de Sistema

Teste: {datetime.now().strftime("%d/%m/%Y %H:%M")}

Sistema WhatsApp funcionando!

Equipe LavaJato"""
