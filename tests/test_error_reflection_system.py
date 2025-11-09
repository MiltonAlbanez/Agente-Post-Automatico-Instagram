"""
Testes para o Sistema de Reflexão e Prevenção de Erros
Valida todas as funcionalidades do sistema implementado.
"""

import unittest
import tempfile
import os
import sqlite3
from unittest.mock import patch, MagicMock
import sys
import json
from datetime import datetime, timedelta

# Adiciona o diretório src ao path para importar os módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.error_reflection_manager import ErrorReflectionManager
from services.structured_error_logger import StructuredErrorLogger
from services.solution_strategy_manager import SolutionStrategyManager
from services.error_reflection_integration import (
    smart_error_handler, 
    with_error_reflection, 
    error_reflection_context,
    analyze_error,
    get_function_health
)


class TestErrorReflectionManager(unittest.TestCase):
    """Testa a classe ErrorReflectionManager."""
    
    def setUp(self):
        """Configura ambiente de teste."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_errors.db")
        self.manager = ErrorReflectionManager(db_path=self.db_path)
    
    def tearDown(self):
        """Limpa ambiente de teste."""
        try:
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
            # Remove arquivos de log que podem ter sido criados
            for file in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            os.rmdir(self.temp_dir)
        except (PermissionError, OSError):
            pass  # Ignora erros de permissão/diretório não vazio no Windows
    
    def test_database_initialization(self):
        """Testa se o banco de dados é inicializado corretamente."""
        self.assertTrue(os.path.exists(self.db_path))
        
        # Verifica se as tabelas foram criadas
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['errors', 'solutions', 'patterns', 'performance_metrics']
        for table in expected_tables:
            self.assertIn(table, tables)
        
        conn.close()
    
    def test_register_error(self):
        """Testa o registro de erros."""
        error = ConnectionError('Falha na conexão')
        context = {'param1': 'value1'}
        
        error_hash = self.manager.register_error(error, context, 'test_function')
        self.assertIsNotNone(error_hash)
        self.assertEqual(len(error_hash), 32)  # MD5 hash length
        
        # Verifica se o erro foi salvo no banco
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM error_patterns WHERE error_hash = ?", (error_hash,))
        result = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(result)
        self.assertEqual(result[1], 'ConnectionError')  # error_type
    
    def test_get_failed_attempts(self):
        """Testa a busca por tentativas falhadas."""
        # Registra um erro
        error = ConnectionError('Falha na conexão com API')
        error_hash = self.manager.register_error(error, {}, 'api_call')
        
        # Registra algumas tentativas falhadas
        self.manager.register_solution_attempt(
            error_hash, 
            "Aumentar timeout", 
            "manual", 
            False
        )
        self.manager.register_solution_attempt(
            error_hash, 
            "Trocar endpoint", 
            "documentation", 
            False
        )
        
        # Busca tentativas falhadas
        failed_attempts = self.manager.get_failed_attempts(error_hash)
        
        self.assertEqual(len(failed_attempts), 2)
        self.assertFalse(failed_attempts[0].success)
        self.assertFalse(failed_attempts[1].success)
    
    def test_error_patterns(self):
        """Testa a criação de padrões de erro."""
        # Adiciona vários erros do mesmo tipo
        for i in range(5):
            error = Exception(f'403 Forbidden - tentativa {i}')
            self.manager.register_error(error, {}, 'collect_hashtags')
        
        # Verifica se o padrão foi criado no cache
        self.assertTrue(len(self.manager._error_patterns_cache) > 0)
        
        # Verifica se algum padrão tem contagem >= 5
        high_frequency_patterns = [
            p for p in self.manager._error_patterns_cache.values() 
            if p.occurrence_count >= 5
        ]
        self.assertTrue(len(high_frequency_patterns) > 0)


class TestStructuredErrorLogger(unittest.TestCase):
    """Testa o sistema de logging estruturado."""
    
    def setUp(self):
        """Configura ambiente de teste."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_logger.db")
        self.logger = StructuredErrorLogger(name="test_logger", log_dir=self.temp_dir)
    
    def tearDown(self):
        """Limpa ambiente de teste."""
        try:
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
            os.rmdir(self.temp_dir)
        except PermissionError:
            pass  # Ignora erro de permissão no Windows
    
    def test_categorize_error(self):
        """Testa a categorização de erros."""
        # Testa diferentes tipos de erro
        test_cases = [
            (ConnectionError("Timeout"), "network"),
            (ValueError("Invalid value"), "validation"),
            (FileNotFoundError("File not found"), "file_system"),
            (Exception("Unknown error"), "unknown")
        ]
        
        for error, expected_category in test_cases:
            category = self.logger.categorize_error(error)
            self.assertEqual(category, expected_category)
    
    def test_extract_context(self):
        """Testa a extração de contexto."""
        try:
            # Simula um erro com contexto
            x = 1 / 0
        except Exception as e:
            context = self.logger.extract_error_context(e)
            
            self.assertIn('traceback', context)
            self.assertIn('local_variables', context)
            self.assertIn('function_name', context)
            self.assertEqual(context['additional_context']['param1'], "value1")
    
    def test_log_error_with_context(self):
        """Testa o logging de erro com contexto completo."""
        try:
            raise ValueError("Teste de erro")
        except Exception as e:
            error_hash = self.logger.log_error(
            e,
            context={"test": True},
            function_name="test_function"
        )
            
            self.assertIsNotNone(error_hash)
            
            # Verifica se foi salvo corretamente
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM error_patterns WHERE error_hash = ?", (error_hash,))
            result = cursor.fetchone()
            conn.close()
            
            self.assertIsNotNone(result)
            self.assertEqual(result[1], "validation")  # category


class TestSolutionStrategyManager(unittest.TestCase):
    """Testa o gerenciador de estratégias de solução."""
    
    def setUp(self):
        """Configura ambiente de teste."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_strategy.db")
        self.strategy_manager = SolutionStrategyManager(project_root=self.temp_dir)
    
    def tearDown(self):
        """Limpa ambiente de teste."""
        try:
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
            os.rmdir(self.temp_dir)
        except PermissionError:
            pass  # Ignora erro de permissão no Windows
    
    def test_analyze_failed_attempts(self):
        """Testa a análise de tentativas falhadas."""
        error_hash = "test_hash_123"
        failed_attempts = [
            "Tentativa 1: Aumentar timeout",
            "Tentativa 2: Retry com backoff",
            "Tentativa 3: Mudança de endpoint"
        ]
        
        analysis = self.strategy_manager.analyze_failed_attempts(error_hash)
        
        self.assertIn('common_patterns', analysis)
        self.assertIn('avoided_solutions', analysis)
        self.assertIn('success_probability', analysis)
    
    def test_generate_solution_strategies(self):
        """Testa a geração de estratégias de solução."""
        error_data = {
            'error_type': 'ConnectionError',
            'message': '403 Forbidden',
            'function_name': 'api_call',
            'category': 'network'
        }
        
        # Primeiro registra o erro para ter um hash
        manager = ErrorReflectionManager(db_path=self.db_path)
        error_hash = manager.register_error(Exception("Test error"), {"test": "context"})
        
        strategies = self.strategy_manager.get_solution_strategies(error_hash)
        
        self.assertIsInstance(strategies, list)
        self.assertTrue(len(strategies) > 0)
        
        # Verifica estrutura das estratégias
        for strategy in strategies:
            self.assertTrue(hasattr(strategy, 'source_type'))
            self.assertTrue(hasattr(strategy, 'priority'))
            self.assertTrue(hasattr(strategy, 'description'))
    
    @patch('requests.get')
    def test_search_web_solutions(self, mock_get):
        """Testa a busca de soluções na web."""
        # Mock da resposta da API
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'items': [
                {
                    'title': 'Como resolver erro 403',
                    'link': 'https://example.com/solution',
                    'snippet': 'Solução para erro 403...'
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Importa SolutionStrategy
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from src.services.solution_strategy_manager import SolutionStrategy
        
        strategy = SolutionStrategy(
            source_type='web_search',
            priority=1,
            description='Test strategy',
            search_terms=['Python', 'ConnectionError', '403', 'Forbidden'],
            expected_patterns=['solution', 'fix'],
            avoid_patterns=['test', 'example']
        )
        results = self.strategy_manager.search_web_solutions(strategy)
        
        self.assertIsInstance(results, list)
        if results:  # Se a busca retornou resultados
            result = results[0]
            self.assertIn('title', result)
            self.assertIn('url', result)
            self.assertIn('description', result)


class TestErrorReflectionIntegration(unittest.TestCase):
    """Testa a integração do sistema de reflexão."""
    
    def setUp(self):
        """Configura ambiente de teste."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_integration.db")
        
        # Configura o sistema para usar o banco de teste
        import services.error_reflection_integration as integration_module
        integration_module.error_manager = ErrorReflectionManager(db_path=self.db_path)
        integration_module.error_logger = StructuredErrorLogger(name="test_integration", log_dir=self.temp_dir)
    
    def tearDown(self):
        """Limpa ambiente de teste."""
        try:
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
            os.rmdir(self.temp_dir)
        except PermissionError:
            pass  # Ignora erro de permissão no Windows
    
    def test_with_error_reflection_decorator(self):
        """Testa o decorator with_error_reflection."""
        
        @with_error_reflection(critical=True, retry_attempts=2)
        def test_function_with_error():
            raise ValueError("Erro de teste")
        
        # A função deve falhar após os retries
        with self.assertRaises(ValueError):
            test_function_with_error()
        
        # Verifica se o erro foi registrado
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM error_attempts")
        error_count = cursor.fetchone()[0]
        conn.close()
        
        self.assertGreater(error_count, 0)
    
    def test_smart_error_handler_with_fallback(self):
        """Testa o smart_error_handler com fallback."""
        
        def fallback_function(*args, **kwargs):
            return "fallback_result"
        
        @smart_error_handler(
            function_name="test_with_fallback",
            critical=False,
            retry_attempts=1,
            fallback_function=fallback_function
        )
        def test_function_with_fallback():
            raise ConnectionError("Erro de conexão")
        
        # Deve retornar o resultado do fallback
        result = test_function_with_fallback()
        self.assertEqual(result, "fallback_result")
    
    def test_error_reflection_context(self):
        """Testa o context manager error_reflection_context."""
        
        with self.assertRaises(ValueError):
            with error_reflection_context("test_context", critical=True):
                raise ValueError("Erro no contexto")
        
        # Verifica se o erro foi registrado
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM error_attempts WHERE context LIKE ?", ("%test_context%",))
        error_count = cursor.fetchone()[0]
        conn.close()
        
        self.assertGreater(error_count, 0)


class TestSystemIntegration(unittest.TestCase):
    """Testa a integração completa do sistema."""
    
    def setUp(self):
        """Configura ambiente de teste."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_system.db")
    
    def tearDown(self):
        """Limpa ambiente de teste."""
        try:
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
            os.rmdir(self.temp_dir)
        except PermissionError:
            pass  # Ignora erro de permissão no Windows
    
    def test_complete_error_cycle(self):
        """Testa o ciclo completo de erro: detecção -> análise -> estratégia -> prevenção."""
        
        # 1. Inicializa o sistema
        manager = ErrorReflectionManager(db_path=self.db_path)
        logger = StructuredErrorLogger(name="test_system", log_dir=self.temp_dir)
        strategy_manager = SolutionStrategyManager(project_root=self.temp_dir)
        
        # 2. Simula um erro recorrente
        error_data = {
            'error_type': 'RapidAPIError',
            'message': '403 Forbidden - Quota exceeded',
            'function_name': 'collect_hashtags',
            'context': {'api_key': 'hidden', 'endpoint': '/hashtags'}
        }
        
        # Registra o erro múltiplas vezes
        error_hashes = []
        for i in range(3):
            error_hash = manager.register_error(Exception("RapidAPI 403 Forbidden"), error_data)
            error_hashes.append(error_hash)
        
        # 3. Verifica padrões no cache
        self.assertTrue(len(manager._error_patterns_cache) > 0)
        
        # 4. Gera estratégias de solução
        strategies = strategy_manager.get_solution_strategies(error_hashes[0])
        self.assertTrue(len(strategies) > 0)
        
        # Verifica se o sistema sugere evitar soluções já tentadas
        failed_attempts = ["Aumentar timeout", "Trocar API key"]
        analysis = strategy_manager.analyze_failed_attempts(error_hashes[0])
        
        self.assertIn('avoided_solutions', analysis)
        self.assertTrue(len(analysis['avoided_solutions']) > 0)
    
    def test_solution_attempt_tracking(self):
        """Testa o rastreamento de tentativas de solução."""
        
        manager = ErrorReflectionManager(db_path=self.db_path)
        
        # Registra um erro
        error = ConnectionError("Timeout na API")
        error_hash = manager.register_error(error, {}, "api_function")
        
        # Registra tentativas de solução
        attempt_id_1 = manager.register_solution_attempt(
            error_hash, "Aumentar timeout para 30s", "manual", False
        )
        attempt_id_2 = manager.register_solution_attempt(
            error_hash, "Implementar retry com backoff", "documentation", True
        )
        
        self.assertIsNotNone(attempt_id_1)
        self.assertIsNotNone(attempt_id_2)
        
        # Verifica se a solução bem-sucedida foi registrada
        successful_solution = manager.get_successful_solution(error_hash)
        self.assertIsNotNone(successful_solution)
        self.assertTrue(successful_solution.success)


class TestErrorPreventionScenarios(unittest.TestCase):
    """Testa cenários específicos de prevenção de erros."""
    
    def test_rapidapi_403_prevention(self):
        """Testa a prevenção específica do erro RapidAPI 403."""
        
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_rapidapi.db")
        
        try:
            manager = ErrorReflectionManager(db_path=db_path)
            
            # Simula histórico de erros 403 da RapidAPI
            for i in range(5):
                error = Exception('403 Forbidden')
                context = {'api': 'rapidapi', 'endpoint': '/hashtags'}
                manager.register_error(error, context, 'collect_hashtags')
            
            # Verifica se o padrão foi criado no cache
            self.assertTrue(len(manager._error_patterns_cache) > 0)
            
            # Verifica se algum padrão tem alta frequência
            high_frequency_patterns = [
                p for p in manager._error_patterns_cache.values() 
                if p.occurrence_count >= 5
            ]
            self.assertTrue(len(high_frequency_patterns) > 0)
            
        finally:
            # Fecha conexões antes de deletar
            if hasattr(manager, '_connection'):
                manager._connection.close()
            try:
                if os.path.exists(db_path):
                    os.remove(db_path)
                os.rmdir(temp_dir)
            except PermissionError:
                pass  # Ignora erro de permissão no Windows


if __name__ == '__main__':
    # Configura o ambiente de teste
    test_suite = unittest.TestSuite()
    
    # Adiciona todos os testes
    test_classes = [
        TestErrorReflectionManager,
        TestStructuredErrorLogger,
        TestSolutionStrategyManager,
        TestErrorReflectionIntegration,
        TestSystemIntegration,
        TestErrorPreventionScenarios
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Executa os testes
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Relatório final
    print(f"\n{'='*60}")
    print("RELATÓRIO FINAL DOS TESTES")
    print(f"{'='*60}")
    print(f"Testes executados: {result.testsRun}")
    print(f"Falhas: {len(result.failures)}")
    print(f"Erros: {len(result.errors)}")
    print(f"Taxa de sucesso: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFALHAS ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"  • {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\nERROS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"  • {test}: {traceback.split('Exception:')[-1].strip()}")
    
    print(f"\n{'='*60}")