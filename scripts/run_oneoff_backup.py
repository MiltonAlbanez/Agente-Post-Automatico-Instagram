#!/usr/bin/env python3
"""
Executa um backup pontual (daily ou full) e termina.
Ideal para uso em Cron do Railway (execução one-off).
"""

import argparse
from src.services.backup_manager import BackupManager

def main():
    parser = argparse.ArgumentParser(description="Backup pontual para cron")
    parser.add_argument("--type", choices=["daily", "full"], default="daily", help="Tipo de backup")
    args = parser.parse_args()

    bm = BackupManager()
    if args.type == "full":
        path = bm.create_full_backup()
    else:
        path = bm.create_daily_backup()
    print(f"Backup concluído: {path}")

if __name__ == "__main__":
    main()