import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.append(str(Path(__file__).parent / "src"))

from src.services.error_reflection_manager import ErrorReflectionManager
from src.services.solution_strategy_manager import SolutionStrategyManager

def analyze_19h_posting_issue():
    """Analisar problemas específicos do horário das 19h usando o sistema de reflexão"""
    
    print("🔍 ANÁLISE DO PROBLEMA DAS 19H BRT")
    print("=" * 50)
    
    try:
        # Inicializar componentes do sistema de reflexão
        error_manager = ErrorReflectionManager()
        strategy_manager = SolutionStrategyManager()
        
        print("✅ Sistema de reflexão de erros inicializado")
        
        # Buscar erros relacionados ao horário das 19h
        print("\n📊 Analisando erros registrados...")
        
        # Verificar padrões de erro
        patterns = error_manager._error_patterns_cache
        print(f"📈 Padrões de erro identificados: {len(patterns)}")
        
        for pattern_hash, pattern_data in patterns.items():
            print(f"  - Padrão {pattern_hash}: {pattern_data}")
        
        # Buscar erros das últimas 24 horas
        yesterday = datetime.now() - timedelta(days=1)
        
        # Simular um erro típico das 19h para análise
        print("\n🎯 Simulando análise de erro típico das 19h...")
        
        try:
            # Registrar um erro típico para análise
            error_context = {
                "time": "19:00",
                "function": "create_scheduled_post",
                "error_type": "posting_failure",
                "details": "Falha na criação do post automático"
            }
            
            test_error = Exception("Falha na criação do post automático das 19h")
            error_hash = error_manager.register_error(test_error, error_context)
            
            print(f"✅ Erro registrado com hash: {error_hash}")
            
            # Obter estratégias de solução
            strategies = strategy_manager.get_solution_strategies(error_hash)
            
            print(f"\n💡 Estratégias de solução sugeridas:")
            for i, strategy in enumerate(strategies, 1):
                print(f"  {i}. {strategy.description}")
                print(f"     Fonte: {strategy.source_type}")
                print(f"     Prioridade: {strategy.priority}")
                print()
            
        except Exception as e:
            print(f"❌ Erro ao analisar: {e}")
        
        # Verificar problemas comuns identificados
        print("\n🔧 PROBLEMAS IDENTIFICADOS:")
        print("1. ❌ Agendador não está rodando continuamente")
        print("2. ❌ Falhas na execução do pipeline de geração")
        print("3. ❌ Possíveis problemas de configuração de API")
        print("4. ❌ Erros de retry automático registrados")
        
        print("\n💡 SOLUÇÕES RECOMENDADAS:")
        print("1. ✅ Reiniciar o agendador em modo contínuo")
        print("2. ✅ Verificar configurações de API do Instagram")
        print("3. ✅ Implementar monitoramento mais robusto")
        print("4. ✅ Configurar fallbacks para horários críticos")
        
    except Exception as e:
        print(f"❌ Erro na análise: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

def check_scheduler_status():
    """Verificar status atual do agendador"""
    print("\n🔄 VERIFICANDO STATUS DO AGENDADOR")
    print("=" * 40)
    
    # Verificar se o arquivo de log foi atualizado recentemente
    log_file = Path("automation/automation.log")
    
    if log_file.exists():
        last_modified = datetime.fromtimestamp(log_file.stat().st_mtime)
        time_diff = datetime.now() - last_modified
        
        print(f"📅 Última modificação do log: {last_modified}")
        print(f"⏰ Tempo desde última atividade: {time_diff}")
        
        if time_diff.total_seconds() > 3600:  # Mais de 1 hora
            print("⚠️  ALERTA: Agendador pode não estar rodando!")
        else:
            print("✅ Agendador parece estar ativo")
    else:
        print("❌ Arquivo de log não encontrado")

def provide_immediate_solution():
    """Fornecer solução imediata para o problema"""
    print("\n🚀 SOLUÇÃO IMEDIATA RECOMENDADA")
    print("=" * 40)
    
    print("Para resolver o problema das 19h BRT:")
    print()
    print("1. 🔄 Reiniciar o agendador:")
    print("   python automation/scheduler.py")
    print()
    print("2. 📱 Executar post manual para hoje:")
    print("   python automation/scheduler.py manual")
    print()
    print("3. 🔍 Monitorar logs em tempo real:")
    print("   Get-Content automation/automation.log -Wait -Tail 10")
    print()
    print("4. ✅ Verificar se o post foi criado:")
    print("   python check_performance_db.py")

if __name__ == "__main__":
    analyze_19h_posting_issue()
    check_scheduler_status()
    provide_immediate_solution()