"""
Script Principal para Executar o Sistema de Automação
Ponto de entrada para todas as funcionalidades de automação
"""

import sys
import argparse
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

from automation.scheduler import AutomationScheduler
from automation.automation_dashboard import main as run_dashboard

def main():
    parser = argparse.ArgumentParser(description="Sistema de Automação para Posts do Instagram")
    parser.add_argument(
        "command",
        choices=["start", "manual", "dashboard", "config", "status"],
        help="Comando a ser executado"
    )
    parser.add_argument(
        "--config-file",
        help="Arquivo de configuração personalizado"
    )
    
    args = parser.parse_args()
    
    if args.command == "start":
        print("🤖 Iniciando sistema de automação...")
        scheduler = AutomationScheduler()
        scheduler.run_scheduler()
        
    elif args.command == "manual":
        print("🔄 Executando ciclo manual...")
        scheduler = AutomationScheduler()
        scheduler.run_manual_cycle()
        print("✅ Ciclo manual concluído!")
        
    elif args.command == "dashboard":
        print("📊 Iniciando dashboard de automação...")
        run_dashboard()
        
    elif args.command == "config":
        print("⚙️ Configurações atuais:")
        scheduler = AutomationScheduler()
        import json
        print(json.dumps(scheduler.config, indent=2, ensure_ascii=False))
        
    elif args.command == "status":
        print("📈 Status do sistema:")
        from automation.consistency_manager import ConsistencyManager
        manager = ConsistencyManager()
        report = manager.get_consistency_report()
        import json
        print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()