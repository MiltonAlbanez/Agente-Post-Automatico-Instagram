#!/usr/bin/env python3
"""
Script de Auto-Setup para configurar os 5 serviços no Railway.

Este script:
- Verifica a presença do Railway CLI;
- Vincula e abre o dashboard de cada projeto alvo;
- Exibe instruções claras para ajustar Start Command e Cron na UI;
- Resume validações e próximos passos.

Importante: O ajuste de Start Command e Cron é feito via UI do Railway.
"""

import subprocess
import sys
import shutil
from dataclasses import dataclass


@dataclass
class ProjectInfo:
    name: str
    id: str
    schedule_cron_utc: str


TARGET_PROJECTS = [
    ProjectInfo(
        name="Agente Post 6h Auto Insta 05",
        id="00c6f4f4-1f60-47a4-b1a7-b174c6ea69f9",
        schedule_cron_utc="0 6 * * *",
    ),
    ProjectInfo(
        name="Agente Post 12h Auto Insta 02",
        id="09d5e915-789e-4909-b2ce-42e4a9fa2e68",
        schedule_cron_utc="0 12 * * *",
    ),
    ProjectInfo(
        name="Agente Post 15h Auto Insta 01",
        id="1c0c1cc6-9fce-45a4-aeeb-601e3b9724ad",
        schedule_cron_utc="0 15 * * *",
    ),
    ProjectInfo(
        name="Agente Post 19h Auto Insta 03",
        id="aec15442-aefb-4f32-a020-7ae546dead73",
        schedule_cron_utc="0 19 * * *",
    ),
    ProjectInfo(
        name="Agente Post 21h Auto Insta 04",
        id="959c499a-f5d9-4515-9ff2-0955e75d5665",
        schedule_cron_utc="0 21 * * *",
    ),
]


START_COMMAND = (
    "python railway_cron_diagnostic.py && "
    "python cron_lock_system.py cleanup && "
    "python main.py autopost"
)


def check_cli() -> bool:
    """Verifica se o Railway CLI está instalado e acessível."""
    print("🔎 Verificando Railway CLI...")
    if shutil.which("railway") is None:
        print("❌ Railway CLI não encontrado. Por favor, instale o Railway CLI e faça login: https://railway.app/cli")
        return False
    try:
        subprocess.run(["railway", "--version"], check=True, capture_output=True, text=True)
        print("✅ Railway CLI encontrado.")
        return True
    except Exception as e:
        print(f"❌ Erro ao verificar Railway CLI: {e}")
        return False


def link_project(project: ProjectInfo) -> bool:
    """Vincula o projeto ao ambiente production."""
    print(f"\n🔗 Vinculando projeto: {project.name}")
    try:
        res = subprocess.run(
            ["railway", "link", "--project", project.id, "--environment", "production"],
            check=True,
            capture_output=True,
            text=True,
        )
        print("✅ Link concluído.")
        print(res.stdout.strip())
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Falha ao vincular projeto.")
        print(e.stdout or "")
        print(e.stderr or "")
        return False


def open_project_dashboard(project: ProjectInfo) -> bool:
    """Abre o dashboard do projeto no navegador."""
    print(f"🌐 Abrindo dashboard: {project.name}")
    try:
        res = subprocess.run(["railway", "open"], check=True, capture_output=True, text=True)
        print("✅ Dashboard aberto (verifique o navegador).")
        # Também exibimos a URL se vier no output
        if res.stdout:
            print(res.stdout.strip())
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Falha ao abrir dashboard.")
        print(e.stdout or "")
        print(e.stderr or "")
        return False


def show_setup_instructions(project: ProjectInfo):
    """Exibe instruções para configurar Start Command e Cron via UI do Railway."""
    print("\n🛠️ Instruções de Configuração (UI do Railway)")
    print(f"Projeto: {project.name}")
    print("1) Abra o serviço principal (web) do projeto.")
    print("2) No campo Start Command, insira exatamente:")
    print(f"   {START_COMMAND}")
    print("3) Defina o Cron Schedule (UTC) para:")
    print(f"   {project.schedule_cron_utc}")
    print("4) Confirme que as variáveis de ambiente essenciais estão presentes (PYTHONUNBUFFERED=1, TZ=UTC).")
    print("5) Salve e implante (Deploy) se solicitado.")


def main():
    print("\n🚀 Iniciando Auto-Setup dos serviços Railway...")
    if not check_cli():
        sys.exit(1)

    any_fail = False
    for project in TARGET_PROJECTS:
        print("\n==============================")
        print(f"⚙️ Projeto alvo: {project.name}")
        print("==============================")
        linked = link_project(project)
        if not linked:
            any_fail = True
            continue

        opened = open_project_dashboard(project)
        if not opened:
            any_fail = True

        show_setup_instructions(project)
        input("\n👉 Após ajustar na UI, pressione Enter para continuar para o próximo projeto...")

    print("\n📋 Resumo e próximos passos:")
    print("- Verifique os logs após o próximo disparo do cron.")
    print("- Para testar manualmente em um projeto já vinculado, use:")
    print("  railway run -- python main.py autopost")
    print("- Se ocorrerem erros, verifique variáveis e o Start Command.")

    if any_fail:
        print("\n⚠️ Algumas etapas falharam. Revise as mensagens acima e tente novamente.")
        sys.exit(1)

    print("\n🎉 Auto-Setup concluído! Todos os dashboards foram abertos e instruções exibidas.")
    sys.exit(0)


if __name__ == "__main__":
    main()