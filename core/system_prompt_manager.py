"""
TRAE IA - System Prompt Manager
Gerenciador do Prompt de Sistema Fundamental
Garante que todas as operações sigam as Regras de Ouro
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging
from pathlib import Path

# Adicionar o diretório src ao path para importar os serviços
sys.path.append(str(Path(__file__).parent.parent / "src"))

try:
    from src.services.error_reflection_manager import error_reflection
    from src.services.solution_strategy_manager import SolutionStrategyManager
    from src.services.structured_error_logger import structured_logger
    LTM_AVAILABLE = True
except ImportError as e:
    logging.warning(f"LTM services não disponíveis: {e}")
    LTM_AVAILABLE = False

class SystemPromptManager:
    """
    Gerenciador do Prompt de Sistema para TRAE IA
    Responsável por carregar, validar e aplicar as regras fundamentais
    """
    
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'system_prompt_core.json')
        self.system_config = None
        self.load_system_prompt()
        
    def load_system_prompt(self) -> bool:
        """
        Carrega o prompt de sistema do arquivo de configuração
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.system_config = json.load(f)
            
            logging.info("✅ System Prompt carregado com sucesso")
            return True
            
        except Exception as e:
            logging.error(f"❌ Erro ao carregar System Prompt: {e}")
            return False
    
    def get_mission_statement(self) -> str:
        """
        Retorna a declaração de missão fundamental
        """
        if not self.system_config:
            return "ERRO: System Prompt não carregado"
            
        return f"""
🎯 **MISSÃO CRÍTICA ATIVA**
{self.system_config['core_identity']['primary_objective']}

{self.system_config['mission_statement']}
        """
    
    def validate_action_against_rules(self, action_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida uma ação contra as regras do sistema
        """
        validation_result = {
            "allowed": True,
            "priority": "MEDIUM",
            "warnings": [],
            "required_checks": []
        }
        
        if not self.system_config:
            validation_result["allowed"] = False
            validation_result["warnings"].append("System Prompt não carregado")
            return validation_result
        
        # Regra 1: Prioridade Máxima - Cron Tasks
        if action_type == "cron_task":
            validation_result["priority"] = "CRITICAL"
            validation_result["required_checks"].append("Verificar próxima tarefa agendada")
        
        # Regra 2: Consulta Obrigatória à LTM
        if action_type in ["error_handling", "code_fix", "troubleshooting"]:
            validation_result["required_checks"].append("Consultar Memória de Longo Prazo (LTM)")
            validation_result["required_checks"].append("Buscar soluções históricas")
        
        # Regra 3: Restrição de Ação
        if action_type in ["optimization", "refactoring", "non_scheduled"]:
            if not context.get("queue_empty", False):
                validation_result["allowed"] = False
                validation_result["warnings"].append("Ação não permitida: fila 24/7 não está vazia")
        
        return validation_result
    
    def get_response_template(self) -> str:
        """
        Retorna o template obrigatório para respostas
        """
        if not self.system_config:
            return "ERRO: System Prompt não carregado"
            
        template = self.system_config['response_template']
        
        return f"""
{template['mandatory_start']}

📋 **CHECKLIST OBRIGATÓRIO:**
✅ Confirmação da missão
✅ Consulta à Memória de Longo Prazo (LTM)
✅ Ação tomada baseada na consulta
✅ Status da operação 24/7

⏰ **PRÓXIMAS TAREFAS AGENDADAS:**
{self._get_next_scheduled_tasks()}
        """
    
    def _get_next_scheduled_tasks(self) -> str:
        """
        Retorna as próximas tarefas agendadas
        """
        if not self.system_config:
            return "Erro ao carregar cronograma"
            
        schedule = self.system_config['schedule_priorities']
        current_time = datetime.now().strftime("%H:%M")
        
        tasks_info = []
        for account in schedule['accounts']:
            tasks_info.append(f"📱 {account}:")
            tasks_info.append(f"   FEED: {', '.join(schedule['feed_posts'])}")
            tasks_info.append(f"   STORIES: {', '.join(schedule['stories_posts'])}")
        
        return "\n".join(tasks_info)
    
    def check_emergency_protocol(self, error_type: str) -> Dict[str, Any]:
        """
        Verifica protocolos de emergência para tipos específicos de erro
        """
        if not self.system_config:
            return {"protocol": "ERRO: System Prompt não carregado"}
            
        protocols = self.system_config.get('emergency_protocols', {})
        
        return {
            "protocol": protocols.get(error_type, "Protocolo padrão: consultar LTM"),
            "priority": "CRITICAL",
            "immediate_action_required": True
        }
    
    def consultar_ltm_obrigatorio(self, error_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        REGRA 2: Consulta Obrigatória à LTM (Memória de Longo Prazo)
        Implementa a busca estruturada na Memória de Erros antes de qualquer nova solução
        """
        resultado_consulta = {
            "ltm_consultada": True,
            "solucao_historica_encontrada": False,
            "solucao_final_sucesso": None,
            "tentativas_anteriores": [],
            "recomendacao": "gerar_nova_solucao",
            "tempo_consulta": datetime.now().isoformat()
        }
        
        if not LTM_AVAILABLE:
            resultado_consulta["erro"] = "Sistema LTM não disponível"
            resultado_consulta["recomendacao"] = "proceder_com_cautela"
            return resultado_consulta
        
        try:
            # Gerar hash do erro para busca
            error_message = error_context.get('error_message', '')
            error_type = error_context.get('error_type', '')
            
            if not error_message and not error_type:
                resultado_consulta["erro"] = "Contexto de erro insuficiente"
                return resultado_consulta
            
            # Buscar soluções históricas
            error_hash = self._generate_error_hash(error_message, error_type)
            solucao_historica = error_reflection.get_successful_solution(error_hash)
            
            if solucao_historica:
                resultado_consulta["solucao_historica_encontrada"] = True
                resultado_consulta["solucao_final_sucesso"] = {
                    "descricao": solucao_historica.attempted_solution,
                    "fonte": solucao_historica.solution_source,
                    "timestamp": solucao_historica.timestamp,
                    "contexto": solucao_historica.context
                }
                resultado_consulta["recomendacao"] = "aplicar_solucao_historica"
                
                # Log da consulta bem-sucedida
                structured_logger.reflection_logger.info(
                    f"✅ LTM CONSULTA: Solução histórica encontrada para {error_hash}"
                )
            else:
                # Buscar tentativas anteriores que falharam
                tentativas = error_reflection.get_failed_attempts(error_hash)
                resultado_consulta["tentativas_anteriores"] = [
                    {
                        "solucao": t.attempted_solution,
                        "fonte": t.solution_source,
                        "timestamp": t.timestamp
                    } for t in tentativas
                ]
                
                structured_logger.reflection_logger.info(
                    f"⚠️ LTM CONSULTA: Nenhuma solução histórica para {error_hash}. "
                    f"Tentativas anteriores: {len(tentativas)}"
                )
        
        except Exception as e:
            resultado_consulta["erro"] = f"Erro na consulta LTM: {str(e)}"
            structured_logger.error_logger.error(f"Erro na consulta LTM: {e}")
        
        return resultado_consulta
    
    def _generate_error_hash(self, error_message: str, error_type: str) -> str:
        """
        Gera hash do erro para busca na LTM
        """
        import hashlib
        combined = f"{error_type}:{error_message}"
        return hashlib.md5(combined.encode()).hexdigest()[:16]
    
    def registrar_nova_solucao(self, error_context: Dict[str, Any], 
                              solucao: str, fonte: str, sucesso: bool) -> bool:
        """
        Registra uma nova solução na LTM após teste rigoroso
        """
        if not LTM_AVAILABLE:
            logging.warning("LTM não disponível para registro de solução")
            return False
        
        try:
            error_hash = self._generate_error_hash(
                error_context.get('error_message', ''),
                error_context.get('error_type', '')
            )
            
            attempt_id = error_reflection.register_solution_attempt(
                error_hash=error_hash,
                attempted_solution=solucao,
                solution_source=fonte,
                success=sucesso,
                context=error_context
            )
            
            if sucesso:
                structured_logger.reflection_logger.info(
                    f"✅ NOVA SOLUÇÃO REGISTRADA: {error_hash} - {solucao}"
                )
            else:
                structured_logger.reflection_logger.info(
                    f"❌ TENTATIVA FALHADA REGISTRADA: {error_hash} - {solucao}"
                )
            
            return True
            
        except Exception as e:
            structured_logger.error_logger.error(f"Erro ao registrar solução: {e}")
            return False
    
    def log_system_status(self):
        """
        Registra o status atual do sistema
        """
        status = {
            "timestamp": datetime.now().isoformat(),
            "system_prompt_loaded": self.system_config is not None,
            "mission_active": True,
            "rules_enforced": True
        }
        
        logging.info(f"🔄 TRAE IA System Status: {status}")
        return status

# Instância global do gerenciador
system_prompt_manager = SystemPromptManager()

def enforce_system_rules(action_type: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Função utilitária para aplicar as regras do sistema
    """
    if context is None:
        context = {}
        
    return system_prompt_manager.validate_action_against_rules(action_type, context)

def get_mission_reminder() -> str:
    """
    Função utilitária para obter lembrete da missão
    """
    return system_prompt_manager.get_mission_statement()

def check_ltm_consultation_required(action_type: str) -> bool:
    """
    Verifica se consulta à LTM é obrigatória para o tipo de ação
    """
    ltm_required_actions = ["error_handling", "code_fix", "troubleshooting", "api_failure"]
    return action_type in ltm_required_actions