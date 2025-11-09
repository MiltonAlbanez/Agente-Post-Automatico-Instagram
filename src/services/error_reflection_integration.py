"""
Integração do Sistema de Reflexão de Erros no Pipeline Principal
Fornece decorators e wrappers para integração transparente.
"""

import functools
import traceback
from typing import Callable, Any, Dict, Optional, List
from datetime import datetime
import inspect

from .error_reflection_manager import error_reflection
from .structured_error_logger import structured_logger
from .solution_strategy_manager import solution_strategy_manager


class ErrorReflectionIntegration:
    """
    Classe principal para integração do sistema de reflexão de erros.
    """
    
    def __init__(self):
        self.active_errors = {}  # Rastreia erros ativos por função
        self.function_stats = {}  # Estatísticas por função
    
    def smart_error_handler(self, 
                          function_name: str = None,
                          auto_generate_plan: bool = True,
                          critical: bool = False,
                          retry_attempts: int = 0,
                          fallback_function: Callable = None):
        """
        Decorator inteligente para tratamento de erros com reflexão automática.
        
        Args:
            function_name: Nome customizado da função
            auto_generate_plan: Se deve gerar plano de solução automaticamente
            critical: Se é uma função crítica (gera alertas especiais)
            retry_attempts: Número de tentativas automáticas
            fallback_function: Função de fallback em caso de falha
        
        Usage:
            @error_reflection.smart_error_handler(critical=True, retry_attempts=2)
            def upload_media(file_path):
                # código que pode falhar
                pass
        """
        def decorator(func: Callable) -> Callable:
            func_name = function_name or func.__name__
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Inicializa estatísticas da função se necessário
                if func_name not in self.function_stats:
                    self.function_stats[func_name] = {
                        'total_calls': 0,
                        'successful_calls': 0,
                        'failed_calls': 0,
                        'last_error_hash': None,
                        'retry_count': 0
                    }
                
                stats = self.function_stats[func_name]
                stats['total_calls'] += 1
                
                # Contexto para logging
                context = {
                    'function_name': func_name,
                    'args_signature': self._get_args_signature(func, args, kwargs),
                    'critical': critical,
                    'call_count': stats['total_calls']
                }
                
                last_error = None
                
                # Loop de retry
                for attempt in range(retry_attempts + 1):
                    try:
                        with structured_logger.error_context(**context):
                            result = func(*args, **kwargs)
                            
                        stats['successful_calls'] += 1
                        
                        # Se teve sucesso após retry, registra a recuperação
                        if attempt > 0 and last_error:
                            self._log_recovery_success(last_error, attempt, func_name)
                        
                        return result
                        
                    except Exception as e:
                        last_error = e
                        stats['failed_calls'] += 1
                        
                        # Registra o erro
                        error_hash = structured_logger.log_error(
                            error=e,
                            context=context,
                            function_name=func_name,
                            auto_reflect=False  # Controlamos a reflexão manualmente
                        )
                        
                        stats['last_error_hash'] = error_hash
                        
                        # Se não é a última tentativa, continua o retry
                        if attempt < retry_attempts:
                            stats['retry_count'] += 1
                            
                            # Registra tentativa de retry
                            structured_logger.log_solution_attempt(
                                error_hash=error_hash,
                                solution_description=f"Retry automático (tentativa {attempt + 1})",
                                solution_source="automatic_retry",
                                success=False
                            )
                            
                            # Delay progressivo entre tentativas
                            import time
                            delay = 2 ** attempt  # Backoff exponencial
                            time.sleep(delay)
                            continue
                        
                        # Última tentativa falhou - processa erro completo
                        self._process_final_error(
                            error_hash, e, func_name, critical, 
                            auto_generate_plan, fallback_function,
                            args, kwargs
                        )
                        
                        # Se tem fallback, tenta executar
                        if fallback_function:
                            try:
                                result = fallback_function(*args, **kwargs)
                                
                                # Registra sucesso do fallback
                                structured_logger.log_solution_attempt(
                                    error_hash=error_hash,
                                    solution_description=f"Fallback function: {fallback_function.__name__}",
                                    solution_source="fallback",
                                    success=True
                                )
                                
                                return result
                                
                            except Exception as fallback_error:
                                # Fallback também falhou
                                structured_logger.log_error(
                                    error=fallback_error,
                                    context={'original_error_hash': error_hash, 'fallback_failed': True},
                                    function_name=f"{func_name}_fallback"
                                )
                        
                        # Re-levanta o erro original
                        raise e
            
            return wrapper
        return decorator
    
    def _get_args_signature(self, func: Callable, args: tuple, kwargs: dict) -> str:
        """Gera assinatura legível dos argumentos."""
        try:
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Converte para string, limitando tamanho de valores grandes
            args_str = []
            for name, value in bound_args.arguments.items():
                value_str = str(value)
                if len(value_str) > 100:
                    value_str = value_str[:97] + "..."
                args_str.append(f"{name}={value_str}")
            
            return ", ".join(args_str)
        except Exception:
            return f"args={len(args)}, kwargs={list(kwargs.keys())}"
    
    def _log_recovery_success(self, error: Exception, attempt: int, func_name: str):
        """Registra recuperação bem-sucedida após retry."""
        structured_logger.reflection_logger.info(
            f"RECUPERAÇÃO BEM-SUCEDIDA: {func_name} se recuperou após {attempt} tentativas"
        )
        structured_logger.reflection_logger.info(f"Erro original: {type(error).__name__}: {str(error)}")
    
    def _process_final_error(self, 
                           error_hash: str, 
                           error: Exception, 
                           func_name: str,
                           critical: bool,
                           auto_generate_plan: bool,
                           fallback_function: Callable,
                           args: tuple,
                           kwargs: dict):
        """Processa erro final após todas as tentativas."""
        
        # Gera reflexão detalhada
        reflection_report = error_reflection.generate_reflection_report(error_hash)
        structured_logger.reflection_logger.info(reflection_report)
        
        # Se é crítico, gera alerta especial
        if critical:
            self._generate_critical_error_alert(error_hash, error, func_name)
        
        # Gera plano de solução se solicitado
        if auto_generate_plan:
            solution_plan = solution_strategy_manager.generate_solution_plan(error_hash)
            self._log_solution_plan(solution_plan)
        
        # Atualiza estatísticas globais
        self._update_global_stats(error_hash, func_name, critical)
    
    def _generate_critical_error_alert(self, error_hash: str, error: Exception, func_name: str):
        """Gera alerta para erros críticos."""
        alert_message = f"""
        🚨 ERRO CRÍTICO DETECTADO 🚨
        
        Função: {func_name}
        Erro: {type(error).__name__}: {str(error)}
        Hash: {error_hash}
        Timestamp: {datetime.now().isoformat()}
        
        Este erro ocorreu em uma função marcada como crítica.
        Ação imediata pode ser necessária.
        """
        
        structured_logger.error_logger.critical(alert_message)
        
        # Aqui poderia integrar com sistemas de alerta (Slack, email, etc.)
        print("=" * 60)
        print("🚨 ERRO CRÍTICO DETECTADO 🚨")
        print(f"Função: {func_name}")
        print(f"Erro: {type(error).__name__}: {str(error)}")
        print(f"Hash: {error_hash}")
        print("=" * 60)
    
    def _log_solution_plan(self, solution_plan: Dict[str, Any]):
        """Registra plano de solução gerado."""
        structured_logger.reflection_logger.info("=" * 60)
        structured_logger.reflection_logger.info("PLANO DE SOLUÇÃO GERADO AUTOMATICAMENTE")
        structured_logger.reflection_logger.info("=" * 60)
        
        structured_logger.reflection_logger.info(f"Error Hash: {solution_plan['error_hash']}")
        structured_logger.reflection_logger.info(f"Tempo estimado: {solution_plan['estimated_time']} minutos")
        
        structured_logger.reflection_logger.info("\nESTRATÉGIAS RECOMENDADAS:")
        for strategy in solution_plan['recommended_strategies']:
            structured_logger.reflection_logger.info(
                f"  {strategy['step']}. {strategy['description']} "
                f"(Prioridade: {strategy['priority']}, "
                f"Tempo: {strategy['estimated_time_minutes']}min)"
            )
        
        structured_logger.reflection_logger.info("\nORDEM DE EXECUÇÃO:")
        for step in solution_plan['execution_order']:
            structured_logger.reflection_logger.info(f"  • {step}")
        
        structured_logger.reflection_logger.info("=" * 60)
    
    def _update_global_stats(self, error_hash: str, func_name: str, critical: bool):
        """Atualiza estatísticas globais do sistema."""
        # Aqui poderia atualizar métricas em tempo real
        pass
    
    def get_function_health_report(self, func_name: str = None) -> Dict[str, Any]:
        """
        Gera relatório de saúde das funções monitoradas.
        
        Args:
            func_name: Nome específico da função (opcional)
        
        Returns:
            Relatório de saúde
        """
        if func_name and func_name in self.function_stats:
            stats = self.function_stats[func_name]
            success_rate = (stats['successful_calls'] / stats['total_calls'] * 100) if stats['total_calls'] > 0 else 0
            
            return {
                'function_name': func_name,
                'total_calls': stats['total_calls'],
                'successful_calls': stats['successful_calls'],
                'failed_calls': stats['failed_calls'],
                'success_rate': round(success_rate, 2),
                'retry_count': stats['retry_count'],
                'last_error_hash': stats['last_error_hash'],
                'health_status': self._calculate_health_status(success_rate, stats['failed_calls'])
            }
        
        # Relatório geral de todas as funções
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_functions': len(self.function_stats),
            'functions': {}
        }
        
        for func_name, stats in self.function_stats.items():
            success_rate = (stats['successful_calls'] / stats['total_calls'] * 100) if stats['total_calls'] > 0 else 0
            
            report['functions'][func_name] = {
                'total_calls': stats['total_calls'],
                'success_rate': round(success_rate, 2),
                'failed_calls': stats['failed_calls'],
                'health_status': self._calculate_health_status(success_rate, stats['failed_calls'])
            }
        
        return report
    
    def _calculate_health_status(self, success_rate: float, failed_calls: int) -> str:
        """Calcula status de saúde baseado em métricas."""
        if success_rate >= 95 and failed_calls <= 2:
            return "EXCELENTE"
        elif success_rate >= 85 and failed_calls <= 5:
            return "BOM"
        elif success_rate >= 70 and failed_calls <= 10:
            return "REGULAR"
        elif success_rate >= 50:
            return "RUIM"
        else:
            return "CRÍTICO"
    
    def manual_error_analysis(self, error_hash: str) -> Dict[str, Any]:
        """
        Executa análise manual detalhada de um erro específico.
        
        Args:
            error_hash: Hash do erro para análise
        
        Returns:
            Análise detalhada com recomendações
        """
        # Obtém análise do contexto
        context_analysis = error_reflection.analyze_error_context(error_hash)
        
        # Obtém estratégias de solução
        strategies = solution_strategy_manager.get_solution_strategies(error_hash)
        
        # Gera plano completo
        solution_plan = solution_strategy_manager.generate_solution_plan(error_hash)
        
        # Análise de tentativas falhadas
        failed_analysis = solution_strategy_manager.analyze_failed_attempts(error_hash)
        
        return {
            'error_hash': error_hash,
            'analysis_timestamp': datetime.now().isoformat(),
            'context_analysis': context_analysis,
            'failed_attempts_analysis': failed_analysis,
            'recommended_strategies': [
                {
                    'source_type': s.source_type,
                    'priority': s.priority,
                    'description': s.description,
                    'search_terms': s.search_terms
                }
                for s in strategies
            ],
            'complete_solution_plan': solution_plan,
            'next_steps': self._generate_next_steps(context_analysis, strategies),
            'risk_assessment': self._assess_error_risk(context_analysis, failed_analysis)
        }
    
    def _generate_next_steps(self, 
                           context_analysis: Dict[str, Any], 
                           strategies: List) -> List[str]:
        """Gera próximos passos recomendados."""
        steps = []
        
        if context_analysis.get('has_successful_solution'):
            steps.append("1. Aplicar solução conhecida que já funcionou anteriormente")
            steps.append("2. Verificar se contexto atual é similar ao da solução anterior")
        else:
            if strategies:
                top_strategy = strategies[0]
                steps.append(f"1. Executar estratégia prioritária: {top_strategy.description}")
                steps.append(f"2. Buscar por: {', '.join(top_strategy.search_terms[:3])}")
            
            steps.append("3. Documentar tentativa de solução para aprendizado futuro")
        
        steps.append("4. Monitorar se solução resolve problema definitivamente")
        
        return steps
    
    def _assess_error_risk(self, 
                         context_analysis: Dict[str, Any], 
                         failed_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Avalia risco associado ao erro."""
        risk_level = "BAIXO"
        risk_factors = []
        
        # Fatores de risco
        occurrence_count = context_analysis.get('occurrence_count', 0)
        failed_attempts = failed_analysis.get('total_attempts', 0)
        
        if occurrence_count > 5:
            risk_factors.append("Erro recorrente (>5 ocorrências)")
            risk_level = "MÉDIO"
        
        if failed_attempts > 3:
            risk_factors.append("Múltiplas tentativas de correção falharam")
            risk_level = "ALTO"
        
        if occurrence_count > 10 and failed_attempts > 5:
            risk_level = "CRÍTICO"
            risk_factors.append("Padrão de erro persistente e resistente a correções")
        
        return {
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'occurrence_count': occurrence_count,
            'failed_attempts': failed_attempts,
            'recommendation': self._get_risk_recommendation(risk_level)
        }
    
    def _get_risk_recommendation(self, risk_level: str) -> str:
        """Retorna recomendação baseada no nível de risco."""
        recommendations = {
            'BAIXO': 'Monitorar e aplicar correção padrão',
            'MÉDIO': 'Priorizar correção e implementar monitoramento adicional',
            'ALTO': 'Correção urgente necessária - considerar refatoração',
            'CRÍTICO': 'Ação imediata obrigatória - pode impactar sistema inteiro'
        }
        
        return recommendations.get(risk_level, 'Avaliar manualmente')


# Instância global para uso em todo o sistema
error_reflection_integration = ErrorReflectionIntegration()


# Aliases para facilitar uso
smart_error_handler = error_reflection_integration.smart_error_handler
get_function_health = error_reflection_integration.get_function_health_report
analyze_error = error_reflection_integration.manual_error_analysis


# Decorator simplificado para uso comum
def with_error_reflection(critical: bool = False, retry_attempts: int = 0):
    """
    Decorator simplificado para adicionar reflexão de erros.
    
    Usage:
        @with_error_reflection(critical=True)
        def important_function():
            pass
    """
    return smart_error_handler(critical=critical, retry_attempts=retry_attempts)


# Context manager para análise de blocos de código
class error_reflection_context:
    """
    Context manager para análise de erros em blocos de código.
    
    Usage:
        with error_reflection_context("upload_process") as ctx:
            # código que pode gerar erro
            upload_file()
    """
    
    def __init__(self, operation_name: str, critical: bool = False):
        self.operation_name = operation_name
        self.critical = critical
        self.start_time = None
        self.error_hash = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        structured_logger.reflection_logger.info(f"Iniciando operação: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is None:
            # Sucesso
            structured_logger.reflection_logger.info(
                f"Operação '{self.operation_name}' concluída com sucesso em {duration:.2f}s"
            )
        else:
            # Erro
            self.error_hash = structured_logger.log_error(
                error=exc_val,
                context={'operation': self.operation_name, 'duration': duration},
                function_name=self.operation_name
            )
            
            if self.critical:
                error_reflection_integration._generate_critical_error_alert(
                    self.error_hash, exc_val, self.operation_name
                )
        
        return False  # Não suprime exceções