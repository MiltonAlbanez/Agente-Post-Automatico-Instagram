#!/usr/bin/env python3
"""
Inicializa o agendador de backups automáticos diariamente usando BackupManager.
Use este comando como serviço ou cron no Railway.
"""

from src.services.backup_manager import BackupManager
from time import sleep

def main():
    bm = BackupManager()
    bm.start_scheduler()
    print("⏰ Backup scheduler ativo. Mantendo processo em execução...")
    # Manter processo vivo
    while True:
        sleep(300)

if __name__ == "__main__":
    main()