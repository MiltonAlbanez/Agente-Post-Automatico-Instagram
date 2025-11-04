#!/usr/bin/env python3
"""
Script de Execução do Otimizador Automático
Executa o ciclo de otimização automática baseado em testes A/B.
"""

import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent.parent / "src"))

def setup_logging():
    """Configura logging para o otimizador."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "optimization.log"),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("AutoOptimizer")

def load_optimization_config():
    """Carrega configurações de otimização."""
    config_file = "config/optimization_config.json"
    
    default_config = {
        "enabled": True,
        "min_confidence": 85,
        "min_sample_size": 30,
        "min_duration_days": 5,
        "check_interval_hours": 24,
        "performance_monitoring_days": 7,
        "rollback_threshold": -10
    }
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return {**default_config, **config}
    except FileNotFoundError:
        # Criar arquivo de configuração padrão
        Path(config_file).parent.mkdir(exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2)
        return default_config

def run_optimization_cycle(logger):
    """Executa um ciclo completo de otimização."""
    try:
        from services.auto_optimizer import AutoOptimizer
        
        logger.info("Iniciando ciclo de otimização automática")
        
        optimizer = AutoOptimizer()
        results = optimizer.run_optimization_cycle()
        
        logger.info(f"Status: {results['status']}")
        logger.info(f"Mensagem: {results['message']}")
        logger.info(f"Testes completados: {len(results['completed_tests'])}")
        logger.info(f"Otimizações aplicadas: {len(results['applied_optimizations'])}")
        
        if results['errors']:
            logger.warning("Erros encontrados durante a otimização:")
            for error in results['errors']:
                logger.warning(f"  - {error}")
        
        # Log das otimizações aplicadas
        for opt in results['applied_optimizations']:
            logger.info(f"Otimização aplicada: {opt['test_name']} -> {opt['winner']} (+{opt['lift']}%)")
        
        # Monitoramento de performance
        performance = results.get('performance_monitoring', {})
        if performance:
            change = performance.get('change_percent', 0)
            if change > 0:
                logger.info(f"Performance melhorou: +{change:.1f}%")
            elif change < -5:
                logger.warning(f"Performance diminuiu: {change:.1f}%")
        
        return results
        
    except ImportError:
        logger.error("Módulos de otimização não encontrados. Execute em ambiente completo.")
        return None
    except Exception as e:
        logger.error(f"Erro durante otimização: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def check_last_optimization():
    """Verifica quando foi a última otimização."""
    log_file = "data/optimization_log.json"
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        if history:
            last_opt = history[-1]
            last_time = datetime.strptime(last_opt['timestamp'], '%Y-%m-%d %H:%M:%S')
            return last_time
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        pass
    
    return None

def should_run_optimization(config, logger):
    """Determina se deve executar otimização baseado na configuração."""
    if not config.get('enabled', True):
        logger.info("Otimização automática desabilitada")
        return False
    
    last_optimization = check_last_optimization()
    
    if last_optimization:
        hours_since = (datetime.now() - last_optimization).total_seconds() / 3600
        interval = config.get('check_interval_hours', 24)
        
        if hours_since < interval:
            logger.info(f"Última otimização há {hours_since:.1f}h. Próxima em {interval - hours_since:.1f}h")
            return False
    
    return True

def generate_optimization_report(results):
    """Gera relatório de otimização."""
    if not results:
        return
    
    report_file = f"reports/optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    Path(report_file).parent.mkdir(exist_ok=True)
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'status': results['status'],
        'summary': {
            'completed_tests': len(results['completed_tests']),
            'applied_optimizations': len(results['applied_optimizations']),
            'errors': len(results['errors'])
        },
        'optimizations': results['applied_optimizations'],
        'performance_impact': results.get('performance_monitoring', {}),
        'errors': results['errors']
    }
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return report_file

def main():
    """Função principal."""
    logger = setup_logging()
    
    logger.info("OTIMIZADOR AUTOMÁTICO - INICIANDO")
    logger.info("=" * 50)
    
    try:
        # Carregar configurações
        config = load_optimization_config()
        logger.info(f"Configurações carregadas: {config}")
        
        # Verificar se deve executar
        if not should_run_optimization(config, logger):
            return
        
        # Executar otimização
        results = run_optimization_cycle(logger)
        
        if results:
            # Gerar relatório
            report_file = generate_optimization_report(results)
            if report_file:
                logger.info(f"Relatório gerado: {report_file}")
            
            # Resumo final
            logger.info("=" * 50)
            logger.info("OTIMIZAÇÃO CONCLUÍDA")
            
            if results['applied_optimizations']:
                total_lift = sum(opt['lift'] for opt in results['applied_optimizations'])
                avg_lift = total_lift / len(results['applied_optimizations'])
                logger.info(f"Melhoria média estimada: +{avg_lift:.1f}%")
            
            logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"Erro crítico: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()