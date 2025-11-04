"""
Sistema de Reflexão e Prevenção de Erros
Implementa um ciclo de aprendizagem contínua para evitar repetição de falhas.
"""

import json
import sqlite3
import hashlib
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import logging


@dataclass
class ErrorAttempt:
    """Representa uma tentativa de correção de erro."""
    timestamp: str
    error_type: str
    error_message: str
    stack_trace: str
    attempted_solution: str
    solution_source: str  # 'documentation', 'codebase', 'web_search', 'manual'
    success: bool
    context: Dict[str, Any]


@dataclass
class ErrorPattern:
    """Padrão de erro identificado."""
    error_hash: str
    error_type: str
    common_message: str
    occurrence_count: int
    failed_attempts: List[ErrorAttempt]
    successful_solution: Optional[ErrorAttempt]
    last_occurrence: str
    prevention_strategy: Optional[str]


class ErrorReflectionManager:
    """
    Gerenciador de Reflexão e Prevenção de Erros.
    
    Implementa um sistema de memória de erros que:
    1. Registra todos os erros e tentativas de correção
    2. Identifica padrões de erros recorrentes
    3. Previne repetição de soluções que já falharam
    4. Sugere estratégias baseadas em conhecimento acumulado
    """
    
    def __init__(self, db_path: str = "data/error_reflection.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
        self.logger = self._setup_logger()
        
        # Cache de padrões de erro em memória
        self._error_patterns_cache: Dict[str, ErrorPattern] = {}
        self._load_error_patterns()
    
    def _setup_logger(self) -> logging.Logger:
        """Configura logger específico para reflexão de erros."""
        logger = logging.getLogger('error_reflection')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.FileHandler('data/error_reflection.log')
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _init_database(self):
        """Inicializa o banco de dados de reflexão de erros."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS error_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_hash TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    error_type TEXT NOT NULL,
                    error_message TEXT NOT NULL,
                    stack_trace TEXT,
                    attempted_solution TEXT NOT NULL,
                    solution_source TEXT NOT NULL,
                    success BOOLEAN NOT NULL,
                    context TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS error_patterns (
                    error_hash TEXT PRIMARY KEY,
                    error_type TEXT NOT NULL,
                    common_message TEXT NOT NULL,
                    occurrence_count INTEGER DEFAULT 1,
                    last_occurrence TEXT NOT NULL,
                    prevention_strategy TEXT,
                    successful_solution_id INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (successful_solution_id) REFERENCES error_attempts(id)
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_error_hash ON error_attempts(error_hash)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON error_attempts(timestamp)
            """)
    
    def _generate_error_hash(self, error_type: str, error_message: str) -> str:
        """Gera hash único para identificar padrões de erro."""
        # Normaliza a mensagem removendo detalhes específicos
        normalized_message = self._normalize_error_message(error_message)
        content = f"{error_type}:{normalized_message}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _normalize_error_message(self, message: str) -> str:
        """Normaliza mensagem de erro removendo detalhes específicos."""
        # Remove números, paths específicos, IDs, etc.
        import re
        
        # Remove paths de arquivo
        message = re.sub(r'[A-Za-z]:\\[^\\]+\\[^\\]+\\.*', '[PATH]', message)
        message = re.sub(r'/[^/]+/[^/]+/.*', '[PATH]', message)
        
        # Remove números específicos
        message = re.sub(r'\b\d+\b', '[NUMBER]', message)
        
        # Remove IDs e hashes
        message = re.sub(r'\b[a-f0-9]{8,}\b', '[ID]', message)
        
        # Remove timestamps
        message = re.sub(r'\d{4}-\d{2}-\d{2}', '[DATE]', message)
        message = re.sub(r'\d{2}:\d{2}:\d{2}', '[TIME]', message)
        
        return message.strip()
    
    def _load_error_patterns(self):
        """Carrega padrões de erro do banco para cache."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT error_hash, error_type, common_message, occurrence_count,
                           last_occurrence, prevention_strategy
                    FROM error_patterns
                """)
                
                for row in cursor.fetchall():
                    error_hash = row[0]
                    pattern = ErrorPattern(
                        error_hash=error_hash,
                        error_type=row[1],
                        common_message=row[2],
                        occurrence_count=row[3],
                        failed_attempts=[],
                        successful_solution=None,
                        last_occurrence=row[4],
                        prevention_strategy=row[5]
                    )
                    self._error_patterns_cache[error_hash] = pattern
        except Exception as e:
            self.logger.error(f"Erro ao carregar padrões: {e}")
    
    def register_error(self, 
                      error: Exception, 
                      context: Dict[str, Any] = None,
                      function_name: str = None) -> str:
        """
        Registra um novo erro no sistema.
        
        Returns:
            error_hash: Hash único do erro para rastreamento
        """
        error_type = type(error).__name__
        error_message = str(error)
        stack_trace = traceback.format_exc()
        timestamp = datetime.now().isoformat()
        
        error_hash = self._generate_error_hash(error_type, error_message)
        
        # Adiciona contexto automático
        if context is None:
            context = {}
        
        context.update({
            'function_name': function_name,
            'timestamp': timestamp,
            'error_hash': error_hash
        })
        
        self.logger.error(f"Erro registrado [{error_hash}]: {error_type} - {error_message}")
        
        # Atualiza padrão de erro
        self._update_error_pattern(error_hash, error_type, error_message, timestamp)
        
        return error_hash
    
    def register_solution_attempt(self,
                                error_hash: str,
                                attempted_solution: str,
                                solution_source: str,
                                success: bool,
                                context: Dict[str, Any] = None) -> int:
        """
        Registra uma tentativa de solução para um erro.
        
        Args:
            error_hash: Hash do erro
            attempted_solution: Descrição da solução tentada
            solution_source: Fonte da solução ('documentation', 'codebase', 'web_search', 'manual')
            success: Se a solução foi bem-sucedida
            context: Contexto adicional
        
        Returns:
            attempt_id: ID da tentativa registrada
        """
        timestamp = datetime.now().isoformat()
        
        if context is None:
            context = {}
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO error_attempts 
                (error_hash, timestamp, error_type, error_message, stack_trace,
                 attempted_solution, solution_source, success, context)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                error_hash,
                timestamp,
                context.get('error_type', 'Unknown'),
                context.get('error_message', 'Unknown'),
                context.get('stack_trace', ''),
                attempted_solution,
                solution_source,
                success,
                json.dumps(context)
            ))
            
            attempt_id = cursor.lastrowid
        
        # Se foi bem-sucedida, atualiza o padrão
        if success:
            self._mark_successful_solution(error_hash, attempt_id)
        
        self.logger.info(f"Tentativa registrada [{error_hash}]: {solution_source} - {'SUCESSO' if success else 'FALHA'}")
        
        return attempt_id
    
    def _update_error_pattern(self, error_hash: str, error_type: str, 
                            error_message: str, timestamp: str):
        """Atualiza ou cria padrão de erro."""
        normalized_message = self._normalize_error_message(error_message)
        
        with sqlite3.connect(self.db_path) as conn:
            # Verifica se padrão já existe
            cursor = conn.execute(
                "SELECT occurrence_count FROM error_patterns WHERE error_hash = ?",
                (error_hash,)
            )
            result = cursor.fetchone()
            
            if result:
                # Atualiza padrão existente
                new_count = result[0] + 1
                conn.execute("""
                    UPDATE error_patterns 
                    SET occurrence_count = ?, last_occurrence = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE error_hash = ?
                """, (new_count, timestamp, error_hash))
            else:
                # Cria novo padrão
                conn.execute("""
                    INSERT INTO error_patterns 
                    (error_hash, error_type, common_message, occurrence_count, last_occurrence)
                    VALUES (?, ?, ?, 1, ?)
                """, (error_hash, error_type, normalized_message, timestamp))
        
        # Atualiza cache
        if error_hash in self._error_patterns_cache:
            self._error_patterns_cache[error_hash].occurrence_count += 1
            self._error_patterns_cache[error_hash].last_occurrence = timestamp
        else:
            pattern = ErrorPattern(
                error_hash=error_hash,
                error_type=error_type,
                common_message=normalized_message,
                occurrence_count=1,
                failed_attempts=[],
                successful_solution=None,
                last_occurrence=timestamp,
                prevention_strategy=None
            )
            self._error_patterns_cache[error_hash] = pattern
    
    def _mark_successful_solution(self, error_hash: str, attempt_id: int):
        """Marca uma solução como bem-sucedida."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE error_patterns 
                SET successful_solution_id = ?, updated_at = CURRENT_TIMESTAMP
                WHERE error_hash = ?
            """, (attempt_id, error_hash))
    
    def get_failed_attempts(self, error_hash: str, limit: int = 5) -> List[ErrorAttempt]:
        """Retorna tentativas falhadas anteriores para um erro."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT timestamp, error_type, error_message, stack_trace,
                       attempted_solution, solution_source, success, context
                FROM error_attempts 
                WHERE error_hash = ? AND success = 0
                ORDER BY timestamp DESC
                LIMIT ?
            """, (error_hash, limit))
            
            attempts = []
            for row in cursor.fetchall():
                context = json.loads(row[7]) if row[7] else {}
                attempt = ErrorAttempt(
                    timestamp=row[0],
                    error_type=row[1],
                    error_message=row[2],
                    stack_trace=row[3],
                    attempted_solution=row[4],
                    solution_source=row[5],
                    success=row[6],
                    context=context
                )
                attempts.append(attempt)
            
            return attempts
    
    def get_successful_solution(self, error_hash: str) -> Optional[ErrorAttempt]:
        """Retorna solução bem-sucedida para um erro, se existir."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT ea.timestamp, ea.error_type, ea.error_message, ea.stack_trace,
                       ea.attempted_solution, ea.solution_source, ea.success, ea.context
                FROM error_patterns ep
                JOIN error_attempts ea ON ep.successful_solution_id = ea.id
                WHERE ep.error_hash = ?
            """, (error_hash,))
            
            row = cursor.fetchone()
            if row:
                context = json.loads(row[7]) if row[7] else {}
                return ErrorAttempt(
                    timestamp=row[0],
                    error_type=row[1],
                    error_message=row[2],
                    stack_trace=row[3],
                    attempted_solution=row[4],
                    solution_source=row[5],
                    success=row[6],
                    context=context
                )
            
            return None
    
    def analyze_error_context(self, error_hash: str) -> Dict[str, Any]:
        """
        Analisa o contexto de um erro e fornece recomendações.
        
        Returns:
            Dicionário com análise e recomendações
        """
        pattern = self._error_patterns_cache.get(error_hash)
        if not pattern:
            return {
                'status': 'new_error',
                'recommendation': 'Primeiro erro deste tipo. Proceder com solução padrão.',
                'search_strategy': ['documentation', 'codebase']
            }
        
        failed_attempts = self.get_failed_attempts(error_hash)
        successful_solution = self.get_successful_solution(error_hash)
        
        analysis = {
            'status': 'recurring_error',
            'occurrence_count': pattern.occurrence_count,
            'last_occurrence': pattern.last_occurrence,
            'failed_attempts_count': len(failed_attempts),
            'has_successful_solution': successful_solution is not None
        }
        
        # Gera recomendações baseadas no histórico
        if successful_solution:
            analysis.update({
                'recommendation': 'Erro já resolvido anteriormente. Aplicar solução conhecida.',
                'known_solution': successful_solution.attempted_solution,
                'solution_source': successful_solution.solution_source,
                'search_strategy': []
            })
        else:
            # Determina estratégia de busca baseada em tentativas anteriores
            tried_sources = {attempt.solution_source for attempt in failed_attempts}
            
            search_strategy = []
            if 'documentation' not in tried_sources:
                search_strategy.append('documentation')
            if 'codebase' not in tried_sources:
                search_strategy.append('codebase')
            if 'web_search' not in tried_sources and len(tried_sources) >= 2:
                search_strategy.append('web_search')
            
            if not search_strategy:
                search_strategy = ['manual_analysis', 'alternative_approach']
            
            analysis.update({
                'recommendation': f'Erro recorrente ({pattern.occurrence_count}x). Evitar soluções já tentadas.',
                'failed_solutions': [attempt.attempted_solution for attempt in failed_attempts],
                'tried_sources': list(tried_sources),
                'search_strategy': search_strategy
            })
        
        return analysis
    
    def generate_reflection_report(self, error_hash: str) -> str:
        """
        Gera relatório de reflexão formatado para um erro.
        
        Segue o formato especificado no prompt de correção de erros.
        """
        analysis = self.analyze_error_context(error_hash)
        pattern = self._error_patterns_cache.get(error_hash)
        failed_attempts = self.get_failed_attempts(error_hash, 3)
        
        report = []
        report.append("=" * 60)
        report.append("RELATÓRIO DE REFLEXÃO DE ERRO")
        report.append("=" * 60)
        
        # ERRO IDENTIFICADO
        if pattern:
            report.append(f"ERRO IDENTIFICADO: {pattern.error_type} - {pattern.common_message}")
        else:
            report.append("ERRO IDENTIFICADO: Novo erro sem padrão identificado")
        
        # ERROS ANTERIORES (Reflexão)
        report.append(f"\nERROS ANTERIORES (Reflexão):")
        if failed_attempts:
            for i, attempt in enumerate(failed_attempts, 1):
                report.append(f"  {i}. Fonte: {attempt.solution_source}")
                report.append(f"     Solução: {attempt.attempted_solution}")
                report.append(f"     Falha: Não resolveu o problema")
        else:
            report.append("  Nenhuma tentativa anterior registrada.")
        
        # FONTE DA SOLUÇÃO (Busca)
        report.append(f"\nFONTE DA SOLUÇÃO (Busca): {' -> '.join(analysis.get('search_strategy', ['manual']))}")
        
        # NOVA ESTRATÉGIA
        report.append(f"\nNOVA ESTRATÉGIA: {analysis.get('recommendation', 'Análise manual necessária')}")
        
        if analysis.get('known_solution'):
            report.append(f"SOLUÇÃO CONHECIDA: {analysis['known_solution']}")
        
        if analysis.get('failed_solutions'):
            report.append("\nSOLUÇÕES A EVITAR:")
            for solution in analysis['failed_solutions']:
                report.append(f"  ❌ {solution}")
        
        report.append("\n" + "=" * 60)
        report.append("META: NÃO COMETER O MESMO ERRO DUAS VEZES")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas gerais do sistema de reflexão."""
        with sqlite3.connect(self.db_path) as conn:
            # Total de erros únicos
            cursor = conn.execute("SELECT COUNT(*) FROM error_patterns")
            unique_errors = cursor.fetchone()[0]
            
            # Total de tentativas
            cursor = conn.execute("SELECT COUNT(*) FROM error_attempts")
            total_attempts = cursor.fetchone()[0]
            
            # Tentativas bem-sucedidas
            cursor = conn.execute("SELECT COUNT(*) FROM error_attempts WHERE success = 1")
            successful_attempts = cursor.fetchone()[0]
            
            # Erros resolvidos
            cursor = conn.execute("SELECT COUNT(*) FROM error_patterns WHERE successful_solution_id IS NOT NULL")
            resolved_errors = cursor.fetchone()[0]
            
            # Top 5 erros mais comuns
            cursor = conn.execute("""
                SELECT error_type, common_message, occurrence_count 
                FROM error_patterns 
                ORDER BY occurrence_count DESC 
                LIMIT 5
            """)
            top_errors = cursor.fetchall()
        
        success_rate = (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0
        resolution_rate = (resolved_errors / unique_errors * 100) if unique_errors > 0 else 0
        
        return {
            'unique_errors': unique_errors,
            'total_attempts': total_attempts,
            'successful_attempts': successful_attempts,
            'success_rate': round(success_rate, 2),
            'resolved_errors': resolved_errors,
            'resolution_rate': round(resolution_rate, 2),
            'top_errors': [
                {
                    'type': row[0],
                    'message': row[1],
                    'count': row[2]
                }
                for row in top_errors
            ]
        }


# Instância global para uso em todo o sistema
error_reflection = ErrorReflectionManager()


def with_error_reflection(func):
    """
    Decorator para automatizar o sistema de reflexão de erros.
    
    Usage:
        @with_error_reflection
        def my_function():
            # código que pode gerar erro
            pass
    """
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            # Registra o erro
            error_hash = error_reflection.register_error(
                error=e,
                context={'function': func.__name__, 'args': str(args), 'kwargs': str(kwargs)},
                function_name=func.__name__
            )
            
            # Gera relatório de reflexão
            reflection_report = error_reflection.generate_reflection_report(error_hash)
            print(reflection_report)
            
            # Re-levanta o erro para tratamento normal
            raise e
    
    return wrapper