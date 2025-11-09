from sqlalchemy.orm import Session
from datetime import datetime
from ..models.ordens_servico import OrdemServico, StatusOrdemServico
from ..models.etapas_servico import EtapaServico
from .whatsapp_service import whatsapp_service
import logging

logger = logging.getLogger(__name__)

class FluxoAtendimentoService:
    def __init__(self, db: Session):
        self.db = db
    
    def criar_etapas_padrao(self, ordem_servico_id: int):
        """Cria etapas padrão para uma ordem de serviço"""
        etapas_padrao = [
            {"nome": "RECEPÇÃO", "descricao": "Recepção do veículo e checklist inicial", "ordem": 1, "tempo_estimado": 10},
            {"nome": "PRÉ-LAVAGEM", "descricao": "Limpeza inicial e remoção de sujeira grossa", "ordem": 2, "tempo_estimado": 15},
            {"nome": "LAVAGEM", "descricao": "Lavagem completa do veículo", "ordem": 3, "tempo_estimado": 30},
            {"nome": "SECAGEM", "descricao": "Secagem e limpeza de vidros", "ordem": 4, "tempo_estimado": 20},
            {"nome": "ACABAMENTO", "descricao": "Acabamento final e verificação de qualidade", "ordem": 5, "tempo_estimado": 15},
            {"nome": "ENTREGA", "descricao": "Preparação para entrega ao cliente", "ordem": 6, "tempo_estimado": 10}
        ]
        
        for etapa_data in etapas_padrao:
            etapa = EtapaServico(
                ordem_servico_id=ordem_servico_id,
                **etapa_data
            )
            self.db.add(etapa)
        
        self.db.commit()
        logger.info(f"Etapas padrão criadas para ordem #{ordem_servico_id}")
    
    def iniciar_ordem(self, ordem_id: int, responsavel: str = "Sistema"):
        """Inicia uma ordem de serviço"""
        ordem = self.db.query(OrdemServico).filter(OrdemServico.id == ordem_id).first()
        if not ordem:
            raise ValueError("Ordem não encontrada")
        
        # Criar etapas se não existirem
        if not ordem.etapas:
            self.criar_etapas_padrao(ordem_id)
            # Recarregar a ordem com as etapas
            ordem = self.db.query(OrdemServico).filter(OrdemServico.id == ordem_id).first()
        
        ordem.status = StatusOrdemServico.EM_ANDAMENTO
        ordem.data_inicio = datetime.now()
        ordem.etapa_atual = "RECEPÇÃO"
        ordem.progresso = 0
        
        # Iniciar primeira etapa
        primeira_etapa = self.db.query(EtapaServico).filter(
            EtapaServico.ordem_servico_id == ordem_id,
            EtapaServico.ordem == 1
        ).first()
        
        if primeira_etapa:
            primeira_etapa.status = "EM_ANDAMENTO"
            primeira_etapa.data_inicio = datetime.now()
            primeira_etapa.responsavel = responsavel
        
        self.db.commit()
        
        # Notificar cliente
        self._notificar_inicio_servico(ordem)
        
        return ordem
    
    def avancar_etapa(self, ordem_id: int, responsavel: str = "Sistema"):
        """Avança para a próxima etapa do serviço"""
        ordem = self.db.query(OrdemServico).filter(OrdemServico.id == ordem_id).first()
        if not ordem:
            raise ValueError("Ordem não encontrada")
        
        # Concluir etapa atual
        etapa_atual = self.db.query(EtapaServico).filter(
            EtapaServico.ordem_servico_id == ordem_id,
            EtapaServico.status == "EM_ANDAMENTO"
        ).first()
        
        if etapa_atual:
            etapa_atual.status = "CONCLUIDA"
            etapa_atual.data_conclusao = datetime.now()
        
        # Buscar próxima etapa
        proxima_etapa = self.db.query(EtapaServico).filter(
            EtapaServico.ordem_servico_id == ordem_id,
            EtapaServico.status == "PENDENTE"
        ).order_by(EtapaServico.ordem).first()
        
        if proxima_etapa:
            # Iniciar próxima etapa
            proxima_etapa.status = "EM_ANDAMENTO"
            proxima_etapa.data_inicio = datetime.now()
            proxima_etapa.responsavel = responsavel
            ordem.etapa_atual = proxima_etapa.nome
            
            # Calcular progresso
            total_etapas = self.db.query(EtapaServico).filter(
                EtapaServico.ordem_servico_id == ordem_id
            ).count()
            
            etapas_concluidas = self.db.query(EtapaServico).filter(
                EtapaServico.ordem_servico_id == ordem_id,
                EtapaServico.status == "CONCLUIDA"
            ).count()
            
            ordem.progresso = int((etapas_concluidas / total_etapas) * 100) if total_etapas > 0 else 0
        else:
            # Todas as etapas concluídas
            ordem.status = StatusOrdemServico.AGUARDANDO_PAGAMENTO
            ordem.etapa_atual = "FINALIZADO"
            ordem.progresso = 100
        
        self.db.commit()
        
        # Notificar cliente se avançou de etapa
        if etapa_atual and proxima_etapa:
            self._notificar_progresso_etapa(ordem, etapa_atual, proxima_etapa)
        
        return ordem, proxima_etapa
    
    def finalizar_ordem(self, ordem_id: int):
        """Finaliza a ordem de serviço"""
        ordem = self.db.query(OrdemServico).filter(OrdemServico.id == ordem_id).first()
        if not ordem:
            raise ValueError("Ordem não encontrada")
        
        ordem.status = StatusOrdemServico.FINALIZADO
        ordem.data_fim = datetime.now()
        ordem.progresso = 100
        ordem.etapa_atual = "ENTREGUE"
        
        self.db.commit()
        
        # Notificar conclusão
        self._notificar_conclusao_servico(ordem)
        
        return ordem
    
    def _notificar_inicio_servico(self, ordem):
        """Notifica o cliente sobre o início do serviço"""
        mensagem = f"""
🚗 *Lava Jato - Serviço Iniciado*

Olá! Seu veículo *{ordem.veiculo}* ({ordem.placa}) está em processo de lavagem.

📋 *Serviço Iniciado:* {datetime.now().strftime('%d/%m/%Y %H:%M')}
🚙 *Veículo:* {ordem.veiculo}
🔢 *Placa:* {ordem.placa}

Acompanhe o progresso do serviço! 🫧

_Equipe Lava Jato_
        """
        
        try:
            whatsapp_service.enviar_mensagem(ordem.cliente.telefone, mensagem)
            logger.info(f"Notificação de início enviada para ordem #{ordem.id}")
        except Exception as e:
            logger.error(f"Erro ao enviar notificação de início: {e}")
    
    def _notificar_progresso_etapa(self, ordem, etapa_concluida, proxima_etapa):
        """Notifica o cliente sobre o progresso do serviço"""
        mensagem = f"""
🔄 *Lava Jato - Andamento do Serviço*

Seu veículo *{ordem.veiculo}* está progredindo!

✅ *Etapa Concluída:* {etapa_concluida.nome}
➡️ *Próxima Etapa:* {proxima_etapa.nome}
📊 *Progresso:* {ordem.progresso}% completo

Agradecemos sua confiança! 🤝

_Equipe Lava Jato_
        """
        
        try:
            whatsapp_service.enviar_mensagem(ordem.cliente.telefone, mensagem)
            logger.info(f"Notificação de progresso enviada para ordem #{ordem.id}")
        except Exception as e:
            logger.error(f"Erro ao enviar notificação de progresso: {e}")
    
    def _notificar_conclusao_servico(self, ordem):
        """Notifica o cliente sobre a conclusão do serviço"""
        mensagem = f"""
🎉 *Lava Jato - Serviço Concluído!*

Seu veículo *{ordem.veiculo}* está pronto para retirada!

✅ *Serviço Concluído:* {datetime.now().strftime('%d/%m/%Y %H:%M')}
🚙 *Veículo:* {ordem.veiculo}
🔢 *Placa:* {ordem.placa}
💰 *Valor Total:* R$ {ordem.valor_total:.2f}

Agradecemos pela preferência! 🚗💨

_Equipe Lava Jato_
        """
        
        try:
            whatsapp_service.enviar_mensagem(ordem.cliente.telefone, mensagem)
            ordem.notificado_whatsapp = True
            self.db.commit()
            logger.info(f"Notificação de conclusão enviada para ordem #{ordem.id}")
        except Exception as e:
            logger.error(f"Erro ao enviar notificação de conclusão: {e}")
