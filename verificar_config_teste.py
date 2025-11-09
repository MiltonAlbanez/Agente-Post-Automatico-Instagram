#!/usr/bin/env python3
"""
Script para verificar se as configurações do Railway estão corretas
para o serviço de teste 20:15
"""

import os
import subprocess
from dotenv import load_dotenv
import json

def get_railway_variables():
    """Obtém as variáveis do Railway diretamente"""
    try:
        result = subprocess.run(['railway', 'variables', '--json'], 
                              capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except:
        return {}

def verificar_configuracoes():
    """Verifica se todas as configurações necessárias estão presentes"""
    print("🔍 VERIFICANDO CONFIGURAÇÕES DO RAILWAY")
    print("=" * 50)
    
    # Carregar variáveis de ambiente locais
    load_dotenv()
    
    # Obter variáveis do Railway
    railway_vars = get_railway_variables()
    
    # Função para obter variável (prioriza Railway, depois local)
    def get_var(key):
        return railway_vars.get(key) or os.getenv(key)
    
    # Criar objeto cfg compatível
    cfg = {}
    for key in os.environ:
        cfg[key] = get_var(key)
    
    try:
        print("✅ Configurações carregadas com sucesso")
    except Exception as e:
        print(f"❌ Erro ao carregar configurações: {e}")
        return False
    
    # Variáveis obrigatórias
    variaveis_obrigatorias = {
        'INSTAGRAM_BUSINESS_ACCOUNT_ID': 'Instagram Business Account ID',
        'INSTAGRAM_ACCESS_TOKEN': 'Instagram Access Token',
        'OPENAI_API_KEY': 'OpenAI API Key',
        'RAPIDAPI_KEY': 'RapidAPI Key',
        'REPLICATE_TOKEN': 'Replicate Token',
        'POSTGRES_DSN': 'PostgreSQL DSN (ou DATABASE_URL)'
    }
    
    # Variáveis opcionais (recomendadas)
    variaveis_opcionais = {
        'TELEGRAM_BOT_TOKEN': 'Telegram Bot Token',
        'TELEGRAM_CHAT_ID': 'Telegram Chat ID',
        'SUPABASE_URL': 'Supabase URL',
        'SUPABASE_SERVICE_KEY': 'Supabase Service Key',
        'SUPABASE_BUCKET': 'Supabase Bucket'
    }
    
    print("\n📋 VERIFICAÇÃO DE VARIÁVEIS OBRIGATÓRIAS:")
    print("-" * 50)
    
    todas_obrigatorias_ok = True
    for var, descricao in variaveis_obrigatorias.items():
        valor = get_var(var) or ""
        if valor and valor.strip():
            # Mascarar valores sensíveis
            if len(valor) > 20:
                valor_mascarado = valor[:10] + "..." + valor[-5:]
            else:
                valor_mascarado = valor[:5] + "..." if len(valor) > 5 else valor
            print(f"  ✅ {var}: {valor_mascarado}")
        else:
            print(f"  ❌ {var}: AUSENTE")
            todas_obrigatorias_ok = False
    
    print(f"\n📋 VERIFICAÇÃO DE VARIÁVEIS OPCIONAIS:")
    print("-" * 50)
    
    opcionais_configuradas = 0
    for var, descricao in variaveis_opcionais.items():
        valor = get_var(var) or ""
        if valor and valor.strip():
            if len(valor) > 20:
                valor_mascarado = valor[:10] + "..." + valor[-5:]
            else:
                valor_mascarado = valor[:5] + "..." if len(valor) > 5 else valor
            print(f"  ✅ {var}: {valor_mascarado}")
            opcionais_configuradas += 1
        else:
            print(f"  ⚠️ {var}: NÃO CONFIGURADA")
    
    # Verificar AUTOCMD
    print(f"\n🔧 VERIFICAÇÃO DE COMANDO:")
    print("-" * 50)
    autocmd = get_var("AUTOCMD") or ""
    if autocmd == "autopost":
        print(f"  ✅ AUTOCMD: {autocmd} (correto para Feed)")
    elif autocmd == "autopost --stories":
        print(f"  ✅ AUTOCMD: {autocmd} (correto para Stories)")
    elif autocmd:
        print(f"  ⚠️ AUTOCMD: {autocmd} (valor inesperado)")
    else:
        print(f"  ❌ AUTOCMD: NÃO CONFIGURADO")
    
    # Verificar configurações específicas
    print(f"\n⚙️ VERIFICAÇÕES ESPECÍFICAS:")
    print("-" * 50)
    
    # RapidAPI Host
    rapidapi_host = get_var("RAPIDAPI_HOST") or ""
    if rapidapi_host:
        print(f"  ✅ RAPIDAPI_HOST: {rapidapi_host}")
    else:
        print(f"  ⚠️ RAPIDAPI_HOST: Usando padrão (instagram-scraper-api2.p.rapidapi.com)")
    
    # Database
    postgres_dsn = get_var("POSTGRES_DSN") or ""
    if postgres_dsn:
        if "railway" in postgres_dsn:
            print(f"  ✅ DATABASE: Conectado ao Railway PostgreSQL")
        else:
            print(f"  ✅ DATABASE: Configurado (externo)")
    else:
        print(f"  ❌ DATABASE: Não configurado")
    
    # Resumo final
    print(f"\n📊 RESUMO DA VERIFICAÇÃO:")
    print("=" * 50)
    
    if todas_obrigatorias_ok:
        print("✅ TODAS AS VARIÁVEIS OBRIGATÓRIAS: CONFIGURADAS")
    else:
        print("❌ VARIÁVEIS OBRIGATÓRIAS: FALTANDO ALGUMAS")
    
    print(f"ℹ️ VARIÁVEIS OPCIONAIS: {opcionais_configuradas}/{len(variaveis_opcionais)} configuradas")
    
    if autocmd in ["autopost", "autopost --stories"]:
        print("✅ COMANDO AUTOCMD: CONFIGURADO CORRETAMENTE")
    else:
        print("❌ COMANDO AUTOCMD: PRECISA SER CONFIGURADO")
    
    # Status geral
    print(f"\n🎯 STATUS GERAL:")
    print("=" * 50)
    
    if todas_obrigatorias_ok and autocmd in ["autopost", "autopost --stories"]:
        print("🟢 CONFIGURAÇÃO: PRONTA PARA TESTE!")
        print("   Você pode executar um teste manual ou aguardar o cron.")
        return True
    else:
        print("🟡 CONFIGURAÇÃO: PRECISA DE AJUSTES")
        print("   Verifique as variáveis marcadas com ❌ acima.")
        return False

if __name__ == "__main__":
    verificar_configuracoes()