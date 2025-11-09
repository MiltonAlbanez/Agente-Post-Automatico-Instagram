"""
Sistema de Logging Estruturado de Erros
Integra com ErrorReflectionManager para captura automática e categorização de erros.
"""

import logging
import json
import sys
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from contextlib import contextmanager
from functools import wraps

from .error_reflection_manager import error_reflection


class StructuredErrorLogger:
    """
    Logger estruturado que automaticamente integra com o sistema de reflexão de erros.
    """
    
    def __init__(self, name: str = "structured_error", log_dir: str = "data/logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Configuração de loggers
        self.error_logger = self._setup_error_logger()
        self.reflection_logger = self._setup_reflection_logger()
        self.performance_logger = self._setup_performance_logger()
        
        # Contexto atual para rastreamento
        self.current_context = {}
        
        # Categorias de erro para classificação automática
        self.error_categories = {
            'api': ['ConnectionError', 'HTTPError', 'RequestException', 'Timeout'],
            'database': ['DatabaseError', 'IntegrityError', 'OperationalError'],
            'file_system': ['FileNotFoundError', 'PermissionError', 'IOError'],
            'authentication': ['AuthenticationError', 'PermissionDenied', '403', 'Unauthorized'],
            'validation': ['ValidationError', 'ValueError', 'TypeError'],
            'network': ['NetworkError', 'DNSError', 'SSLError'],
            'instagram': ['InstagramError', 'RateLimitError', 'MediaUploadError'],
            'rapidapi': ['RapidAPIError', 'QuotaExceeded', '403 Forbidden']
        }
    
    def _setup_error_logger(self) -> logging.Logger:
        """Configura logger para erros estruturados."""
        logger = logging.getLogger(f"{self.name}_errors")
        logger.setLevel(logging.ERROR)
        
        if not logger.handlers:
            # Handler para arquivo JSON estruturado
            json_handler = logging.FileHandler(self.log_dir / "structured_errors.jsonl")
            json_handler.setFormatter(self._get_json_formatter())
            logger.addHandler(json_handler)
            
            # Handler para arquivo de texto legível
            text_handler = logging.FileHandler(self.log_dir / "errors.log")
            text_handler.setFormatter(self._get_text_formatter())
            logger.addHandler(text_handler)
        
        return logger
    
    def _setup_reflection_logger(self) -> logging.Logger:
        """Configura logger para relatórios de reflexão."""
        logger = logging.getLogger(f"{self.name}_reflection")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.FileHandler(self.log_dir / "error_reflection.log")
            handler.setFormatter(self._get_text_formatter())
            logger.addHandler(handler)
        
        return logger
    
    def _setup_performance_logger(self) -> logging.Logger:
        """Configura logger para métricas de performance."""
        logger = logging.getLogger(f"{self.name}_performance")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.FileHandler(self.log_dir / "performance.jsonl")
            handler.setFormatter(self._get_json_formatter())
            logger.addHandler(handler)
        
        return logger
    
    def _get_json_formatter(self) -> logging.Formatter:
        """Formatter para logs em formato JSON."""
        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                    'level': record.levelname,
                    'logger': record.name,
                    'message': record.getMessage(),
                }
                
                # Adiciona dados extras se disponíveis
                if hasattr(record, 'extra_data'):
                    log_entry.update(record.extra_data)
                
                return json.dumps(log_entry, ensure_ascii=False)
        
        return JSONFormatter()
    
    def _get_text_formatter(self) -> logging.Formatter:
        """Formatter para logs em formato texto."""
        return logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def categorize_error(self, error: Exception) -> str:
        """Categoriza automaticamente um erro baseado no tipo e mensagem."""
        error_type = type(error).__name__
        error_message = str(error).lower()
        
        for category, patterns in self.error_categories.items():
            for pattern in patterns:
                if pattern.lower() in error_type.lower() or pattern.lower() in error_message:
                    return category
        
        return 'unknown'
    
    def extract_error_context(self, error: Exception) -> Dict[str, Any]:
        """Extrai contexto detalhado de um erro."""
        context = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'error_category': self.categorize_error(error),
            'stack_trace': traceback.format_exc(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Adiciona contexto atual se disponível
        context.update(self.current_context)
        
        # Extrai informações específicas baseadas no tipo de erro
        if hasattr(error, 'response'):
            # Erros de HTTP/API
            response = error.response
            context.update({
                'status_code': getattr(response, 'status_code', None),
                'response_headers': dict(getattr(response, 'headers', {})),
                'response_text': getattr(response, 'text', '')[:500]  # Limita tamanho
            })
        
        if hasattr(error, 'errno'):
            # Erros de sistema/arquivo
            context['errno'] = error.errno
        
        # Informações do sistema
        context.update({
            'python_version': sys.version,
            'platform': sys.platform
        })
        
        return context
    
    def log_error(self, 
                  error: Exception, 
                  context: Dict[str, Any] = None,
                  function_name: str = None,
                  auto_reflect: bool = True) -> str:
        """
        Registra um erro de forma estruturada.
        
        Args:
            error: Exceção capturada
            context: Contexto adicional
            function_name: Nome da função onde ocorreu o erro
            auto_reflect: Se deve automaticamente gerar reflexão
        
        Returns:
            error_hash: Hash único do erro
        """
        # Extrai contexto completo
        full_context = self.extract_error_context(error)
        if context:
            full_context.update(context)
        
        if function_name:
            full_context['function_name'] = function_name
        
        # Registra no sistema de reflexão
        error_hash = error_reflection.register_error(
            error=error,
            context=full_context,
            function_name=function_name
        )
        
        full_context['error_hash'] = error_hash
        
        # Log estruturado
        self.error_logger.error(
            f"[{error_hash}] {type(error).__name__}: {str(error)}",
            extra={'extra_data': full_context}
        )
        
        # Gera reflexão automática se solicitado
        if auto_reflect:
            self.generate_reflection_log(error_hash)
        
        return error_hash
    
    def log_solution_attempt(self,
                           error_hash: str,
                           solution_description: str,
                           solution_source: str,
                           success: bool,
                           execution_time: float = None,
                           additional_context: Dict[str, Any] = None) -> int:
        """
        Registra uma tentativa de solução.
        
        Args:
            error_hash: Hash do erro
            solution_description: Descrição da solução tentada
            solution_source: Fonte da solução
            success: Se foi bem-sucedida
            execution_time: Tempo de execução em segundos
            additional_context: Contexto adicional
        
        Returns:
            attempt_id: ID da tentativa
        """
        context = additional_context or {}
        
        if execution_time is not None:
            context['execution_time'] = execution_time
        
        # Registra no sistema de reflexão
        attempt_id = error_reflection.register_solution_attempt(
            error_hash=error_hash,
            attempted_solution=solution_description,
            solution_source=solution_source,
            success=success,
            context=context
        )
        
        # Log da tentativa
        status = "SUCESSO" if success else "FALHA"
        self.reflection_logger.info(
            f"[{error_hash}] Tentativa {attempt_id}: {solution_source} - {status}"
        )
        self.reflection_logger.info(f"Solução: {solution_description}")
        
        if execution_time:
            self.performance_logger.info(
                "Solution attempt performance",
                extra={'extra_data': {
                    'error_hash': error_hash,
                    'attempt_id': attempt_id,
                    'execution_time': execution_time,
                    'success': success,
                    'solution_source': solution_source
                }}
            )
        
        return attempt_id
    
    def generate_reflection_log(self, error_hash: str):
        """Gera e registra relatório de reflexão para um erro."""
        reflection_report = error_reflection.generate_reflection_report(error_hash)
        
        self.reflection_logger.info("=" * 80)
        self.reflection_logger.info("NOVO RELATÓRIO DE REFLEXÃO GERADO")
        self.reflection_logger.info("=" * 80)
        
        for line in reflection_report.split('\n'):
            self.reflection_logger.info(line)
        
        self.reflection_logger.info("=" * 80)
    
    @contextmanager
    def error_context(self, **context_data):
        """
        Context manager para adicionar contexto temporário aos logs.
        
        Usage:
            with logger.error_context(function="upload_media", account="test"):
                # código que pode gerar erro
                pass
        """
        old_context = self.current_context.copy()
        self.current_context.update(context_data)
        
        try:
            yield
        finally:
            self.current_context = old_context
    
    def log_performance_metric(self, 
                             metric_name: str, 
                             value: float, 
                             unit: str = "seconds",
                             context: Dict[str, Any] = None):
        """Registra métrica de performance."""
        metric_data = {
            'metric_name': metric_name,
            'value': value,
            'unit': unit,
            'timestamp': datetime.now().isoformat()
        }
        
        if context:
            metric_data.update(context)
        
        self.performance_logger.info(
            f"Performance metric: {metric_name} = {value} {unit}",
            extra={'extra_data': metric_data}
        )
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Retorna resumo de erros das últimas N horas."""
        # Esta função poderia ser expandida para ler os logs JSON
        # e gerar estatísticas em tempo real
        stats = error_reflection.get_error_statistics()
        
        return {
            'period_hours': hours,
            'timestamp': datetime.now().isoformat(),
            'reflection_stats': stats,
            'log_files': {
                'errors': str(self.log_dir / "structured_errors.jsonl"),
                'reflection': str(self.log_dir / "error_reflection.log"),
                'performance': str(self.log_dir / "performance.jsonl")
            }
        }


# Instância global
structured_logger = StructuredErrorLogger()


def log_errors(function_name: str = None, auto_reflect: bool = True):
    """
    Decorator para logging automático de erros.
    
    Args:
        function_name: Nome customizado da função (opcional)
        auto_reflect: Se deve gerar reflexão automática
    
    Usage:
        @log_errors()
        def my_function():
            # código que pode gerar erro
            pass
        
        @log_errors(function_name="custom_name", auto_reflect=False)
        def another_function():
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = function_name or func.__name__
            
            with structured_logger.error_context(
                function=func_name,
                args_count=len(args),
                kwargs_keys=list(kwargs.keys())
            ):
                try:
                    start_time = datetime.now()
                    result = func(*args, **kwargs)
                    
                    # Log de performance para funções bem-sucedidas
                    execution_time = (datetime.now() - start_time).total_seconds()
                    if execution_time > 1.0:  # Log apenas se demorar mais de 1 segundo
                        structured_logger.log_performance_metric(
                            metric_name=f"function_execution_{func_name}",
                            value=execution_time,
                            context={'success': True}
                        )
                    
                    return result
                    
                except Exception as e:
                    # Log do erro
                    error_hash = structured_logger.log_error(
                        error=e,
                        function_name=func_name,
                        auto_reflect=auto_reflect
                    )
                    
                    # Re-levanta o erro para tratamento normal
                    raise e
        
        return wrapper
    return decorator


def track_solution_attempt(error_hash: str, 
                         solution_source: str,
                         auto_log: bool = True):
    """
    Decorator para rastrear tentativas de solução.
    
    Usage:
        @track_solution_attempt("abc123", "documentation")
        def try_fix_error():
            # código da tentativa de correção
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            success = False
            
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                success = False
                raise e
            finally:
                if auto_log:
                    execution_time = (datetime.now() - start_time).total_seconds()
                    
                    structured_logger.log_solution_attempt(
                        error_hash=error_hash,
                        solution_description=f"Execução da função {func.__name__}",
                        solution_source=solution_source,
                        success=success,
                        execution_time=execution_time
                    )
        
        return wrapper
    return decorator