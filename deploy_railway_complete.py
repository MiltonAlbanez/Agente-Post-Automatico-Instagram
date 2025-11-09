#!/usr/bin/env python3
"""
Script para configurar todas as variáveis de ambiente no Railway
Para deploy completo do sistema de automação 24/7
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv

def load_accounts():
    """Carregar contas do accounts.json"""
    try:
        accounts_file = Path(__file__).parent / "accounts.json"
        with open(accounts_file, 'r', encoding='utf-8') as f:
            accounts = json.load(f)
        print(f"✅ Carregado accounts.json com {len(accounts)} contas")
        return accounts
    except Exception as e:
        print(f"❌ Erro ao carregar accounts.json: {e}")
        return []

def load_config():
    """Carregar configuração principal de variáveis de ambiente (sem segredos em código)"""
    try:
        # Carregar .env para uso local
        load_dotenv()
        # Configurações lidas do ambiente
        return {
            'TELEGRAM_CHAT_ID': os.getenv('TELEGRAM_CHAT_ID', ''),
            'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN', ''),
            'RAPIDAPI_KEY': os.getenv('RAPIDAPI_KEY', ''),
            'RAPIDAPI_HOST': os.getenv('RAPIDAPI_HOST', 'instagram-scraper-api2.p.rapidapi.com'),
            'RAPIDAPI_ALT_HOSTS': os.getenv('RAPIDAPI_ALT_HOSTS', 'instagram-scraper.p.rapidapi.com,instagram-scraper-api.p.rapidapi.com,instagram-bulk-scraper-latest.p.rapidapi.com'),
            'REPLICATE_TOKEN': os.getenv('REPLICATE_TOKEN', ''),
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', ''),
            'POSTGRES_DSN': os.getenv('POSTGRES_DSN', ''),
            'SUPABASE_URL': os.getenv('SUPABASE_URL', ''),
            'SUPABASE_SERVICE_KEY': os.getenv('SUPABASE_SERVICE_KEY', ''),
            'SUPABASE_BUCKET': os.getenv('SUPABASE_BUCKET', '')
        }
    except Exception as e:
        print(f"❌ Erro ao carregar config: {e}")
        return {}

def generate_railway_env_commands():
    """Gerar comandos para configurar variáveis no Railway"""
    print("🚀 CONFIGURAÇÃO DE VARIÁVEIS DE AMBIENTE PARA RAILWAY")
    print("=" * 60)
    
    # Carregar contas
    accounts = load_accounts()
    if not accounts:
        print("❌ Não foi possível carregar as contas!")
        return
    
    # Carregar configuração
    config = load_config()
    
    print("\n📋 COMANDOS PARA EXECUTAR NO TERMINAL DO RAILWAY:")
    print("=" * 60)
    print("# Copie e cole estes comandos no terminal do Railway CLI\n")
    
    # Variáveis básicas do sistema
    print("# === VARIÁVEIS BÁSICAS DO SISTEMA ===")
    for key, value in config.items():
        print(f'railway variables set {key}="{value}"')
    
    print("\n# === CONFIGURAÇÕES ESPECÍFICAS ===")
    print('railway variables set RAILWAY_ENVIRONMENT="production"')
    print('railway variables set TZ="America/Sao_Paulo"')
    print('railway variables set PYTHONUNBUFFERED="1"')
    
    # Variáveis das contas (usar a primeira conta como padrão para compatibilidade)
    if accounts:
        primary_account = accounts[0]
        print(f"\n# === CONTA PRINCIPAL ({primary_account['nome']}) ===")
        print(f'railway variables set INSTAGRAM_BUSINESS_ACCOUNT_ID="{primary_account["instagram_id"]}"')
        print(f'railway variables set INSTAGRAM_ACCESS_TOKEN="{primary_account["instagram_access_token"]}"')
    
    print("\n" + "=" * 60)
    print("📝 INSTRUÇÕES:")
    print("1. Instale o Railway CLI: npm install -g @railway/cli")
    print("2. Faça login: railway login")
    print("3. Conecte ao seu projeto: railway link")
    print("4. Execute os comandos acima um por um")
    print("5. Faça o deploy: railway up")
    print("\n✅ Após configurar, o sistema funcionará 24/7 automaticamente!")
    
    # Salvar comandos em arquivo
    commands_file = Path(__file__).parent / "railway_env_commands.txt"
    with open(commands_file, 'w', encoding='utf-8') as f:
        f.write("# COMANDOS PARA CONFIGURAR VARIÁVEIS NO RAILWAY\n")
        f.write("# Execute estes comandos no terminal após instalar Railway CLI\n\n")
        
        f.write("# === VARIÁVEIS BÁSICAS DO SISTEMA ===\n")
        for key, value in config.items():
            f.write(f'railway variables set {key}="{value}"\n')
        
        f.write("\n# === CONFIGURAÇÕES ESPECÍFICAS ===\n")
        f.write('railway variables set RAILWAY_ENVIRONMENT="production"\n')
        f.write('railway variables set TZ="America/Sao_Paulo"\n')
        f.write('railway variables set PYTHONUNBUFFERED="1"\n')
        
        if accounts:
            primary_account = accounts[0]
            f.write(f"\n# === CONTA PRINCIPAL ({primary_account['nome']}) ===\n")
            f.write(f'railway variables set INSTAGRAM_BUSINESS_ACCOUNT_ID="{primary_account["instagram_id"]}"\n')
            f.write(f'railway variables set INSTAGRAM_ACCESS_TOKEN="{primary_account["instagram_access_token"]}"\n')
    
    print(f"\n💾 Comandos salvos em: {commands_file}")

def show_deployment_guide():
    """Mostrar guia completo de deploy"""
    print("\n🚀 GUIA COMPLETO DE DEPLOY NO RAILWAY")
    print("=" * 60)
    
    print("\n📋 PASSO A PASSO:")
    print("1. 📦 Instalar Railway CLI:")
    print("   npm install -g @railway/cli")
    
    print("\n2. 🔐 Fazer login no Railway:")
    print("   railway login")
    
    print("\n3. 🔗 Conectar ao projeto:")
    print("   railway link")
    print("   (ou criar novo: railway init)")
    
    print("\n4. ⚙️ Configurar variáveis de ambiente:")
    print("   Execute os comandos do arquivo railway_env_commands.txt")
    
    print("\n5. 🚀 Fazer deploy:")
    print("   railway up")
    
    print("\n6. ✅ Verificar funcionamento:")
    print("   railway logs")
    
    print("\n🎯 RESULTADO ESPERADO:")
    print("- Sistema rodando 24/7 na nuvem")
    print("- Posts automáticos nos horários programados")
    print("- Processamento de múltiplas contas")
    print("- Logs em tempo real disponíveis")
    
    print("\n⏰ HORÁRIOS DE POSTAGEM (BRT):")
    print("📝 FEED: 06:00, 12:00, 19:00")
    print("📱 STORIES: 09:00, 15:00, 21:00")

if __name__ == "__main__":
    generate_railway_env_commands()
    show_deployment_guide()