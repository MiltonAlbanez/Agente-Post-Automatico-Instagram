#!/usr/bin/env python3
"""
Procedimento de rollback e recuperação:
- Reverte para backup anterior (mais recente ou específico)
- Recupera arquivos apagados restaurando o conteúdo do backup
- Gera relatório de operações
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional

from src.services.backup_manager import BackupManager

def find_latest_backup_dir(base: Path) -> Optional[Path]:
    if not base.exists():
        return None
    candidates = sorted([p for p in base.iterdir() if p.is_dir()], reverse=True)
    return candidates[0] if candidates else None

def rollback(target_backup: Optional[str] = None) -> dict:
    bm = BackupManager()
    base_dir = Path(bm.config.get("backup_base_dir", "backups"))
    base_dir.mkdir(exist_ok=True)

    if target_backup:
        backup_dir = Path(target_backup)
    else:
        backup_dir = find_latest_backup_dir(base_dir)

    if not backup_dir or not backup_dir.exists():
        raise FileNotFoundError("Nenhum backup válido encontrado para rollback.")

    result = bm.restore_backup(str(backup_dir))
    return {"backup_dir": str(backup_dir), "result": result}

def main():
    import argparse
    ap = argparse.ArgumentParser(description="Procedimento de rollback e recuperação")
    ap.add_argument("--backup", help="Caminho do backup específico (opcional)")
    args = ap.parse_args()

    report = rollback(args.backup)
    out = Path("backups") / f"rollback_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"↩️ Rollback concluído a partir de: {report['backup_dir']}")
    print(f"📋 Relatório salvo em: {out}")

if __name__ == "__main__":
    main()