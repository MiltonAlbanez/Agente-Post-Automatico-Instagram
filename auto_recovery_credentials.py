#!/usr/bin/env python3
"""
🚨 SISTEMA DE AUTO-RECUPERAÇÃO DE CREDENCIAIS 🚨
NUNCA MAIS PERDER CREDENCIAIS NO RAILWAY!

Este script:
1. Verifica se as credenciais estão configuradas no Railway
2. Se não estiverem, automaticamente as restaura
3. Envia notificação no Telegram sobre o status
4. Registra logs detalhados
"""

import json
import os
import subprocess
import sys
import requests
from datetime import datetime
from pathlib import Path

class CredentialsAutoRecovery:
    def __init__(self):
        self.credentials_file = "CREDENCIAIS_PERMANENTES.json"
        self.log_file = "auto_recovery.log"
        self.credentials = self.load_credentials()
        
    def load_credentials(self):
        """Carrega credenciais do arquivo permanente"""
        try:
            with open(self.credentials_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.log_error(f"❌ ERRO CRÍTICO: Arquivo {self.credentials_file} não encontrado!")
            return None
    
    def log_message(self, message):
        """Registra mensagem no log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
    
    def log_error(self, message):
        """Registra erro no log"""
        self.log_message(f"🚨 ERRO: {message}")
    
    def send_telegram_notification(self, message):
        """Envia notificação via Telegram"""
        try:
            if not self.credentials:
                return False
                
            bot_token = self.credentials['railway_environment_variables']['TELEGRAM_BOT_TOKEN']
            chat_id = self.credentials['railway_environment_variables']['TELEGRAM_CHAT_ID']
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': f"🤖 AUTO-RECOVERY SYSTEM\n\n{message}",
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            self.log_error(f"Falha ao enviar notificação Telegram: {e}")
            return False
    
    def check_railway_variables(self):
        """Verifica se as variáveis estão configuradas no Railway"""
        try:
            result = subprocess.run(['railway', 'variables'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                self.log_error(f"Falha ao verificar variáveis Railway: {result.stderr}")
                return False, []
            
            output = result.stdout
            missing_vars = []
            
            # Verificar variáveis críticas
            critical_vars = [
                'OPENAI_API_KEY',
                'RAPIDAPI_KEY', 
                'INSTAGRAM_ACCESS_TOKEN',
                'INSTAGRAM_BUSINESS_ACCOUNT_ID'
            ]
            
            for var in critical_vars:
                if var not in output:
                    missing_vars.append(var)
            
            return len(missing_vars) == 0, missing_vars
            
        except subprocess.TimeoutExpired:
            self.log_error("Timeout ao verificar variáveis Railway")
            return False, []
        except Exception as e:
            self.log_error(f"Erro ao verificar variáveis Railway: {e}")
            return False, []
    
    def restore_railway_variables(self):
        """Restaura todas as variáveis no Railway"""
        if not self.credentials:
            self.log_error("Não é possível restaurar - credenciais não carregadas")
            return False
        
        try:
            commands = self.credentials['railway_commands']
            failed_commands = []
            
            for cmd in commands:
                self.log_message(f"Executando: {cmd[:50]}...")
                
                result = subprocess.run(cmd, shell=True, capture_output=True, 
                                      text=True, timeout=30)
                
                if result.returncode != 0:
                    failed_commands.append(cmd)
                    self.log_error(f"Falha no comando: {result.stderr}")
                else:
                    self.log_message("✅ Comando executado com sucesso")
            
            if failed_commands:
                self.log_error(f"Falharam {len(failed_commands)} comandos")
                return False
            
            # Redeploy do serviço
            self.log_message("Fazendo redeploy do serviço...")
            result = subprocess.run(['railway', 'up', '--detach'], 
                                  capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                self.log_error(f"Falha no redeploy: {result.stderr}")
                return False
            
            self.log_message("✅ Redeploy concluído com sucesso")
            return True
            
        except Exception as e:
            self.log_error(f"Erro ao restaurar variáveis: {e}")
            return False
    
    def run_recovery_check(self):
        """Executa verificação e recuperação completa"""
        self.log_message("🔍 Iniciando verificação de credenciais...")
        
        # Verificar se credenciais estão OK
        variables_ok, missing_vars = self.check_railway_variables()
        
        if variables_ok:
            self.log_message("✅ Todas as credenciais estão configuradas corretamente!")
            self.send_telegram_notification(
                "✅ <b>CREDENCIAIS OK</b>\n"
                "Todas as variáveis estão configuradas no Railway.\n"
                "Sistema funcionando normalmente."
            )
            return True
        
        # Credenciais faltando - iniciar recuperação
        self.log_message(f"❌ Credenciais faltando: {missing_vars}")
        self.send_telegram_notification(
            f"🚨 <b>CREDENCIAIS PERDIDAS DETECTADAS!</b>\n"
            f"Variáveis faltando: {', '.join(missing_vars)}\n"
            f"Iniciando auto-recuperação..."
        )
        
        # Restaurar credenciais
        if self.restore_railway_variables():
            self.log_message("✅ Auto-recuperação concluída com sucesso!")
            self.send_telegram_notification(
                "✅ <b>AUTO-RECUPERAÇÃO CONCLUÍDA!</b>\n"
                "Todas as credenciais foram restauradas.\n"
                "Sistema voltou ao funcionamento normal.\n"
                "Cron jobs devem funcionar agora."
            )
            return True
        else:
            self.log_error("❌ Falha na auto-recuperação!")
            self.send_telegram_notification(
                "🚨 <b>FALHA NA AUTO-RECUPERAÇÃO!</b>\n"
                "Não foi possível restaurar as credenciais automaticamente.\n"
                "INTERVENÇÃO MANUAL NECESSÁRIA!\n"
                "Verificar logs para detalhes."
            )
            return False

def main():
    """Função principal"""
    recovery = CredentialsAutoRecovery()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--force-restore':
        # Forçar restauração
        recovery.log_message("🔧 Modo FORCE RESTORE ativado")
        success = recovery.restore_railway_variables()
        if success:
            recovery.log_message("✅ Restauração forçada concluída!")
        else:
            recovery.log_error("❌ Falha na restauração forçada!")
        return success
    
    # Verificação normal
    return recovery.run_recovery_check()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)