#!/usr/bin/env python3
"""
⏱️ AGENDADOR DE VERIFICAÇÃO DE LOGS (RAILWAY)
Executa monitoramento de logs recente em intervalo fixo, com alertas Telegram.
"""

import time
import argparse
from datetime import datetime

try:
    import monitor_railway_logs as m
except ImportError:
    raise SystemExit("❌ Não foi possível importar monitor_railway_logs. Verifique o arquivo e o PYTHONPATH.")


def log(message: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {message}")


def run_once(enable_alerts: bool):
    log("🔍 Execução única: check_recent_logs")
    m.check_recent_logs(enable_alerts=enable_alerts)


def main():
    parser = argparse.ArgumentParser(description="Agendador simples para verificar logs do Railway periodicamente")
    parser.add_argument("--interval", type=int, default=10, help="Intervalo entre execuções, em minutos")
    parser.add_argument("--runs", type=int, default=6, help="Número de execuções antes de finalizar (use 0 para infinito)")
    parser.add_argument("--alerts", action="store_true", help="Enviar alertas Telegram quando erros forem detectados")
    args = parser.parse_args()

    log("⏱️ Iniciando agendador de verificação de logs")
    log(f"Intervalo: {args.interval} minutos | Runs: {'∞' if args.runs == 0 else args.runs} | Alerts: {args.alerts}")

    executed = 0
    try:
        while True:
            run_once(enable_alerts=args.alerts)
            executed += 1
            if args.runs != 0 and executed >= args.runs:
                log("✅ Agendador finalizado pelo limite de execuções")
                break
            sleep_seconds = max(1, args.interval * 60)
            log(f"🕒 Aguardando {sleep_seconds} segundos para próxima execução...")
            time.sleep(sleep_seconds)
    except KeyboardInterrupt:
        log("⏹️ Agendador interrompido pelo usuário")


if __name__ == "__main__":
    main()