import os
import sys
import time
from pathlib import Path


LOCKS_DIR = Path(".locks")
LOCKS_DIR.mkdir(exist_ok=True)


class CronLock:
    def __init__(self, name: str, timeout_minutes: int = 30):
        self.name = name
        self.timeout_seconds = timeout_minutes * 60
        self.lock_path = LOCKS_DIR / f"{self.name}.lock"

    def __enter__(self):
        now = int(time.time())
        if self.lock_path.exists():
            try:
                with open(self.lock_path, "r", encoding="utf-8") as f:
                    ts = int(f.read().strip() or "0")
            except Exception:
                ts = 0
            age = now - ts
            if age < self.timeout_seconds:
                raise RuntimeError(
                    f"Lock ativo para '{self.name}' (idade {age}s < {self.timeout_seconds}s)."
                )
            # Stale lock; remove
            try:
                self.lock_path.unlink()
            except Exception:
                pass

        with open(self.lock_path, "w", encoding="utf-8") as f:
            f.write(str(now))
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            if self.lock_path.exists():
                self.lock_path.unlink()
        except Exception:
            pass


def cleanup(stale_older_minutes: int = 60) -> int:
    """Remove locks mais antigos que o limite."""
    if not LOCKS_DIR.exists():
        return 0
    now = int(time.time())
    threshold = stale_older_minutes * 60
    removed = 0
    for fp in LOCKS_DIR.glob("*.lock"):
        try:
            with open(fp, "r", encoding="utf-8") as f:
                ts = int(f.read().strip() or "0")
        except Exception:
            ts = 0
        age = now - ts
        if age > threshold:
            try:
                fp.unlink()
                removed += 1
            except Exception:
                pass
    print(f"Cleanup: removidos {removed} locks antigos (> {stale_older_minutes} min)")
    return removed


def _print_usage():
    print("Uso:")
    print("  python cron_lock_system.py cleanup [minutos]")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "cleanup":
        minutes = 60
        if len(sys.argv) >= 3:
            try:
                minutes = int(sys.argv[2])
            except Exception:
                pass
        cleanup(minutes)
        sys.exit(0)
    else:
        _print_usage()
        sys.exit(0)