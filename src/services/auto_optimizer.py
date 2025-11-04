#!/usr/bin/env python3
"""
Sistema de Otimização Automática
Aplica automaticamente as configurações vencedoras dos testes A/B para maximizar performance.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from .ab_testing_manager import ABTestingManager
from .performance_tracker import PerformanceTracker

class AutoOptimizer:
    """
    Sistema que automaticamente aplica otimizações baseadas nos resultados dos testes A/B.
    """
    
    def __init__(self, config_path: str = "config/auto_optimizer.json"):
        self.config_path = config_path
        self.ab_manager = ABTestingManager()
        self.performance_tracker = PerformanceTracker()
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Carrega configurações do otimizador."""
        default_config = {
            "auto_apply_enabled": True,
            "confidence_threshold": 95,
            "minimum_sample_size": 30,
            "minimum_test_duration_days": 7,
            "optimization_rules": {
                "content_format": {
                    "metric": "engagement_rate",
                    "weight": 0.4
                },
                "hashtag_strategy": {
                    "metric": "reach",
                    "weight": 0.3
                },
                "image_style": {
                    "metric": "impressions",
                    "weight": 0.3
                }
            },
            "rollback_conditions": {
                "performance_drop_threshold": 0.1,  # 10% queda
                "monitoring_period_days": 3
            }
        }
        
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge com configurações padrão
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            else:
                # Criar arquivo de configuração padrão
                Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2, ensure_ascii=False)
                return default_config
        except Exception as e:
            print(f"Erro ao carregar configuração: {e}")
            return default_config
    
    def analyze_test_completion(self) -> List[Dict[str, Any]]:
        """
        Analisa testes A/B para identificar quais podem ser finalizados e aplicados.
        """
        completed_tests = []
        
        for test_name, test_data in self.ab_manager.active_tests.items():
            if test_data.get('status') != 'active':
                continue
                
            # Analisar resultados do teste
            analysis = self.ab_manager.analyze_test_results(test_name)
            
            if not analysis:
                continue
                
            # Verificar critérios para finalização
            confidence = analysis.get('confidence', 0)
            sample_size = analysis.get('sample_size', 0)
            duration_days = analysis.get('duration_days', 0)
            
            meets_criteria = (
                confidence >= self.config['confidence_threshold'] and
                sample_size >= self.config['minimum_sample_size'] and
                duration_days >= self.config['minimum_test_duration_days']
            )
            
            if meets_criteria:
                completed_tests.append({
                    'test_name': test_name,
                    'winner': analysis.get('winner'),
                    'confidence': confidence,
                    'lift': analysis.get('lift', 0),
                    'analysis': analysis
                })
        
        return completed_tests
    
    def apply_optimization(self, test_result: Dict[str, Any]) -> bool:
        """
        Aplica uma otimização baseada no resultado de um teste A/B.
        """
        try:
            test_name = test_result['test_name']
            winner = test_result['winner']
            
            # Determinar tipo de otimização
            optimization_type = self._get_optimization_type(test_name)
            
            if not optimization_type:
                print(f"Tipo de otimização não identificado para: {test_name}")
                return False
            
            # Aplicar otimização
            success = self._apply_configuration(optimization_type, winner)
            
            if success:
                # Registrar otimização aplicada
                self._log_optimization(test_result)
                
                # Marcar teste como finalizado
                self.ab_manager.end_test(test_name)
                
                print(f"✅ Otimização aplicada: {optimization_type} = {winner}")
                print(f"   Melhoria esperada: +{test_result['lift']}%")
                
                return True
            else:
                print(f"❌ Falha ao aplicar otimização: {test_name}")
                return False
                
        except Exception as e:
            print(f"Erro ao aplicar otimização: {e}")
            return False
    
    def _get_optimization_type(self, test_name: str) -> Optional[str]:
        """Identifica o tipo de otimização baseado no nome do teste."""
        test_name_lower = test_name.lower()
        
        if 'formato' in test_name_lower or 'content' in test_name_lower:
            return 'content_format'
        elif 'hashtag' in test_name_lower:
            return 'hashtag_strategy'
        elif 'imagem' in test_name_lower or 'image' in test_name_lower:
            return 'image_style'
        else:
            return None
    
    def _apply_configuration(self, optimization_type: str, winner_value: str) -> bool:
        """Aplica uma configuração específica."""
        try:
            # Carregar configuração atual
            config_file = "config/bot_config.json"
            
            if Path(config_file).exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {}
            
            # Aplicar otimização
            if 'optimizations' not in config:
                config['optimizations'] = {}
            
            config['optimizations'][optimization_type] = {
                'value': winner_value,
                'applied_at': datetime.now().isoformat(),
                'source': 'ab_testing'
            }
            
            # Salvar configuração
            Path(config_file).parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Erro ao aplicar configuração: {e}")
            return False
    
    def _log_optimization(self, test_result: Dict[str, Any]):
        """Registra uma otimização aplicada."""
        try:
            log_file = "data/optimization_log.json"
            
            # Carregar log existente
            if Path(log_file).exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
            else:
                log_data = {'optimizations': []}
            
            # Adicionar nova otimização
            optimization_entry = {
                'timestamp': datetime.now().isoformat(),
                'test_name': test_result['test_name'],
                'winner': test_result['winner'],
                'confidence': test_result['confidence'],
                'lift': test_result['lift'],
                'status': 'applied'
            }
            
            log_data['optimizations'].append(optimization_entry)
            
            # Salvar log
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Erro ao registrar otimização: {e}")
    
    def monitor_performance(self) -> Dict[str, Any]:
        """
        Monitora performance após aplicação de otimizações.
        """
        try:
            # Período de monitoramento
            monitoring_days = self.config['rollback_conditions']['monitoring_period_days']
            cutoff_date = datetime.now() - timedelta(days=monitoring_days)
            
            with sqlite3.connect(self.performance_tracker.db_path) as conn:
                cursor = conn.cursor()
                
                # Performance antes das otimizações
                cursor.execute("""
                    SELECT AVG(engagement_rate) 
                    FROM post_performance 
                    WHERE published_at < ? AND engagement_rate > 0
                """, (cutoff_date.isoformat(),))
                
                before_avg = cursor.fetchone()[0] or 0
                
                # Performance após otimizações
                cursor.execute("""
                    SELECT AVG(engagement_rate) 
                    FROM post_performance 
                    WHERE published_at >= ? AND engagement_rate > 0
                """, (cutoff_date.isoformat(),))
                
                after_avg = cursor.fetchone()[0] or 0
                
                # Calcular mudança
                if before_avg > 0:
                    change_percent = ((after_avg - before_avg) / before_avg) * 100
                else:
                    change_percent = 0
                
                return {
                    'before_avg': round(before_avg, 2),
                    'after_avg': round(after_avg, 2),
                    'change_percent': round(change_percent, 2),
                    'monitoring_period_days': monitoring_days,
                    'needs_rollback': change_percent < -self.config['rollback_conditions']['performance_drop_threshold'] * 100
                }
                
        except Exception as e:
            print(f"Erro ao monitorar performance: {e}")
            return {
                'before_avg': 0,
                'after_avg': 0,
                'change_percent': 0,
                'monitoring_period_days': 0,
                'needs_rollback': False
            }
    
    def run_optimization_cycle(self) -> Dict[str, Any]:
        """
        Executa um ciclo completo de otimização automática.
        """
        if not self.config['auto_apply_enabled']:
            return {'status': 'disabled', 'message': 'Otimização automática desabilitada'}
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'completed_tests': [],
            'applied_optimizations': [],
            'performance_monitoring': {},
            'errors': []
        }
        
        try:
            # 1. Analisar testes completados
            completed_tests = self.analyze_test_completion()
            results['completed_tests'] = completed_tests
            
            # 2. Aplicar otimizações
            for test_result in completed_tests:
                if self.apply_optimization(test_result):
                    results['applied_optimizations'].append(test_result)
                else:
                    results['errors'].append(f"Falha ao aplicar: {test_result['test_name']}")
            
            # 3. Monitorar performance
            performance_data = self.monitor_performance()
            results['performance_monitoring'] = performance_data
            
            # 4. Verificar necessidade de rollback
            if performance_data.get('needs_rollback', False):
                results['errors'].append(f"Performance drop detected: {performance_data['change_percent']}%")
            
            results['status'] = 'success'
            results['message'] = f"Ciclo concluído: {len(results['applied_optimizations'])} otimizações aplicadas"
            
        except Exception as e:
            results['status'] = 'error'
            results['message'] = f"Erro durante ciclo de otimização: {str(e)}"
            results['errors'].append(str(e))
        
        return results
    
    def get_optimization_history(self) -> List[Dict[str, Any]]:
        """Obtém histórico de otimizações aplicadas."""
        try:
            log_file = "data/optimization_log.json"
            
            if Path(log_file).exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
                    return log_data.get('optimizations', [])
            else:
                return []
                
        except Exception as e:
            print(f"Erro ao obter histórico: {e}")
            return []

def main():
    """Função principal para execução standalone."""
    print("🤖 Iniciando Otimizador Automático...")
    
    optimizer = AutoOptimizer()
    results = optimizer.run_optimization_cycle()
    
    print(f"\n📊 Resultados do Ciclo de Otimização:")
    print(f"Status: {results['status']}")
    print(f"Mensagem: {results['message']}")
    print(f"Testes completados: {len(results['completed_tests'])}")
    print(f"Otimizações aplicadas: {len(results['applied_optimizations'])}")
    
    if results['errors']:
        print(f"\n⚠️ Erros encontrados:")
        for error in results['errors']:
            print(f"  - {error}")
    
    performance = results.get('performance_monitoring', {})
    if performance:
        print(f"\n📈 Monitoramento de Performance:")
        print(f"Antes: {performance['before_avg']}%")
        print(f"Depois: {performance['after_avg']}%")
        print(f"Mudança: {performance['change_percent']:+.1f}%")

if __name__ == "__main__":
    main()