"""
Gerenciador de Estratégias de Solução
Implementa análise inteligente de tentativas anteriores e estratégias de busca.
"""

import re
import json
import requests
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timedelta

from .error_reflection_manager import error_reflection
from .structured_error_logger import structured_logger


@dataclass
class SolutionStrategy:
    """Representa uma estratégia de solução."""
    source_type: str  # 'documentation', 'codebase', 'web_search', 'manual'
    priority: int     # 1 = alta, 2 = média, 3 = baixa
    description: str
    search_terms: List[str]
    expected_patterns: List[str]  # Padrões que indicam solução válida
    avoid_patterns: List[str]     # Padrões que indicam solução inválida


class SolutionStrategyManager:
    """
    Gerenciador de estratégias de solução baseado em análise de tentativas anteriores.
    """
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        
        # Estratégias base por categoria de erro
        self.base_strategies = {
            'api': [
                SolutionStrategy(
                    source_type='documentation',
                    priority=1,
                    description='Verificar documentação oficial da API',
                    search_terms=['api documentation', 'rate limits', 'authentication'],
                    expected_patterns=['official', 'docs', 'api reference'],
                    avoid_patterns=['stackoverflow', 'forum', 'blog']
                ),
                SolutionStrategy(
                    source_type='codebase',
                    priority=2,
                    description='Buscar implementações similares no código',
                    search_terms=['api_client', 'request', 'retry', 'error_handling'],
                    expected_patterns=['def ', 'class ', 'try:', 'except'],
                    avoid_patterns=['test_', 'mock_', 'example_']
                )
            ],
            'rapidapi': [
                SolutionStrategy(
                    source_type='codebase',
                    priority=1,
                    description='Verificar implementação de fallback para RapidAPI',
                    search_terms=['rapidapi', 'fallback', '403', 'forbidden'],
                    expected_patterns=['fallback', 'alternative', 'backup'],
                    avoid_patterns=['test', 'debug']
                ),
                SolutionStrategy(
                    source_type='documentation',
                    priority=2,
                    description='Consultar documentação RapidAPI sobre limites',
                    search_terms=['rapidapi limits', 'quota exceeded', 'rate limiting'],
                    expected_patterns=['quota', 'limit', 'billing'],
                    avoid_patterns=['tutorial', 'getting started']
                )
            ],
            'instagram': [
                SolutionStrategy(
                    source_type='codebase',
                    priority=1,
                    description='Verificar implementações de retry e rate limiting',
                    search_terms=['instagram', 'retry', 'rate_limit', 'sleep'],
                    expected_patterns=['retry', 'sleep', 'wait', 'delay'],
                    avoid_patterns=['test_', 'mock_']
                ),
                SolutionStrategy(
                    source_type='web_search',
                    priority=2,
                    description='Buscar soluções para erros específicos do Instagram',
                    search_terms=['instagram api error', 'instagrapi error'],
                    expected_patterns=['solution', 'fix', 'resolved'],
                    avoid_patterns=['question', 'help needed', 'unsolved']
                )
            ],
            'database': [
                SolutionStrategy(
                    source_type='codebase',
                    priority=1,
                    description='Verificar padrões de conexão e transação',
                    search_terms=['database', 'connection', 'transaction', 'commit'],
                    expected_patterns=['with ', 'try:', 'finally:', 'close()'],
                    avoid_patterns=['test_', 'example_']
                )
            ],
            'file_system': [
                SolutionStrategy(
                    source_type='codebase',
                    priority=1,
                    description='Verificar tratamento de paths e permissões',
                    search_terms=['file', 'path', 'exists', 'mkdir'],
                    expected_patterns=['Path(', 'os.path', 'exists()', 'mkdir'],
                    avoid_patterns=['test_', 'temp_']
                )
            ]
        }
        
        # Cache de resultados de busca
        self._search_cache = {}
    
    def analyze_failed_attempts(self, error_hash: str) -> Dict[str, Any]:
        """
        Analisa tentativas falhadas para identificar padrões e evitar repetições.
        """
        failed_attempts = error_reflection.get_failed_attempts(error_hash, limit=10)
        
        if not failed_attempts:
            return {
                'patterns': [],
                'avoided_sources': [],
                'avoided_solutions': [],
                'recommendations': ['Primeiro erro deste tipo - proceder com estratégia padrão']
            }
        
        # Analisa padrões nas tentativas falhadas
        source_failures = {}
        solution_patterns = []
        common_mistakes = []
        
        for attempt in failed_attempts:
            # Conta falhas por fonte
            source = attempt.solution_source
            source_failures[source] = source_failures.get(source, 0) + 1
            
            # Extrai padrões das soluções tentadas
            solution_text = attempt.attempted_solution.lower()
            solution_patterns.append(solution_text)
            
            # Identifica erros comuns
            if 'timeout' in solution_text and 'increase' in solution_text:
                common_mistakes.append('Aumentar timeout sem verificar causa raiz')
            elif 'retry' in solution_text and 'infinite' in solution_text:
                common_mistakes.append('Retry infinito sem limite')
            elif 'ignore' in solution_text or 'skip' in solution_text:
                common_mistakes.append('Ignorar erro sem tratamento adequado')
        
        # Identifica padrões de falha
        failure_patterns = []
        for pattern in solution_patterns:
            words = pattern.split()
            for i in range(len(words) - 1):
                bigram = f"{words[i]} {words[i+1]}"
                if solution_patterns.count(bigram) > 1:
                    failure_patterns.append(bigram)
        
        return {
            'total_attempts': len(failed_attempts),
            'source_failures': source_failures,
            'failure_patterns': list(set(failure_patterns)),
            'common_mistakes': list(set(common_mistakes)),
            'avoided_sources': [s for s, count in source_failures.items() if count >= 2],
            'avoided_solutions': solution_patterns,
            'recommendations': self._generate_avoidance_recommendations(
                source_failures, common_mistakes
            )
        }
    
    def _generate_avoidance_recommendations(self, 
                                          source_failures: Dict[str, int],
                                          common_mistakes: List[str]) -> List[str]:
        """Gera recomendações baseadas em falhas anteriores."""
        recommendations = []
        
        # Recomendações baseadas em fontes que falharam
        if source_failures.get('web_search', 0) >= 2:
            recommendations.append('Evitar soluções genéricas da web - focar em documentação oficial')
        
        if source_failures.get('manual', 0) >= 2:
            recommendations.append('Soluções manuais falharam - buscar abordagem sistemática')
        
        if source_failures.get('codebase', 0) >= 2:
            recommendations.append('Implementações internas falharam - verificar dependências externas')
        
        # Recomendações baseadas em erros comuns
        if 'Aumentar timeout' in common_mistakes:
            recommendations.append('Não apenas aumentar timeouts - investigar causa da lentidão')
        
        if 'Retry infinito' in common_mistakes:
            recommendations.append('Implementar retry com backoff exponencial e limite máximo')
        
        if 'Ignorar erro' in common_mistakes:
            recommendations.append('Não ignorar erros - implementar tratamento adequado')
        
        return recommendations
    
    def get_solution_strategies(self, error_hash: str) -> List[SolutionStrategy]:
        """
        Retorna estratégias de solução priorizadas para um erro específico.
        """
        # Analisa contexto do erro
        analysis = error_reflection.analyze_error_context(error_hash)
        failed_analysis = self.analyze_failed_attempts(error_hash)
        
        # Determina categoria do erro
        error_category = 'unknown'
        if 'error_patterns_cache' in dir(error_reflection):
            pattern = error_reflection._error_patterns_cache.get(error_hash)
            if pattern:
                error_category = self._categorize_error_from_pattern(pattern)
        
        # Obtém estratégias base para a categoria
        base_strategies = self.base_strategies.get(error_category, [])
        
        # Filtra estratégias baseado em tentativas anteriores
        filtered_strategies = []
        avoided_sources = set(failed_analysis.get('avoided_sources', []))
        
        for strategy in base_strategies:
            # Pula fontes que já falharam múltiplas vezes
            if strategy.source_type in avoided_sources:
                continue
            
            # Ajusta prioridade baseado no histórico
            adjusted_priority = strategy.priority
            source_failures = failed_analysis.get('source_failures', {})
            if strategy.source_type in source_failures:
                adjusted_priority += source_failures[strategy.source_type]
            
            # Cria nova estratégia com prioridade ajustada
            adjusted_strategy = SolutionStrategy(
                source_type=strategy.source_type,
                priority=adjusted_priority,
                description=strategy.description,
                search_terms=strategy.search_terms,
                expected_patterns=strategy.expected_patterns,
                avoid_patterns=strategy.avoid_patterns + failed_analysis.get('failure_patterns', [])
            )
            
            filtered_strategies.append(adjusted_strategy)
        
        # Adiciona estratégias alternativas se poucas restaram
        if len(filtered_strategies) < 2:
            filtered_strategies.extend(self._get_alternative_strategies(error_category, avoided_sources))
        
        # Ordena por prioridade
        filtered_strategies.sort(key=lambda x: x.priority)
        
        return filtered_strategies
    
    def _categorize_error_from_pattern(self, pattern) -> str:
        """Categoriza erro baseado no padrão identificado."""
        error_type = pattern.error_type.lower()
        error_message = pattern.common_message.lower()
        
        if 'rapidapi' in error_message or '403' in error_message:
            return 'rapidapi'
        elif 'instagram' in error_message or 'instagrapi' in error_message:
            return 'instagram'
        elif 'connection' in error_message or 'http' in error_message:
            return 'api'
        elif 'database' in error_message or 'sql' in error_message:
            return 'database'
        elif 'file' in error_message or 'path' in error_message:
            return 'file_system'
        
        return 'unknown'
    
    def _get_alternative_strategies(self, 
                                  error_category: str, 
                                  avoided_sources: set) -> List[SolutionStrategy]:
        """Retorna estratégias alternativas quando as principais falharam."""
        alternatives = []
        
        # Estratégias de último recurso
        if 'web_search' not in avoided_sources:
            alternatives.append(SolutionStrategy(
                source_type='web_search',
                priority=5,
                description='Busca ampla na web por soluções similares',
                search_terms=[error_category, 'error', 'solution'],
                expected_patterns=['solved', 'fixed', 'working'],
                avoid_patterns=['question', 'help', 'unsolved']
            ))
        
        if 'manual' not in avoided_sources:
            alternatives.append(SolutionStrategy(
                source_type='manual',
                priority=6,
                description='Análise manual detalhada do problema',
                search_terms=[],
                expected_patterns=[],
                avoid_patterns=[]
            ))
        
        return alternatives
    
    def search_codebase_solutions(self, strategy: SolutionStrategy) -> List[Dict[str, Any]]:
        """
        Busca soluções no codebase baseado na estratégia.
        """
        results = []
        
        for search_term in strategy.search_terms:
            # Busca em arquivos Python
            for py_file in self.project_root.rglob("*.py"):
                try:
                    content = py_file.read_text(encoding='utf-8')
                    
                    if search_term.lower() in content.lower():
                        # Extrai contexto relevante
                        lines = content.split('\n')
                        relevant_lines = []
                        
                        for i, line in enumerate(lines):
                            if search_term.lower() in line.lower():
                                # Inclui contexto (5 linhas antes e depois)
                                start = max(0, i - 5)
                                end = min(len(lines), i + 6)
                                context = '\n'.join(lines[start:end])
                                
                                # Verifica se contém padrões esperados
                                has_expected = any(
                                    pattern in context.lower() 
                                    for pattern in strategy.expected_patterns
                                )
                                
                                # Verifica se contém padrões a evitar
                                has_avoided = any(
                                    pattern in context.lower() 
                                    for pattern in strategy.avoid_patterns
                                )
                                
                                if has_expected and not has_avoided:
                                    results.append({
                                        'file': str(py_file.relative_to(self.project_root)),
                                        'line_number': i + 1,
                                        'context': context,
                                        'relevance_score': self._calculate_relevance_score(
                                            context, strategy
                                        )
                                    })
                
                except Exception as e:
                    continue
        
        # Ordena por relevância
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:10]  # Retorna top 10
    
    def search_documentation_solutions(self, strategy: SolutionStrategy) -> List[Dict[str, Any]]:
        """
        Busca soluções em documentação online.
        """
        results = []
        
        # URLs de documentação conhecidas
        doc_urls = {
            'rapidapi': 'https://docs.rapidapi.com/',
            'instagram': 'https://developers.facebook.com/docs/instagram-api/',
            'python': 'https://docs.python.org/3/',
            'requests': 'https://docs.python-requests.org/',
        }
        
        # Simula busca em documentação (implementação real dependeria de web scraping)
        for search_term in strategy.search_terms:
            for doc_name, base_url in doc_urls.items():
                if any(term in search_term.lower() for term in [doc_name, 'api', 'error']):
                    results.append({
                        'source': f'{doc_name} documentation',
                        'url': base_url,
                        'search_term': search_term,
                        'relevance_score': 0.8,
                        'description': f'Consultar documentação oficial do {doc_name}'
                    })
        
        return results
    
    def search_web_solutions(self, strategy: SolutionStrategy) -> List[Dict[str, Any]]:
        """
        Busca soluções na web (implementação simplificada).
        """
        results = []
        
        # Termos de busca otimizados
        search_queries = []
        for term in strategy.search_terms:
            search_queries.append(f"{term} python solution")
            search_queries.append(f"{term} error fix")
        
        # Simula resultados de busca web
        for query in search_queries[:3]:  # Limita para evitar muitas requisições
            results.append({
                'query': query,
                'description': f'Buscar: "{query}"',
                'suggested_sites': ['stackoverflow.com', 'github.com', 'docs.python.org'],
                'relevance_score': 0.6
            })
        
        return results
    
    def _calculate_relevance_score(self, content: str, strategy: SolutionStrategy) -> float:
        """Calcula score de relevância de um conteúdo."""
        score = 0.0
        content_lower = content.lower()
        
        # Pontos por padrões esperados
        for pattern in strategy.expected_patterns:
            if pattern.lower() in content_lower:
                score += 0.3
        
        # Penaliza padrões a evitar
        for pattern in strategy.avoid_patterns:
            if pattern.lower() in content_lower:
                score -= 0.2
        
        # Pontos por termos de busca
        for term in strategy.search_terms:
            if term.lower() in content_lower:
                score += 0.1
        
        # Bonificação por estruturas de código bem formadas
        if 'try:' in content_lower and 'except' in content_lower:
            score += 0.2
        
        if 'def ' in content_lower or 'class ' in content_lower:
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def generate_solution_plan(self, error_hash: str) -> Dict[str, Any]:
        """
        Gera plano completo de solução para um erro.
        """
        strategies = self.get_solution_strategies(error_hash)
        failed_analysis = self.analyze_failed_attempts(error_hash)
        
        plan = {
            'error_hash': error_hash,
            'timestamp': datetime.now().isoformat(),
            'failed_attempts_summary': failed_analysis,
            'recommended_strategies': [],
            'execution_order': [],
            'estimated_time': 0
        }
        
        total_time = 0
        for i, strategy in enumerate(strategies[:5]):  # Top 5 estratégias
            strategy_plan = {
                'step': i + 1,
                'source_type': strategy.source_type,
                'description': strategy.description,
                'priority': strategy.priority,
                'estimated_time_minutes': self._estimate_strategy_time(strategy),
                'search_terms': strategy.search_terms,
                'success_indicators': strategy.expected_patterns,
                'avoid_patterns': strategy.avoid_patterns
            }
            
            # Adiciona resultados de busca se disponível
            if strategy.source_type == 'codebase':
                strategy_plan['search_results'] = self.search_codebase_solutions(strategy)
            elif strategy.source_type == 'documentation':
                strategy_plan['search_results'] = self.search_documentation_solutions(strategy)
            elif strategy.source_type == 'web_search':
                strategy_plan['search_results'] = self.search_web_solutions(strategy)
            
            plan['recommended_strategies'].append(strategy_plan)
            plan['execution_order'].append(f"Passo {i+1}: {strategy.description}")
            total_time += strategy_plan['estimated_time_minutes']
        
        plan['estimated_time'] = total_time
        
        return plan
    
    def _estimate_strategy_time(self, strategy: SolutionStrategy) -> int:
        """Estima tempo necessário para executar uma estratégia (em minutos)."""
        base_times = {
            'codebase': 10,
            'documentation': 15,
            'web_search': 20,
            'manual': 30
        }
        
        base_time = base_times.get(strategy.source_type, 15)
        
        # Ajusta baseado na prioridade
        if strategy.priority == 1:
            return base_time
        elif strategy.priority == 2:
            return int(base_time * 1.2)
        else:
            return int(base_time * 1.5)


# Instância global
solution_strategy_manager = SolutionStrategyManager()