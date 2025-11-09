import os
import sys
import json
from pathlib import Path


BASE = Path(__file__).resolve().parent


REQUIRED_FILES = {
    "Procfile": "Define processo web/worker (Railway)",
    "railway.json": "Configuração de deploy do Railway",
    "accounts.json": "Configurações de contas e prompts",
    "src/main.py": "Entry point principal da aplicação",
}

REQUIRED_PACKAGES = {
    "requests": "2.31.0",
    "python-dotenv": ">=1.0.0",
    "psycopg[binary]": "==3.2.3",
    "flask": "==2.3.3",
    "Werkzeug": "==2.3.7",
    "psutil": "==5.9.6",
}


CRON_SERVICES = [
    {
        "name": "Agente Post 06h Auto Insta 01",
        "schedule": "0 9 * * *",  # 06h BRT => 09h UTC
        "description": "Post automático 06h BRT (Feed)",
        "env": {"ACCOUNT_NAME": "Milton_Albanez", "TZ": "America/Sao_Paulo"},
        "command": "python main.py autopost",
        "lock": {"CRON_LOCK_NAME": "cron_autopost_06h", "CRON_LOCK_TIMEOUT_MIN": "60"},
    },
    {
        "name": "Agente Post 09h Auto Insta 01",
        "schedule": "0 12 * * *",  # 09h BRT => 12h UTC
        "description": "Post automático 09h BRT (Feed)",
        "env": {"ACCOUNT_NAME": "Milton_Albanez", "TZ": "America/Sao_Paulo"},
        "command": "python main.py autopost",
        "lock": {"CRON_LOCK_NAME": "cron_autopost_09h", "CRON_LOCK_TIMEOUT_MIN": "60"},
    },
    {
        "name": "Agente Post 12h Auto Insta 02",
        "schedule": "0 15 * * *",  # 12h BRT => 15h UTC
        "description": "Post automático 12h BRT (Feed)",
        "env": {"ACCOUNT_NAME": "Milton_Albanez", "TZ": "America/Sao_Paulo"},
        "command": "python main.py autopost",
        "lock": {"CRON_LOCK_NAME": "cron_autopost_12h", "CRON_LOCK_TIMEOUT_MIN": "60"},
    },
    {
        "name": "Agente Post 15h Auto Insta 02",
        "schedule": "0 18 * * *",  # 15h BRT => 18h UTC
        "description": "Post automático 15h BRT (Feed)",
        "env": {"ACCOUNT_NAME": "Milton_Albanez", "TZ": "America/Sao_Paulo"},
        "command": "python main.py autopost",
        "lock": {"CRON_LOCK_NAME": "cron_autopost_15h", "CRON_LOCK_TIMEOUT_MIN": "60"},
    },
    {
        "name": "Agente Post 19h Auto Insta 02",
        "schedule": "0 22 * * *",  # 19h BRT => 22h UTC (corrigido)
        "description": "Post automático 19h BRT (Feed)",
        "env": {"ACCOUNT_NAME": "Milton_Albanez", "TZ": "America/Sao_Paulo"},
        "command": "python main.py autopost",
        "lock": {"CRON_LOCK_NAME": "cron_autopost_19h", "CRON_LOCK_TIMEOUT_MIN": "60"},
    },
]


def check_required_files():
    status = {}
    issues = []
    for fname, desc in REQUIRED_FILES.items():
        exists = (BASE / fname).exists()
        status[fname] = {"exists": exists, "description": desc}
        if not exists:
            issues.append(f"Arquivo ausente: {fname} ({desc})")
    return status, issues


def read_requirements():
    req_path = BASE / "requirements.txt"
    if not req_path.exists():
        return []
    with open(req_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def write_requirements(lines):
    req_path = BASE / "requirements.txt"
    with open(req_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def ensure_packages():
    lines = read_requirements()
    changed = False
    def has_pkg(name):
        return any(l.startswith(name) for l in lines)
    for name, version_spec in REQUIRED_PACKAGES.items():
        if not has_pkg(name):
            lines.append(f"{name}{version_spec}")
            changed = True
    if changed:
        write_requirements(lines)
    return changed


def generate_cron_config():
    cfg = {
        "services": []
    }
    for svc in CRON_SERVICES:
        env = {}
        env.update(svc.get("env", {}))
        env.update(svc.get("lock", {}))
        cfg["services"].append({
            "name": svc["name"],
            "schedule": svc["schedule"],
            "description": svc["description"],
            "env": env,
            "startCommand": svc["command"],
        })
    return cfg


def save_cron_config(cfg, path: Path | None = None):
    path = path or (BASE / "railway_cron_config.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    return path


def print_manual_instructions(cfg):
    print("\n=== INSTRUÇÕES MANUAIS (Railway Dashboard) ===")
    print("Crie 5 serviços (cron/worker) com as seguintes configurações:")
    for svc in cfg["services"]:
        print(f"\n• Nome: {svc['name']}")
        print(f"  - Agendamento (cron UTC): {svc['schedule']}")
        print(f"  - Descrição: {svc['description']}")
        print(f"  - Comando: {svc['startCommand']}")
        print("  - Variáveis de ambiente:")
        for k, v in svc["env"].items():
            print(f"    • {k}={v}")
    print("\nNotas:")
    print("- As expressões de cron estão em UTC. Ajustadas para BRT (UTC-3).")
    print("- CRON_LOCK_NAME evita execuções concorrentes entre serviços do mesmo horário.")
    print("- CRON_LOCK_TIMEOUT_MIN define o prazo para considerar o lock como válido (minutos).")


def main():
    files_status, issues = check_required_files()
    print("=== Verificação de arquivos ===")
    for fname, info in files_status.items():
        print(f"- {fname}: {'OK' if info['exists'] else 'AUSENTE'} ({info['description']})")
    if issues:
        print("\n⚠️  Issues:")
        for i in issues:
            print("-", i)

    print("\n=== Verificação/Atualização de requirements.txt ===")
    changed = ensure_packages()
    print("- requirements.txt: ", "atualizado" if changed else "ok")

    print("\n=== Geração de configuração de cron (Railway) ===")
    cfg = generate_cron_config()
    out_path = save_cron_config(cfg)
    print(f"- Arquivo gerado: {out_path}")
    print_manual_instructions(cfg)


if __name__ == "__main__":
    main()