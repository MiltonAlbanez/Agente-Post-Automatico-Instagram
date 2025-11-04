#!/usr/bin/env python3
"""
Deploy do Agente Post 15h Auto Insta 01 com rollback automático

Fluxo:
- Backup dos bancos LTM
- Registro/validação dos LTMs no índice
- Verificação de conectividade ao Postgres (DSN endurecido)
- Pré‑validações de ambiente
- Notificação de sucesso/fracasso
- Rollback automático em caso de falha
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime

from notification_system import notification_system
from ltm_update_manager import LTMUpdateManager
from src.config import load_config, perform_preflight_checks
from src.services.db import Database


def restore_backups(backup_paths: dict, data_path: Path):
    """Restaura backups criados no início do processo."""
    for db_name, bpath in backup_paths.items():
        try:
            src = Path(bpath)
            dst = data_path / f"{db_name}.db"
            if src.exists():
                shutil.copy2(src, dst)
        except Exception:
            # Falha de restauração não impede outras
            pass


def main():
    mgr = LTMUpdateManager()
    print("🚀 Iniciando deploy do Agente Post 15h...")

    # 1) Backup
    backups = mgr.backup_current_ltm()

    try:
        # 2) Registro/validação LTM
        result = mgr.register_ltm_docs()
        status = result.get('status')
        if status == 'FAILED':
            raise RuntimeError("Registro LTM falhou completamente")

        # 3) Pré‑validações de ambiente
        cfg = load_config()
        pre_ok = perform_preflight_checks(cfg)
        if not pre_ok:
            raise RuntimeError("Pré‑validações do ambiente falharam")

        # 4) Verificar conectividade DB
        dsn = cfg.get("POSTGRES_DSN")
        if not dsn:
            raise RuntimeError("POSTGRES_DSN ausente nas variáveis de ambiente")
        db = Database(dsn)
        if not db.check_connectivity():
            raise RuntimeError("Conectividade ao Postgres falhou (SELECT 1)")

        # 5) Sucesso: notificar
        notification_system.send_system_alert(
            "deploy_post_15h_success",
            "Deploy do Agente Post 15h concluído com sucesso",
            {"ltm_status": status, "timestamp": datetime.now().isoformat()}
        )
        print("✅ Deploy concluído com sucesso")

        # Sugestão de mensagem de commit para versionamento
        print("\nMensagem de commit sugerida:")
        print("""
feat(post-15h): validações LTM + endurecimento DSN + deploy c/ rollback

- Integra validações de tipos, regras de negócio e integridade nos LTMs
- Adiciona notificações de falhas via Telegram
- Endurece conexão Postgres (sslmode=require, connect_timeout)
- Script de deploy com backup e rollback automático

Impactos esperados:
- Redução de erros de conexão (startup packet)
- Maior confiabilidade no registro e execução do Agente 15h
""")

    except Exception as e:
        # Rollback
        restore_backups(backups, mgr.data_path)
        msg = f"Falha no deploy do Agente Post 15h: {e}"
        notification_system.send_system_alert(
            "deploy_post_15h_failure",
            msg,
            {"timestamp": datetime.now().isoformat()}
        )
        print(f"❌ {msg}")
        sys.exit(1)


if __name__ == "__main__":
    main()