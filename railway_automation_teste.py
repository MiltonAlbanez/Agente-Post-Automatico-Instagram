#!/usr/bin/env python3
"""
Sistema de Automação para Teste às 20:35 BRT (23:35 UTC)
Versão específica para teste do serviço "teste 20:15"
"""

import os
import time
import schedule
from datetime import datetime
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

def log_message(message):
    """Log com timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def check_environment():
    """Verifica se as variáveis de ambiente estão configuradas"""
    log_message("🔍 Verificando variáveis de ambiente...")
    
    required_vars = {
        'OPENAI_API_KEY': 'OpenAI API',
        'INSTAGRAM_ACCESS_TOKEN': 'Instagram Access Token',
        'INSTAGRAM_BUSINESS_ACCOUNT_ID': 'Instagram Business Account ID',
        'AUTOCMD': 'Comando de automação'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"  ❌ {var} ({description})")
        else:
            log_message(f"  ✅ {var} configurada")
    
    if missing_vars:
        log_message("⚠️ Variáveis faltando:")
        for var in missing_vars:
            log_message(var)
        return False
    
    log_message("✅ Todas as variáveis necessárias estão configuradas!")
    return True

def execute_real_autopost():
    """Executa o multirun real usando o sistema principal"""
    log_message("🎨 Executando multirun real...")
    
    try:
        import subprocess
        
        # Executar o comando real de multirun
        cmd = [sys.executable, "src/main.py", "multirun", "--limit", "1", "--only", "Milton_Albanez"]
        log_message(f"🔧 Executando comando: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos timeout
        )
        
        if result.returncode == 0:
            log_message("✅ Multirun executado com sucesso!")
            log_message(f"📝 Output: {result.stdout}")
            return True
        else:
            log_message(f"❌ Erro no multirun: {result.stderr}")
            return False
        
    except subprocess.TimeoutExpired:
        log_message("⏰ Timeout na execução do autopost")
        return False
    except Exception as e:
        log_message(f"❌ Erro na execução: {str(e)}")
        return False

def run_automation_cycle():
    """Executa um ciclo completo de automação"""
    try:
        log_message("🚀 Iniciando ciclo de automação...")
        
        # Verificar ambiente
        if not check_environment():
            log_message("❌ Ambiente não configurado corretamente")
            return False
        
        # Verificar se é comando de autopost
        autocmd = os.getenv('AUTOCMD', '').lower()
        if autocmd != 'autopost':
            log_message(f"⚠️ AUTOCMD não é 'autopost': {autocmd}")
            return False
        
        # Executar multirun real
        if execute_real_autopost():
            log_message("✅ Ciclo de automação concluído com sucesso!")
            log_message("🎯 TESTE ÀS 20:35 BRT EXECUTADO COM SUCESSO!")
            return True
        else:
            log_message("❌ Erro no ciclo de automação")
            return False
            
    except Exception as e:
        log_message(f"❌ Erro no ciclo de automação: {str(e)}")
        return False

def main():
    """Função principal do sistema de automação"""
    log_message("🤖 SISTEMA DE AUTOMAÇÃO TESTE 20:35 - Iniciando...")
    log_message(f"🌍 Ambiente: {os.getenv('RAILWAY_ENVIRONMENT', 'local')}")
    log_message(f"⏰ Horário de início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Configurar agendamento para teste às 20:35 BRT (23:35 UTC)
    schedule.every().day.at("23:35").do(run_automation_cycle)  # 20:35 BRT
    
    # Executar um ciclo imediatamente para teste
    log_message("🔄 Executando ciclo inicial de teste...")
    run_automation_cycle()
    
    log_message("📅 Agendamento configurado:")
    log_message("  - 23:35 UTC (20:35 BRT) - Post de teste")
    
    log_message("🔄 Entrando no loop principal...")
    
    # Loop principal
    loop_count = 0
    while True:
        loop_count += 1
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Log a cada 5 minutos para teste
        if loop_count % 5 == 1:
            log_message(f"💓 Sistema ativo - Loop #{loop_count}")
            log_message(f"📋 Jobs agendados: {len(schedule.jobs)}")
            if schedule.jobs:
                log_message(f"⏰ Próxima execução: {schedule.next_run()}")
        
        # Executar tarefas pendentes
        schedule.run_pending()
        
        # Aguardar 1 minuto
        time.sleep(60)

if __name__ == "__main__":
    main()