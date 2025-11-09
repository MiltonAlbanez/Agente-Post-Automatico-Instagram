import sys
import os
from pathlib import Path

# Garantir que 'src' está no PYTHONPATH
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from main import main as src_main  # src/main.py: def main()

try:
    from cron_lock_system import CronLock
except Exception:
    CronLock = None


def main():
    if CronLock is None:
        # Fallback: executar sem lock
        src_main()
        return
    # Nome padrão de lock para serviços agendados
    lock_name = os.environ.get("CRON_NAME", "default_cron")
    timeout = int(os.environ.get("CRON_LOCK_TIMEOUT_MIN", "30"))
    with CronLock(lock_name, timeout_minutes=timeout):
        src_main()


if __name__ == "__main__":
    main()