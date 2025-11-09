#!/usr/bin/env python3
"""
🚨 CORREÇÃO EMERGENCIAL - RAILWAY AUTOMATION
Script para restaurar a operação 24/7 configurando todas as variáveis necessárias
"""

import subprocess
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

def log_message(message):
    """Log com timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def run_railway_command(command):
    """Executa comando do Railway CLI"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()
    except Exception as e:
        return False, str(e)

def configure_railway_variables():
    """Configurar todas as variáveis necessárias no Railway (sem segredos no código)"""
    log_message("🚨 INICIANDO CORREÇÃO EMERGENCIAL DO RAILWAY")
    log_message("=" * 60)
    
    # Carregar .env para uso local
    load_dotenv()

    # Variáveis essenciais para funcionamento
    variables = {
        # APIs essenciais
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', ''),
        'RAPIDAPI_KEY': os.getenv('RAPIDAPI_KEY', ''),
        'REPLICATE_TOKEN': os.getenv('REPLICATE_TOKEN', ''),

        # Configurações RapidAPI
        'RAPIDAPI_HOST': os.getenv('RAPIDAPI_HOST', 'instagram-scraper-api2.p.rapidapi.com'),
        'RAPIDAPI_ALT_HOSTS': os.getenv('RAPIDAPI_ALT_HOSTS', 'instagram-scraper.p.rapidapi.com,instagram-scraper-api.p.rapidapi.com,instagram-bulk-scraper-latest.p.rapidapi.com'),

        # Telegram (notificações)
        'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN', ''),
        'TELEGRAM_CHAT_ID': os.getenv('TELEGRAM_CHAT_ID', ''),

        # Configurações do Railway
        'RAILWAY_ENVIRONMENT': os.getenv('RAILWAY_ENVIRONMENT', 'production'),
        'TZ': os.getenv('TZ', 'America/Sao_Paulo'),
        'PYTHONUNBUFFERED': os.getenv('PYTHONUNBUFFERED', '1'),

        # Instagram - Conta Principal
        'INSTAGRAM_BUSINESS_ACCOUNT_ID': os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID_MILTON', ''),
        'INSTAGRAM_ACCESS_TOKEN': os.getenv('INSTAGRAM_ACCESS_TOKEN_MILTON', ''),

        # Database (opcional - Railway pode fornecer automaticamente)
        'POSTGRES_DSN': os.getenv('POSTGRES_DSN', ''),

        # Supabase (opcional)
        'SUPABASE_URL': os.getenv('SUPABASE_URL', ''),
        'SUPABASE_SERVICE_KEY': os.getenv('SUPABASE_SERVICE_KEY', ''),
        'SUPABASE_BUCKET': os.getenv('SUPABASE_BUCKET', '')
    }
    
    log_message(f"🔧 Configurando {len(variables)} variáveis de ambiente...")
    
    success_count = 0
    failed_vars = []
    
    for var_name, var_value in variables.items():
        log_message(f"⚙️ Configurando {var_name}...")
        
        # Comando para definir variável
        command = f'railway variables set {var_name}="{var_value}"'
        success, output = run_railway_command(command)
        
        if success:
            log_message(f"  ✅ {var_name} configurada com sucesso")
            success_count += 1
        else:
            log_message(f"  ❌ Erro ao configurar {var_name}: {output}")
            failed_vars.append(var_name)
    
    # Relatório final
    log_message("=" * 60)
    log_message(f"📊 RELATÓRIO FINAL:")
    log_message(f"  ✅ Variáveis configuradas: {success_count}/{len(variables)}")
    
    if failed_vars:
        log_message(f"  ❌ Variáveis com erro: {len(failed_vars)}")
        for var in failed_vars:
            log_message(f"    - {var}")
    
    if success_count == len(variables):
        log_message("🎉 TODAS AS VARIÁVEIS CONFIGURADAS COM SUCESSO!")
        log_message("🚀 O Railway deve funcionar corretamente agora.")
        return True
    else:
        log_message("⚠️ ALGUMAS VARIÁVEIS FALHARAM - Verifique os erros acima")
        return False

def restart_railway_service():
    """Reiniciar o serviço do Railway para aplicar as mudanças"""
    log_message("🔄 Reiniciando serviço do Railway...")
    
    # Tentar redeploy
    success, output = run_railway_command("railway up --detach")
    
    if success:
        log_message("✅ Serviço reiniciado com sucesso!")
        return True
    else:
        log_message(f"❌ Erro ao reiniciar serviço: {output}")
        return False

def main():
    """Função principal de correção"""
    log_message("🚨 TRAE IA - CORREÇÃO EMERGENCIAL RAILWAY")
    log_message("Restaurando operação 24/7 ininterrupta...")
    log_message("=" * 60)
    
    # Verificar se Railway CLI está instalado
    success, output = run_railway_command("railway --version")
    if not success:
        log_message("❌ Railway CLI não encontrado!")
        log_message("   Instale com: npm install -g @railway/cli")
        log_message("   Depois faça login: railway login")
        return False
    
    log_message(f"✅ Railway CLI encontrado: {output}")
    
    # Configurar variáveis
    if configure_railway_variables():
        log_message("✅ Configuração concluída com sucesso!")
        
        # Reiniciar serviço
        if restart_railway_service():
            log_message("🎯 MISSÃO CUMPRIDA!")
            log_message("   A automação deve voltar a funcionar em alguns minutos.")
            log_message("   Monitore os logs no Railway para confirmar.")
        else:
            log_message("⚠️ Variáveis configuradas, mas falha no restart.")
            log_message("   Faça o redeploy manualmente no Railway.")
    else:
        log_message("❌ FALHA NA CONFIGURAÇÃO!")
        log_message("   Verifique os erros acima e tente novamente.")
    
    log_message("=" * 60)
    log_message("🤖 TRAE IA - Correção finalizada")

if __name__ == "__main__":
    main()