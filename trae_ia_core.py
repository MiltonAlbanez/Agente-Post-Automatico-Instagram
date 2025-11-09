"""
TRAE IA - Agente de Automação de Mídias Sociais
Implementação do System Prompt como Regra de Ouro Fundamental
"""

import sys
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

# Importar o System Prompt Manager
from core.system_prompt_manager import system_prompt_manager, enforce_system_rules

class TraeIA:
    """
    TRAE IA - Agente de Automação de Mídias Sociais de Alto Desempenho
    
    IDENTIDADE E MISSÃO CRÍTICA (NÃO NEGOCIÁVEL):
    Garantir a Operação Ininterrupta e Consistente (24/7) de todas as tarefas 
    de Postagem e Preseed, conforme o Cronograma de Produção.
    """
    
    def __init__(self):
        """
        Inicializa o TRAE IA com as Regras de Ouro ativas
        """
        self.mission_active = True
        self.system_prompt_loaded = system_prompt_manager.system_config is not None
        
        # Configurar logging
        self._setup_logging()
        
        # Exibir missão crítica
        self._display_mission()
        
        # Verificar status do sistema
        self._verify_system_status()
    
    def _setup_logging(self):
        """
        Configura logging focado na missão 24/7
        """
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - TRAE IA - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/trae_ia_core.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('TRAE_IA')
    
    def _display_mission(self):
        """
        Exibe a missão crítica do TRAE IA
        """
        mission = system_prompt_manager.get_mission_statement()
        print("=" * 80)
        print("🤖 TRAE IA - SISTEMA ATIVO")
        print("=" * 80)
        print(mission)
        print("=" * 80)
        
        self.logger.info("TRAE IA inicializado com missão crítica ativa")
    
    def _verify_system_status(self):
        """
        Verifica status crítico do sistema
        """
        status = system_prompt_manager.log_system_status()
        
        if not status['system_prompt_loaded']:
            self.logger.critical("❌ FALHA CRÍTICA: System Prompt não carregado")
            raise SystemError("System Prompt obrigatório não disponível")
        
        self.logger.info("✅ Sistema verificado - Regras de Ouro ativas")
    
    def processar_erro(self, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Processa erro seguindo REGRA 2: Consulta Obrigatória à LTM
        
        Args:
            error: Exceção capturada
            context: Contexto adicional do erro
            
        Returns:
            Resultado do processamento com ação recomendada
        """
        print("\n" + "="*60)
        print("🚨 FOCO NA RESTAURAÇÃO DA OPERAÇÃO 24/7...")
        print("="*60)
        
        # Preparar contexto do erro
        error_context = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': datetime.now().isoformat(),
            **(context or {})
        }
        
        self.logger.info(f"Processando erro: {error_context['error_type']} - {error_context['error_message']}")
        
        # REGRA 2: Consulta Obrigatória à LTM
        print("📋 EXECUTANDO CHECKLIST OBRIGATÓRIO:")
        print("✅ Confirmação da missão: Operação 24/7 Ininterrupta")
        print("🔍 Consultando Memória de Longo Prazo (LTM)...")
        
        resultado_ltm = system_prompt_manager.consultar_ltm_obrigatorio(error_context)
        
        print(f"✅ Consulta à LTM concluída: {resultado_ltm['ltm_consultada']}")
        
        # Determinar ação baseada na consulta LTM
        if resultado_ltm['solucao_historica_encontrada']:
            print("🎯 SOLUÇÃO HISTÓRICA ENCONTRADA!")
            solucao = resultado_ltm['solucao_final_sucesso']
            print(f"📝 Solução: {solucao['descricao']}")
            print(f"📚 Fonte: {solucao['fonte']}")
            print("⚡ APLICANDO SOLUÇÃO IMEDIATAMENTE (velocidade na restauração)")
            
            acao_recomendada = {
                'tipo': 'aplicar_solucao_historica',
                'solucao': solucao,
                'prioridade': 'CRITICAL'
            }
        else:
            print("⚠️ Nenhuma solução histórica encontrada")
            if resultado_ltm['tentativas_anteriores']:
                print(f"📊 Tentativas anteriores falhadas: {len(resultado_ltm['tentativas_anteriores'])}")
                for i, tentativa in enumerate(resultado_ltm['tentativas_anteriores'], 1):
                    print(f"   {i}. {tentativa['solucao']} ({tentativa['fonte']})")
            
            print("🔧 AUTORIZADO a gerar nova correção")
            print("⚠️ OBRIGATÓRIO: Testes rigorosos + Registro na LTM")
            
            acao_recomendada = {
                'tipo': 'gerar_nova_solucao',
                'tentativas_evitar': resultado_ltm['tentativas_anteriores'],
                'prioridade': 'HIGH'
            }
        
        # Status da operação 24/7
        print("✅ Status da operação 24/7: Sistema ativo e monitorando")
        print("⏰ Próximas tarefas agendadas:")
        print(system_prompt_manager._get_next_scheduled_tasks())
        print("="*60)
        
        return {
            'error_context': error_context,
            'ltm_result': resultado_ltm,
            'recommended_action': acao_recomendada,
            'system_status': 'operational'
        }
    
    def registrar_solucao_testada(self, error_context: Dict[str, Any], 
                                 solucao: str, fonte: str, sucesso: bool) -> bool:
        """
        Registra solução após testes rigorosos (REGRA 2)
        """
        print(f"\n📝 REGISTRANDO SOLUÇÃO NA LTM:")
        print(f"   Solução: {solucao}")
        print(f"   Fonte: {fonte}")
        print(f"   Sucesso: {'✅' if sucesso else '❌'}")
        
        resultado = system_prompt_manager.registrar_nova_solucao(
            error_context, solucao, fonte, sucesso
        )
        
        if resultado:
            print("✅ Solução registrada na Memória de Longo Prazo")
            self.logger.info(f"Solução registrada: {solucao} - Sucesso: {sucesso}")
        else:
            print("❌ Erro ao registrar solução")
            self.logger.error("Falha ao registrar solução na LTM")
        
        return resultado
    
    def validar_acao(self, action_type: str, context: Dict[str, Any] = None) -> bool:
        """
        Valida ação contra as Regras de Ouro (REGRA 3)
        """
        validation = enforce_system_rules(action_type, context or {})
        
        if not validation['allowed']:
            print(f"🚫 AÇÃO BLOQUEADA: {action_type}")
            for warning in validation['warnings']:
                print(f"   ⚠️ {warning}")
            self.logger.warning(f"Ação bloqueada: {action_type} - {validation['warnings']}")
            return False
        
        if validation['required_checks']:
            print(f"📋 VERIFICAÇÕES OBRIGATÓRIAS para {action_type}:")
            for check in validation['required_checks']:
                print(f"   ✅ {check}")
        
        return True
    
    def executar_tarefa_cron(self, task_name: str, task_function, *args, **kwargs):
        """
        Executa tarefa do cronograma com prioridade máxima (REGRA 1)
        """
        print(f"\n🎯 EXECUTANDO TAREFA CRÍTICA: {task_name}")
        print("⚡ PRIORIDADE MÁXIMA - Operação 24/7")
        
        try:
            # Validar se é tarefa crítica
            if not self.validar_acao('cron_task', {'task_name': task_name}):
                raise SystemError(f"Tarefa crítica bloqueada: {task_name}")
            
            # Executar tarefa
            resultado = task_function(*args, **kwargs)
            
            print(f"✅ TAREFA CONCLUÍDA: {task_name}")
            self.logger.info(f"Tarefa crítica executada com sucesso: {task_name}")
            
            return resultado
            
        except Exception as e:
            print(f"🚨 EMERGÊNCIA: Falha na tarefa crítica {task_name}")
            self.logger.critical(f"FALHA CRÍTICA: {task_name} - {str(e)}")
            
            # Processar erro automaticamente
            return self.processar_erro(e, {'task_name': task_name, 'task_type': 'cron'})

# Instância global do TRAE IA
trae_ia = TraeIA()

def processar_erro_automatico(error: Exception, context: Dict[str, Any] = None):
    """
    Função utilitária para processamento automático de erros
    """
    return trae_ia.processar_erro(error, context)

def executar_com_protecao(task_name: str, task_function, *args, **kwargs):
    """
    Executa função com proteção automática de erro
    """
    return trae_ia.executar_tarefa_cron(task_name, task_function, *args, **kwargs)