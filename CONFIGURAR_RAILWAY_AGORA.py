#!/usr/bin/env python3
"""
🚨 CONFIGURAÇÃO IMEDIATA DAS CREDENCIAIS RAILWAY 🚨
EXECUTA AGORA MESMO - SEM MAIS PERDA DE TEMPO!
"""

import json
import subprocess
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

def log_message(message):
    """Log com timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def execute_command(cmd, description):
    """Executa comando e retorna resultado"""
    log_message(f"🔧 {description}")
    log_message(f"Comando: {cmd[:60]}...")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            log_message("✅ SUCESSO!")
            return True
        else:
            log_message(f"❌ ERRO: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        log_message("❌ TIMEOUT!")
        return False
    except Exception as e:
        log_message(f"❌ EXCEÇÃO: {e}")
        return False

def main():
    """Configuração imediata"""
    log_message("🚀 INICIANDO CONFIGURAÇÃO IMEDIATA DAS CREDENCIAIS")
    log_message("=" * 60)
    
    # Carregar .env para uso local
    load_dotenv()

    # Carregar credenciais
    try:
        with open('CREDENCIAIS_PERMANENTES.json', 'r', encoding='utf-8') as f:
            credenciais = json.load(f)
        log_message("✅ Credenciais carregadas do arquivo permanente")
    except Exception as e:
        log_message(f"❌ ERRO ao carregar credenciais: {e}")
        return False
    
    # Comandos Railway (valores vindos do ambiente)
    commands = [
        (f'railway variables set OPENAI_API_KEY="{os.getenv("OPENAI_API_KEY", "")}"', 
         "Configurando OPENAI_API_KEY"),

        (f'railway variables set RAPIDAPI_KEY="{os.getenv("RAPIDAPI_KEY", "")}"', 
         "Configurando RAPIDAPI_KEY"),

        (f'railway variables set REPLICATE_TOKEN="{os.getenv("REPLICATE_TOKEN", "")}"', 
         "Configurando REPLICATE_TOKEN"),

        (f'railway variables set RAPIDAPI_HOST="{os.getenv("RAPIDAPI_HOST", "instagram-scraper-api2.p.rapidapi.com")}"', 
         "Configurando RAPIDAPI_HOST"),

        (f'railway variables set RAPIDAPI_ALT_HOSTS="{os.getenv("RAPIDAPI_ALT_HOSTS", "instagram-scraper.p.rapidapi.com,instagram-scraper-api.p.rapidapi.com,instagram-bulk-scraper-latest.p.rapidapi.com")}"', 
         "Configurando RAPIDAPI_ALT_HOSTS"),

        (f'railway variables set INSTAGRAM_BUSINESS_ACCOUNT_ID="{os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID_MILTON", "")}"', 
         "Configurando INSTAGRAM_BUSINESS_ACCOUNT_ID (Milton)"),

        (f'railway variables set INSTAGRAM_ACCESS_TOKEN="{os.getenv("INSTAGRAM_ACCESS_TOKEN_MILTON", "")}"', 
         "Configurando INSTAGRAM_ACCESS_TOKEN (Milton)"),

        (f'railway variables set TELEGRAM_BOT_TOKEN="{os.getenv("TELEGRAM_BOT_TOKEN", "")}"', 
         "Configurando TELEGRAM_BOT_TOKEN"),

        (f'railway variables set TELEGRAM_CHAT_ID="{os.getenv("TELEGRAM_CHAT_ID", "")}"', 
         "Configurando TELEGRAM_CHAT_ID"),

        (f'railway variables set RAILWAY_ENVIRONMENT="{os.getenv("RAILWAY_ENVIRONMENT", "production")}"', 
         "Configurando RAILWAY_ENVIRONMENT"),

        (f'railway variables set TZ="{os.getenv("TZ", "America/Sao_Paulo")}"', 
         "Configurando TZ"),

        (f'railway variables set PYTHONUNBUFFERED="{os.getenv("PYTHONUNBUFFERED", "1")}"', 
         "Configurando PYTHONUNBUFFERED")
    ]
    
    # Executar todos os comandos
    success_count = 0
    total_commands = len(commands)
    
    for cmd, description in commands:
        if execute_command(cmd, description):
            success_count += 1
        log_message("-" * 40)
    
    # Resultado
    log_message("=" * 60)
    log_message(f"📊 RESULTADO: {success_count}/{total_commands} comandos executados com sucesso")
    
    if success_count == total_commands:
        log_message("🎉 TODAS AS CREDENCIAIS CONFIGURADAS COM SUCESSO!")
        
        # Redeploy
        log_message("🚀 Fazendo redeploy do serviço...")
        if execute_command('railway up --detach', "Redeploy do serviço"):
            log_message("✅ REDEPLOY CONCLUÍDO!")
            log_message("🎯 SISTEMA DEVE ESTAR FUNCIONANDO AGORA!")
        else:
            log_message("⚠️ Redeploy falhou - fazer manualmente")
        
        return True
    else:
        log_message("❌ ALGUMAS CONFIGURAÇÕES FALHARAM!")
        log_message("🔧 Verificar erros acima e tentar novamente")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n" + "="*60)
        print("🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
        print("🎯 O sistema deve estar funcionando agora!")
        print("📱 Verificar logs do Railway para confirmar")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ CONFIGURAÇÃO FALHOU!")
        print("🔧 Verificar erros e tentar novamente")
        print("="*60)
    
    sys.exit(0 if success else 1)