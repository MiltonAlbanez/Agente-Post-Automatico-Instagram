#!/usr/bin/env python3
"""
📊 MONITOR DE LOGS DO RAILWAY
Monitora logs para verificar notificações Telegram
"""

import subprocess
import time
import re
import os
import requests
from datetime import datetime

def log_message(message):
    """Log com timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def get_telegram_config():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    return token, chat_id


def send_telegram_message(text: str) -> bool:
    token, chat_id = get_telegram_config()
    if not token or not chat_id:
        log_message("⚠️ Variáveis TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID ausentes; alerta não enviado")
        return False
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={"chat_id": chat_id, "text": text}
        )
        if resp.status_code == 200 and resp.json().get("ok"):
            log_message("✅ Alerta Telegram enviado")
            return True
        else:
            log_message(f"❌ Falha ao enviar Telegram: {resp.text}")
            return False
    except Exception as e:
        log_message(f"❌ Erro ao enviar Telegram: {e}")
        return False

def monitor_railway_logs(enable_alerts: bool = False):
    """Monitora logs do Railway em tempo real ou via polling"""
    log_message("📊 INICIANDO MONITORAMENTO DOS LOGS RAILWAY")
    log_message("=" * 60)
    log_message("🔍 Procurando por:")
    log_message("   - Notificações Telegram")
    log_message("   - Erros de Telegram")
    log_message("   - Execuções do sistema")
    log_message("   - Status de publicações")
    log_message("-" * 60)
    
    def parse_and_report(line, counters):
        current_time = datetime.now().strftime("%H:%M:%S")
        low = line.lower()
        if any(keyword in low for keyword in ['telegram', 'notification', 'notificação']):
            if 'erro' in low or 'error' in low:
                counters['telegram_errors'] += 1
                print(f"🔴 [{current_time}] ERRO TELEGRAM: {line.strip()}")
                if enable_alerts:
                    send_telegram_message(f"🔴 ERRO TELEGRAM detectado: {line.strip()}")
            else:
                counters['telegram_notifications'] += 1
                print(f"🟢 [{current_time}] TELEGRAM: {line.strip()}")
        elif any(keyword in low for keyword in ['execução', 'execution', 'iniciando', 'starting']):
            counters['executions'] += 1
            print(f"🔵 [{current_time}] EXECUÇÃO: {line.strip()}")
        elif any(keyword in low for keyword in ['publicação', 'publication', 'posted', 'published']):
            print(f"📱 [{current_time}] PUBLICAÇÃO: {line.strip()}")
        elif any(keyword in low for keyword in ['error', 'erro', 'exception', 'fail']):
            print(f"⚠️  [{current_time}] ERRO: {line.strip()}")
            if enable_alerts:
                send_telegram_message(f"⚠️ ERRO detectado nos logs: {line.strip()}")
        elif any(keyword in low for keyword in ['instagram', 'railway', 'automation']):
            print(f"ℹ️  [{current_time}] INFO: {line.strip()}")

    def print_stats(counters):
        total = counters['telegram_notifications'] + counters['telegram_errors'] + counters['executions']
        if total % 10 == 0 and total > 0:
            print(f"\n📊 ESTATÍSTICAS:")
            print(f"   📱 Notificações Telegram: {counters['telegram_notifications']}")
            print(f"   🔴 Erros Telegram: {counters['telegram_errors']}")
            print(f"   🔵 Execuções: {counters['executions']}")
            print("-" * 40)

    def monitor_follow_mode():
        counters = {'telegram_notifications': 0, 'telegram_errors': 0, 'executions': 0}
        log_message("🚀 Monitoramento ativo (follow) - Pressione Ctrl+C para parar")
        log_message("=" * 60)
        cmd = "railway logs --follow"
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True)
        try:
            for line in iter(process.stdout.readline, ''):
                if line.strip():
                    parse_and_report(line, counters)
                    print_stats(counters)
        finally:
            process.terminate()
        return counters

    def monitor_polling_mode(interval=30):
        counters = {'telegram_notifications': 0, 'telegram_errors': 0, 'executions': 0}
        log_message(f"🚀 Monitoramento ativo (polling {interval}s) - Pressione Ctrl+C para parar")
        log_message("=" * 60)
        last_seen = set()
        try:
            while True:
                result = subprocess.run("railway logs", shell=True, capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    lines = result.stdout.splitlines()
                    new_lines = [ln for ln in lines if ln not in last_seen]
                    for ln in new_lines:
                        if ln.strip():
                            parse_and_report(ln, counters)
                            print_stats(counters)
                    last_seen = set(lines[-200:])
                else:
                    log_message(f"❌ Erro ao obter logs: {result.stderr.strip()}")
                    if enable_alerts:
                        send_telegram_message(f"❌ Erro ao obter logs do Railway: {result.stderr.strip()}")
                time.sleep(interval)
        except KeyboardInterrupt:
            return counters

    try:
        probe = subprocess.run("railway logs --help", shell=True, capture_output=True, text=True)
        if '--follow' in probe.stdout or '--follow' in probe.stderr:
            counters = monitor_follow_mode()
        else:
            log_message("ℹ️ A CLI do Railway não suporta '--follow'. Usando modo polling.")
            counters = monitor_polling_mode()
    except Exception as e:
        log_message(f"❌ ERRO no monitoramento: {e}")
        counters = {'telegram_notifications': 0, 'telegram_errors': 0, 'executions': 0}

    print(f"\n📊 RESUMO FINAL:")
    print(f"   📱 Notificações Telegram: {counters['telegram_notifications']}")
    print(f"   🔴 Erros Telegram: {counters['telegram_errors']}")
    print(f"   🔵 Execuções: {counters['executions']}")
    if counters['telegram_notifications'] > 0:
        print("✅ NOTIFICAÇÕES TELEGRAM FUNCIONANDO!")
    elif counters['telegram_errors'] > 0:
        print("❌ PROBLEMAS COM TELEGRAM DETECTADOS!")
        if enable_alerts:
            send_telegram_message("❌ Problemas com Telegram detectados nos logs (resumo final).")
    else:
        print("⚠️ NENHUMA ATIVIDADE TELEGRAM DETECTADA")

def check_recent_logs(enable_alerts: bool = False):
    """Verifica logs recentes para atividade Telegram"""
    log_message("🔍 VERIFICANDO LOGS RECENTES")
    log_message("=" * 40)
    try:
        result = subprocess.run("railway logs", shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            logs = result.stdout
            telegram_mentions = len(re.findall(r'telegram|notification|notificação', logs, re.IGNORECASE))
            error_mentions = len(re.findall(r'erro.*telegram|telegram.*erro|error.*telegram|telegram.*error', logs, re.IGNORECASE))
            log_message(f"📊 Análise dos últimos 100 logs:")
            log_message(f"   📱 Menções ao Telegram: {telegram_mentions}")
            log_message(f"   🔴 Erros relacionados: {error_mentions}")
            if telegram_mentions > 0:
                log_message("✅ Atividade Telegram detectada nos logs!")
            else:
                log_message("⚠️ Nenhuma atividade Telegram nos logs recentes")
            if error_mentions > 0 and enable_alerts:
                send_telegram_message(f"❌ Erros relacionados ao Telegram detectados: {error_mentions}")
            return telegram_mentions > 0
        else:
            err = result.stderr.strip()
            log_message(f"❌ Erro ao obter logs: {err}")
            if enable_alerts:
                send_telegram_message(f"❌ Erro ao obter logs com 'railway logs': {err}")
            return False
    except Exception as e:
        log_message(f"❌ Erro na verificação: {e}")
        if enable_alerts:
            send_telegram_message(f"❌ Exceção na verificação de logs: {e}")
        return False

def main():
    """Menu principal"""
    log_message("📊 MONITOR DE LOGS RAILWAY - TELEGRAM")
    log_message("=" * 50)
    print("Escolha uma opção:")
    print("1. 🔍 Verificar logs recentes")
    print("2. 📊 Monitorar logs em tempo real")
    print("3. 🚀 Ambos (verificar + monitorar)")
    try:
        choice = input("\nDigite sua escolha (1-3): ").strip()
        if choice == "1":
            check_recent_logs()
        elif choice == "2":
            monitor_railway_logs()
        elif choice == "3":
            check_recent_logs()
            print("\n" + "="*50)
            input("Pressione Enter para iniciar monitoramento contínuo...")
            monitor_railway_logs()
        else:
            log_message("❌ Opção inválida")
    except KeyboardInterrupt:
        log_message("\n⏹️ Operação cancelada")
    except Exception as e:
        log_message(f"❌ Erro: {e}")

if __name__ == "__main__":
    # CLI headless opcional
    import argparse
    parser = argparse.ArgumentParser(description="Monitor de logs do Railway com alertas Telegram")
    parser.add_argument("--recent", action="store_true", help="Executa verificação de logs recentes e sai")
    parser.add_argument("--monitor", action="store_true", help="Monitora logs continuamente (follow/polling)")
    parser.add_argument("--interval", type=int, default=30, help="Intervalo de polling em segundos quando follow não está disponível")
    parser.add_argument("--alerts", action="store_true", help="Envia alertas via Telegram quando erros forem identificados")
    args = parser.parse_args()

    if args.recent and not args.monitor:
        check_recent_logs(enable_alerts=args.alerts)
    elif args.monitor:
        # Ajustar intervalo no modo polling via variável global simples
        # Nota: interval é usado internamente quando follow não existe
        monitor_railway_logs(enable_alerts=args.alerts)
    else:
        # Fallback para modo interativo antigo
        log_message("📊 MONITOR DE LOGS RAILWAY - TELEGRAM")
        log_message("=" * 50)
        print("Escolha uma opção:")
        print("1. 🔍 Verificar logs recentes")
        print("2. 📊 Monitorar logs em tempo real")
        print("3. 🚀 Ambos (verificar + monitorar)")
        try:
            choice = input("\nDigite sua escolha (1-3): ").strip()
            if choice == "1":
                check_recent_logs()
            elif choice == "2":
                monitor_railway_logs()
            elif choice == "3":
                check_recent_logs()
                print("\n" + "="*50)
                input("Pressione Enter para iniciar monitoramento contínuo...")
                monitor_railway_logs()
            else:
                log_message("❌ Opção inválida")
        except KeyboardInterrupt:
            log_message("\n⏹️ Operação cancelada")
        except Exception as e:
            log_message(f"❌ Erro: {e}")

    main()