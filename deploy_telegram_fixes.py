#!/usr/bin/env python3
"""
🚀 DEPLOY DAS CORREÇÕES DE NOTIFICAÇÕES TELEGRAM
Deploy imediato das correções no Railway
"""

import subprocess
import sys
import time
from datetime import datetime

def log_message(message):
    """Log com timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def execute_command(cmd, description, timeout=60):
    """Executa comando e retorna resultado"""
    log_message(f"🔧 {description}")
    log_message(f"Comando: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        
        if result.returncode == 0:
            log_message("✅ SUCESSO!")
            if result.stdout.strip():
                log_message(f"Output: {result.stdout.strip()}")
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
    """Deploy das correções"""
    log_message("🚀 INICIANDO DEPLOY DAS CORREÇÕES TELEGRAM")
    log_message("=" * 60)
    
    # Verificar se Railway CLI está instalado
    log_message("🔍 Verificando Railway CLI...")
    if not execute_command("railway --version", "Verificando Railway CLI", 10):
        log_message("❌ Railway CLI não encontrado!")
        log_message("📋 Instale com: npm install -g @railway/cli")
        return False
    
    # Fazer login no Railway (se necessário)
    log_message("🔐 Verificando login Railway...")
    if not execute_command("railway whoami", "Verificando login", 10):
        log_message("⚠️ Não logado no Railway")
        log_message("📋 Faça login com: railway login")
        return False
    
    # Verificar projeto Railway
    log_message("📁 Verificando projeto Railway...")
    if not execute_command("railway status", "Verificando projeto", 10):
        log_message("⚠️ Projeto não vinculado")
        log_message("📋 Vincule com: railway link")
        return False
    
    # Deploy das correções
    log_message("🚀 Fazendo deploy das correções...")
    
    deploy_commands = [
        ("git add .", "Adicionando arquivos ao git"),
        ('git commit -m "🔧 Fix: Correção das notificações Telegram - removido except Exception: pass"', "Commitando correções"),
        ("railway up", "Deploy no Railway")
    ]
    
    success_count = 0
    for cmd, description in deploy_commands:
        if execute_command(cmd, description, 120):  # 2 minutos timeout para deploy
            success_count += 1
        else:
            log_message(f"❌ Falha em: {description}")
            break
        log_message("-" * 40)
    
    if success_count == len(deploy_commands):
        log_message("✅ DEPLOY CONCLUÍDO COM SUCESSO!")
        log_message("📋 PRÓXIMOS PASSOS:")
        log_message("1. 🔍 Aguardar próxima execução agendada")
        log_message("2. 📱 Verificar se notificações chegam")
        log_message("3. 📊 Monitorar logs do Railway")
        log_message("4. 🎯 Confirmar funcionamento completo")
        return True
    else:
        log_message("❌ DEPLOY FALHOU!")
        log_message("🔧 Verifique os erros acima e tente novamente")
        return False

if __name__ == "__main__":
    main()