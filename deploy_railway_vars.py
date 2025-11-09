#!/usr/bin/env python3
"""
Script para configurar variáveis de ambiente nos serviços Stories do Railway
"""

import subprocess
import sys
import json
import os
from dotenv import load_dotenv

# Carregar variáveis do .env (para uso local)
load_dotenv()

"""
Configuração de contas sem segredos em código.
Para cada conta, apontamos os nomes das variáveis de ambiente que devem conter os valores.
Defina estes valores no ambiente (ex.: Railway variables ou arquivo .env local).
"""
ACCOUNTS_ENV_MAP = {
    "milton_albanez": {
        "OPENAI_API_KEY": "OPENAI_API_KEY",
        "INSTAGRAM_ACCESS_TOKEN": "INSTAGRAM_ACCESS_TOKEN_MILTON",
        "INSTAGRAM_BUSINESS_ACCOUNT_ID": "INSTAGRAM_BUSINESS_ACCOUNT_ID_MILTON"
    },
    "albanez_assistencia": {
        "OPENAI_API_KEY": "OPENAI_API_KEY",
        "INSTAGRAM_ACCESS_TOKEN": "INSTAGRAM_ACCESS_TOKEN_ALBANEZ",
        "INSTAGRAM_BUSINESS_ACCOUNT_ID": "INSTAGRAM_BUSINESS_ACCOUNT_ID_ALBANEZ"
    }
}

# Mapeamento de serviços para contas
SERVICES_MAPPING = {
    "Stories 9h": "milton_albanez",
    "Stories 15h": "albanez_assistencia", 
    "Stories 21h": "milton_albanez"
}

def run_command(command):
    """Executa comando e retorna resultado"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_railway_cli():
    """Verifica se Railway CLI está disponível"""
    success, stdout, stderr = run_command("railway --version")
    if success:
        print(f"✅ Railway CLI encontrado: {stdout.strip()}")
        return True
    else:
        print("❌ Railway CLI não encontrado. Instale com: npm install -g @railway/cli")
        return False

def set_environment_variable(service_name, var_name, var_value):
    """Define uma variável de ambiente para um serviço específico"""
    command = f'railway variables --set "{var_name}={var_value}" --service "{service_name}"'
    success, stdout, stderr = run_command(command)
    
    if success:
        print(f"✅ {service_name}: {var_name} configurada")
        return True
    else:
        print(f"❌ {service_name}: Erro ao configurar {var_name}")
        print(f"   Erro: {stderr}")
        return False

def deploy_variables_for_service(service_name, account_key):
    """Deploy das variáveis para um serviço específico (sem segredos no código)"""
    print(f"\n🚀 Configurando variáveis para {service_name} (conta: {account_key})")

    if account_key not in ACCOUNTS_ENV_MAP:
        print(f"❌ Mapeamento não encontrado para conta: {account_key}")
        return False

    env_map = ACCOUNTS_ENV_MAP[account_key]
    success_count = 0
    missing = []

    for var_name, env_var in env_map.items():
        value = os.getenv(env_var)
        if not value:
            missing.append(env_var)
            print(f"❌ {service_name}: variável de ambiente ausente '{env_var}'")
            continue

        if set_environment_variable(service_name, var_name, value):
            success_count += 1

    total_vars = len(env_map)
    if success_count == total_vars:
        print(f"✅ {service_name}: Todas as {total_vars} variáveis configuradas com sucesso!")
        return True
    else:
        if missing:
            print(f"⚠️ {service_name}: variáveis ausentes: {', '.join(missing)}")
        print(f"⚠️ {service_name}: {success_count}/{total_vars} variáveis configuradas")
        return False

def main():
    """Função principal"""
    print("🔧 Deploy de Variáveis de Ambiente - Railway Stories Services")
    print("=" * 60)
    
    # Verificar Railway CLI
    if not check_railway_cli():
        sys.exit(1)
    
    # Deploy para cada serviço
    success_services = []
    failed_services = []
    
    for service_name, account_key in SERVICES_MAPPING.items():
        if deploy_variables_for_service(service_name, account_key):
            success_services.append(service_name)
        else:
            failed_services.append(service_name)
    
    # Relatório final
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO FINAL")
    print("=" * 60)
    
    if success_services:
        print(f"✅ Serviços configurados com sucesso: {', '.join(success_services)}")
    
    if failed_services:
        print(f"❌ Serviços com problemas: {', '.join(failed_services)}")
        print("\n💡 Dicas para resolver problemas:")
        print("   1. Verifique se você está logado no Railway: railway login")
        print("   2. Verifique se os nomes dos serviços estão corretos")
        print("   3. Verifique se você tem permissões no projeto")
    
    if not failed_services:
        print("\n🎉 DEPLOY CONCLUÍDO COM SUCESSO!")
        print("   Os Stories das 15h agora devem funcionar corretamente.")
        print("   Próxima execução: hoje às 15:00 BRT")
    
    return len(failed_services) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)