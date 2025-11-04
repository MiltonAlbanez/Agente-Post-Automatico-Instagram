#!/usr/bin/env python3
"""
Sistema de Automação Simplificado para Railway
Versão que funciona sem banco de dados para teste inicial
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
        'INSTAGRAM_BUSINESS_ACCOUNT_ID': 'Instagram Business Account ID'
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

def simulate_post_creation():
    """Simula a criação de um post (sem banco de dados)"""
    log_message("🎨 Simulando criação de post...")
    
    # Simular tempo de processamento
    time.sleep(2)
    
    log_message("✅ Post simulado criado com sucesso!")
    log_message("📝 Conteúdo: Post automático gerado pelo sistema Railway")
    log_message("🏷️ Hashtags: #automacao #railway #instagram")
    
    return True

def run_automation_cycle():
    """Executa um ciclo completo de automação"""
    log_message("🚀 Iniciando ciclo de automação...")
    
    try:
        # Verificar ambiente
        if not check_environment():
            log_message("❌ Ambiente não configurado corretamente")
            return False
        
        # Simular criação de post
        if simulate_post_creation():
            log_message("✅ Ciclo de automação concluído com sucesso!")
            return True
        else:
            log_message("❌ Erro no ciclo de automação")
            return False
            
    except Exception as e:
        log_message(f"❌ Erro no ciclo de automação: {str(e)}")
        return False

def main():
    """Função principal do sistema de automação"""
    log_message("🤖 SISTEMA DE AUTOMAÇÃO RAILWAY - Iniciando...")
    log_message(f"🌍 Ambiente: {os.getenv('RAILWAY_ENVIRONMENT', 'local')}")
    log_message(f"⏰ Horário de início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Configurar agendamentos (horários em UTC para Railway)
    # 6h BRT = 9h UTC, 12h BRT = 15h UTC, 19h BRT = 22h UTC
    schedule.every().day.at("09:00").do(run_automation_cycle)  # 6h BRT
    schedule.every().day.at("15:00").do(run_automation_cycle)  # 12h BRT  
    schedule.every().day.at("22:00").do(run_automation_cycle)  # 19h BRT
    
    # Executar um ciclo imediatamente para teste
    log_message("🔄 Executando ciclo inicial de teste...")
    run_automation_cycle()
    
    log_message("📅 Agendamentos configurados:")
    log_message("  - 09:00 UTC (06:00 BRT) - Post matinal")
    log_message("  - 15:00 UTC (12:00 BRT) - Post do meio-dia")
    log_message("  - 22:00 UTC (19:00 BRT) - Post noturno")
    
    log_message("🔄 Entrando no loop principal...")
    
    # Loop principal
    loop_count = 0
    while True:
        loop_count += 1
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Log a cada 30 minutos (30 iterações de 1 minuto)
        if loop_count % 30 == 1:
            log_message(f"💓 Sistema ativo - Loop #{loop_count}")
            log_message(f"📋 Jobs agendados: {len(schedule.jobs)}")
            log_message(f"⏰ Próxima execução: {schedule.next_run()}")
        
        # Executar tarefas pendentes
        schedule.run_pending()
        
        # Aguardar 1 minuto
        time.sleep(60)

if __name__ == "__main__":
    main()