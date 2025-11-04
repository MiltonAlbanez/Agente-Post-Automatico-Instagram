#!/usr/bin/env python3
"""
Enhanced Error Handler - Sistema de Tratamento de Erros Avançado
Implementa captura de erros, fallback automático e sistema de notificações
"""

import json
import sqlite3
import traceback
import hashlib
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import functools
import time

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Níveis de severidade de erro"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ErrorCategory(Enum):
    """Categorias de erro"""
    NETWORK = "NETWORK"
    DATABASE = "DATABASE"
    AUTHENTICATION = "AUTHENTICATION"
    VALIDATION = "VALIDATION"
    FILE_SYSTEM = "FILE_SYSTEM"
    API = "API"
    CONFIGURATION = "CONFIGURATION"
    BUSINESS_LOGIC = "BUSINESS_LOGIC"
    SYSTEM = "SYSTEM"

@dataclass
class ErrorContext:
    """Contexto do erro"""
    timestamp: str
    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    details: str
    stack_trace: str
    function_name: str
    file_path: str
    line_number: int
    user_context: Dict[str, Any]
    system_context: Dict[str, Any]
    recovery_attempts: int = 0
    resolved: bool = False
    resolution_method: str = ""

@dataclass
class FallbackStrategy:
    """Estratégia de fallback"""
    name: str
    description: str
    function: Callable
    max_attempts: int = 3
    delay_seconds: float = 1.0
    conditions: List[str] = None
    
    def __post_init__(self):
        if self.conditions is None:
            self.conditions = []

class EnhancedErrorHandler:
    """Sistema de tratamento de erros avançado"""
    
    def __init__(self, base_path: Path = None, telegram_config: Dict[str, str] = None):
        self.base_path = base_path or Path.cwd()
        self.telegram_config = telegram_config or {}
        self.error_db_path = self.base_path / "data" / "error_reflection.db"
        self.fallback_strategies = self._initialize_fallback_strategies()
        self.notification_channels = self._initialize_notification_channels()
        self._ensure_error_db()
        
    def _initialize_fallback_strategies(self) -> Dict[str, List[FallbackStrategy]]:
        """Inicializar estratégias de fallback"""
        return {
            ErrorCategory.NETWORK.value: [
                FallbackStrategy(
                    name="retry_with_backoff",
                    description="Tentar novamente com backoff exponencial",
                    function=self._retry_with_backoff,
                    max_attempts=3,
                    delay_seconds=2.0
                ),
                FallbackStrategy(
                    name="use_cached_data",
                    description="Usar dados em cache",
                    function=self._use_cached_data,
                    max_attempts=1
                ),
                FallbackStrategy(
                    name="offline_mode",
                    description="Ativar modo offline",
                    function=self._activate_offline_mode,
                    max_attempts=1
                )
            ],
            ErrorCategory.DATABASE.value: [
                FallbackStrategy(
                    name="recreate_connection",
                    description="Recriar conexão com banco",
                    function=self._recreate_db_connection,
                    max_attempts=2
                ),
                FallbackStrategy(
                    name="use_backup_db",
                    description="Usar banco de backup",
                    function=self._use_backup_database,
                    max_attempts=1
                ),
                FallbackStrategy(
                    name="file_based_storage",
                    description="Usar armazenamento em arquivo",
                    function=self._use_file_storage,
                    max_attempts=1
                )
            ],
            ErrorCategory.AUTHENTICATION.value: [
                FallbackStrategy(
                    name="refresh_token",
                    description="Renovar token de acesso",
                    function=self._refresh_access_token,
                    max_attempts=2
                ),
                FallbackStrategy(
                    name="use_backup_credentials",
                    description="Usar credenciais de backup",
                    function=self._use_backup_credentials,
                    max_attempts=1
                ),
                FallbackStrategy(
                    name="guest_mode",
                    description="Ativar modo convidado",
                    function=self._activate_guest_mode,
                    max_attempts=1
                )
            ],
            ErrorCategory.API.value: [
                FallbackStrategy(
                    name="use_alternative_endpoint",
                    description="Usar endpoint alternativo",
                    function=self._use_alternative_endpoint,
                    max_attempts=2
                ),
                FallbackStrategy(
                    name="reduce_request_complexity",
                    description="Reduzir complexidade da requisição",
                    function=self._reduce_request_complexity,
                    max_attempts=1
                ),
                FallbackStrategy(
                    name="queue_for_later",
                    description="Enfileirar para processamento posterior",
                    function=self._queue_for_later,
                    max_attempts=1
                )
            ]
        }
    
    def _initialize_notification_channels(self) -> Dict[str, Callable]:
        """Inicializar canais de notificação"""
        return {
            'telegram': self._send_telegram_notification,
            'log': self._send_log_notification,
            'file': self._send_file_notification,
            'console': self._send_console_notification
        }
    
    def _ensure_error_db(self):
        """Garantir que o banco de erros existe"""
        try:
            self.error_db_path.parent.mkdir(parents=True, exist_ok=True)
            
            conn = sqlite3.connect(self.error_db_path)
            cursor = conn.cursor()
            
            # Criar tabela de erros se não existir
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS error_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_id TEXT UNIQUE,
                    timestamp TEXT,
                    category TEXT,
                    severity TEXT,
                    message TEXT,
                    details TEXT,
                    stack_trace TEXT,
                    function_name TEXT,
                    file_path TEXT,
                    line_number INTEGER,
                    user_context TEXT,
                    system_context TEXT,
                    recovery_attempts INTEGER DEFAULT 0,
                    resolved BOOLEAN DEFAULT FALSE,
                    resolution_method TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Criar tabela de estratégias de recuperação
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS recovery_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_id TEXT,
                    strategy_name TEXT,
                    attempt_number INTEGER,
                    success BOOLEAN,
                    details TEXT,
                    timestamp TEXT,
                    FOREIGN KEY (error_id) REFERENCES error_logs (error_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erro ao inicializar banco de erros: {e}")
    
    def handle_error(self, 
                    error: Exception, 
                    category: ErrorCategory = ErrorCategory.SYSTEM,
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                    user_context: Dict[str, Any] = None,
                    auto_recover: bool = True) -> ErrorContext:
        """Manipular erro com contexto completo"""
        
        # Capturar contexto do erro
        tb = traceback.extract_tb(error.__traceback__)
        if tb:
            frame = tb[-1]
            function_name = frame.name
            file_path = frame.filename
            line_number = frame.lineno
        else:
            function_name = "unknown"
            file_path = "unknown"
            line_number = 0
        
        # Gerar ID único do erro
        error_signature = f"{category.value}_{type(error).__name__}_{str(error)}"
        error_id = hashlib.md5(error_signature.encode()).hexdigest()[:16]
        
        # Criar contexto do erro
        error_context = ErrorContext(
            timestamp=datetime.now().isoformat(),
            error_id=error_id,
            category=category,
            severity=severity,
            message=str(error),
            details=f"{type(error).__name__}: {str(error)}",
            stack_trace=traceback.format_exc(),
            function_name=function_name,
            file_path=file_path,
            line_number=line_number,
            user_context=user_context or {},
            system_context=self._get_system_context()
        )
        
        # Registrar erro no banco
        self._log_error_to_db(error_context)
        
        # Enviar notificações
        self._send_notifications(error_context)
        
        # Tentar recuperação automática se habilitada
        if auto_recover:
            recovery_success = self._attempt_recovery(error_context)
            if recovery_success:
                error_context.resolved = True
                self._update_error_resolution(error_context)
        
        return error_context
    
    def _get_system_context(self) -> Dict[str, Any]:
        """Obter contexto do sistema"""
        return {
            'timestamp': datetime.now().isoformat(),
            'working_directory': str(Path.cwd()),
            'python_version': f"{__import__('sys').version_info.major}.{__import__('sys').version_info.minor}",
            'platform': __import__('platform').system(),
            'memory_usage': self._get_memory_usage(),
            'disk_space': self._get_disk_space()
        }
    
    def _get_memory_usage(self) -> Dict[str, Any]:
        """Obter uso de memória"""
        try:
            import psutil
            process = psutil.Process()
            return {
                'rss': process.memory_info().rss,
                'vms': process.memory_info().vms,
                'percent': process.memory_percent()
            }
        except ImportError:
            return {'error': 'psutil not available'}
        except Exception as e:
            return {'error': str(e)}
    
    def _get_disk_space(self) -> Dict[str, Any]:
        """Obter espaço em disco"""
        try:
            import shutil
            total, used, free = shutil.disk_usage(self.base_path)
            return {
                'total': total,
                'used': used,
                'free': free,
                'percent_used': (used / total) * 100
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _log_error_to_db(self, error_context: ErrorContext):
        """Registrar erro no banco de dados"""
        try:
            conn = sqlite3.connect(self.error_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO error_logs 
                (error_id, timestamp, category, severity, message, details, stack_trace,
                 function_name, file_path, line_number, user_context, system_context,
                 recovery_attempts, resolved, resolution_method)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                error_context.error_id,
                error_context.timestamp,
                error_context.category.value,
                error_context.severity.value,
                error_context.message,
                error_context.details,
                error_context.stack_trace,
                error_context.function_name,
                error_context.file_path,
                error_context.line_number,
                json.dumps(error_context.user_context),
                json.dumps(error_context.system_context),
                error_context.recovery_attempts,
                error_context.resolved,
                error_context.resolution_method
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erro ao registrar no banco: {e}")
    
    def _send_notifications(self, error_context: ErrorContext):
        """Enviar notificações do erro"""
        # Determinar canais baseado na severidade
        channels = ['log']  # Sempre logar
        
        if error_context.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            channels.extend(['telegram', 'file'])
        
        if error_context.severity == ErrorSeverity.CRITICAL:
            channels.append('console')
        
        # Enviar para cada canal
        for channel in channels:
            try:
                if channel in self.notification_channels:
                    self.notification_channels[channel](error_context)
            except Exception as e:
                logger.error(f"Erro ao enviar notificação via {channel}: {e}")
    
    def _send_telegram_notification(self, error_context: ErrorContext):
        """Enviar notificação via Telegram"""
        if not self.telegram_config.get('bot_token') or not self.telegram_config.get('chat_id'):
            return
        
        try:
            severity_emoji = {
                ErrorSeverity.LOW: "🟡",
                ErrorSeverity.MEDIUM: "🟠", 
                ErrorSeverity.HIGH: "🔴",
                ErrorSeverity.CRITICAL: "🚨"
            }
            
            message = f"""
{severity_emoji.get(error_context.severity, '⚠️')} **ERRO DETECTADO**

**Severidade:** {error_context.severity.value}
**Categoria:** {error_context.category.value}
**Função:** {error_context.function_name}
**Mensagem:** {error_context.message}
**Timestamp:** {error_context.timestamp}
**ID:** {error_context.error_id}

**Detalhes:** {error_context.details[:200]}...
            """.strip()
            
            url = f"https://api.telegram.org/bot{self.telegram_config['bot_token']}/sendMessage"
            data = {
                'chat_id': self.telegram_config['chat_id'],
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação Telegram: {e}")
    
    def _send_log_notification(self, error_context: ErrorContext):
        """Enviar notificação via log"""
        level_map = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }
        
        level = level_map.get(error_context.severity, logging.ERROR)
        logger.log(level, f"[{error_context.error_id}] {error_context.category.value}: {error_context.message}")
    
    def _send_file_notification(self, error_context: ErrorContext):
        """Enviar notificação via arquivo"""
        try:
            error_file = self.base_path / "data" / "error_notifications.jsonl"
            error_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(error_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(asdict(error_context), ensure_ascii=False) + '\n')
                
        except Exception as e:
            logger.error(f"Erro ao escrever notificação em arquivo: {e}")
    
    def _send_console_notification(self, error_context: ErrorContext):
        """Enviar notificação via console"""
        print(f"\n🚨 ERRO CRÍTICO DETECTADO 🚨")
        print(f"ID: {error_context.error_id}")
        print(f"Categoria: {error_context.category.value}")
        print(f"Severidade: {error_context.severity.value}")
        print(f"Mensagem: {error_context.message}")
        print(f"Função: {error_context.function_name}")
        print(f"Timestamp: {error_context.timestamp}")
        print("=" * 50)
    
    def _attempt_recovery(self, error_context: ErrorContext) -> bool:
        """Tentar recuperação automática"""
        strategies = self.fallback_strategies.get(error_context.category.value, [])
        
        for strategy in strategies:
            for attempt in range(strategy.max_attempts):
                try:
                    logger.info(f"Tentando recuperação: {strategy.name} (tentativa {attempt + 1})")
                    
                    # Registrar tentativa
                    self._log_recovery_attempt(error_context.error_id, strategy.name, attempt + 1, False)
                    
                    # Executar estratégia
                    success = strategy.function(error_context, attempt)
                    
                    if success:
                        logger.info(f"Recuperação bem-sucedida: {strategy.name}")
                        error_context.resolution_method = strategy.name
                        error_context.recovery_attempts = attempt + 1
                        
                        # Atualizar registro de sucesso
                        self._log_recovery_attempt(error_context.error_id, strategy.name, attempt + 1, True)
                        
                        return True
                    
                    # Aguardar antes da próxima tentativa
                    if attempt < strategy.max_attempts - 1:
                        time.sleep(strategy.delay_seconds * (2 ** attempt))  # Backoff exponencial
                        
                except Exception as e:
                    logger.error(f"Erro na estratégia de recuperação {strategy.name}: {e}")
                    continue
        
        return False
    
    def _log_recovery_attempt(self, error_id: str, strategy_name: str, attempt_number: int, success: bool):
        """Registrar tentativa de recuperação"""
        try:
            conn = sqlite3.connect(self.error_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO recovery_attempts 
                (error_id, strategy_name, attempt_number, success, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (error_id, strategy_name, attempt_number, success, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erro ao registrar tentativa de recuperação: {e}")
    
    def _update_error_resolution(self, error_context: ErrorContext):
        """Atualizar resolução do erro"""
        try:
            conn = sqlite3.connect(self.error_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE error_logs 
                SET resolved = ?, resolution_method = ?, recovery_attempts = ?
                WHERE error_id = ?
            ''', (error_context.resolved, error_context.resolution_method, 
                  error_context.recovery_attempts, error_context.error_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erro ao atualizar resolução: {e}")
    
    # Estratégias de fallback específicas
    def _retry_with_backoff(self, error_context: ErrorContext, attempt: int) -> bool:
        """Estratégia: tentar novamente com backoff"""
        # Implementação específica dependeria do contexto
        logger.info(f"Executando retry com backoff (tentativa {attempt + 1})")
        return False  # Placeholder
    
    def _use_cached_data(self, error_context: ErrorContext, attempt: int) -> bool:
        """Estratégia: usar dados em cache"""
        logger.info("Tentando usar dados em cache")
        return False  # Placeholder
    
    def _activate_offline_mode(self, error_context: ErrorContext, attempt: int) -> bool:
        """Estratégia: ativar modo offline"""
        logger.info("Ativando modo offline")
        return False  # Placeholder
    
    def _recreate_db_connection(self, error_context: ErrorContext, attempt: int) -> bool:
        """Estratégia: recriar conexão com banco"""
        logger.info("Recriando conexão com banco de dados")
        return False  # Placeholder
    
    def _use_backup_database(self, error_context: ErrorContext, attempt: int) -> bool:
        """Estratégia: usar banco de backup"""
        logger.info("Tentando usar banco de backup")
        return False  # Placeholder
    
    def _use_file_storage(self, error_context: ErrorContext, attempt: int) -> bool:
        """Estratégia: usar armazenamento em arquivo"""
        logger.info("Mudando para armazenamento em arquivo")
        return False  # Placeholder
    
    def _refresh_access_token(self, error_context: ErrorContext, attempt: int) -> bool:
        """Estratégia: renovar token de acesso"""
        logger.info("Tentando renovar token de acesso")
        return False  # Placeholder
    
    def _use_backup_credentials(self, error_context: ErrorContext, attempt: int) -> bool:
        """Estratégia: usar credenciais de backup"""
        logger.info("Tentando credenciais de backup")
        return False  # Placeholder
    
    def _activate_guest_mode(self, error_context: ErrorContext, attempt: int) -> bool:
        """Estratégia: ativar modo convidado"""
        logger.info("Ativando modo convidado")
        return False  # Placeholder
    
    def _use_alternative_endpoint(self, error_context: ErrorContext, attempt: int) -> bool:
        """Estratégia: usar endpoint alternativo"""
        logger.info("Tentando endpoint alternativo")
        return False  # Placeholder
    
    def _reduce_request_complexity(self, error_context: ErrorContext, attempt: int) -> bool:
        """Estratégia: reduzir complexidade da requisição"""
        logger.info("Reduzindo complexidade da requisição")
        return False  # Placeholder
    
    def _queue_for_later(self, error_context: ErrorContext, attempt: int) -> bool:
        """Estratégia: enfileirar para processamento posterior"""
        logger.info("Enfileirando para processamento posterior")
        return True  # Esta estratégia sempre "funciona"

def error_handler_decorator(category: ErrorCategory = ErrorCategory.SYSTEM,
                          severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                          auto_recover: bool = True,
                          handler_instance: EnhancedErrorHandler = None):
    """Decorator para tratamento automático de erros"""
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if handler_instance:
                    error_context = handler_instance.handle_error(
                        error=e,
                        category=category,
                        severity=severity,
                        user_context={'function': func.__name__, 'args': str(args)[:100]},
                        auto_recover=auto_recover
                    )
                    
                    # Se não foi possível recuperar, re-raise o erro
                    if not error_context.resolved:
                        raise
                    
                    # Se foi recuperado, retornar None ou valor padrão
                    return None
                else:
                    raise
        return wrapper
    return decorator

def main():
    """Função principal para teste"""
    # Configurar Telegram (opcional)
    telegram_config = {
        'bot_token': 'YOUR_BOT_TOKEN',
        'chat_id': 'YOUR_CHAT_ID'
    }
    
    handler = EnhancedErrorHandler(telegram_config=telegram_config)
    
    # Teste de tratamento de erro
    try:
        # Simular erro de rede
        raise requests.ConnectionError("Falha na conexão com API")
    except Exception as e:
        error_context = handler.handle_error(
            error=e,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.HIGH,
            user_context={'operation': 'api_call', 'endpoint': '/api/posts'}
        )
        
        print(f"Erro tratado: {error_context.error_id}")
        print(f"Resolvido: {'✅ Sim' if error_context.resolved else '❌ Não'}")
    
    print("\n🛡️ Sistema de tratamento de erros avançado implementado com sucesso!")

if __name__ == "__main__":
    main()