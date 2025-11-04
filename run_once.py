#!/usr/bin/env python3
"""
Execução única da pipeline de publicação.
Uso típico: apontar o Cron Start Command para este script para evitar loops 24/7.

Exemplos:
  python run_once.py --stories         # publica Stories (fallback standalone se DB vazio)
  python run_once.py                   # publica Feed
  python run_once.py --account "Albanez Assistência Técnica"  # força conta específica via env

Observação: este script delega para o CLI de src/main.py (subcomando autopost)
para reaproveitar toda a lógica de fallback, Supabase e filtros por tags.
"""

import argparse
import os
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description="Executar uma publicação única (Feed/Stories)")
    parser.add_argument("--stories", action="store_true", help="Publicar como Stories em vez de Feed")
    parser.add_argument("--account", required=False, help="Nome exato da conta em accounts.json (define env ACCOUNT_NAME)")
    parser.add_argument("--style", required=False, help="Estilo opcional da legenda")
    parser.add_argument("--tags", required=False, help="Lista de tags/usernames separadas por vírgula para filtrar o banco")
    parser.add_argument("--replicate_prompt", required=False, help="Override do prompt de geração de imagem (Replicate)")
    parser.add_argument("--disable_replicate", action="store_true", help="Usar imagem original (sem Replicate)")
    args = parser.parse_args()

    # Propagar ACCOUNT_NAME para o autopost se informado
    if args.account:
        os.environ["ACCOUNT_NAME"] = args.account

    # Montar comando para o subcomando autopost do src/main.py
    cmd_parts = [sys.executable, "src/main.py", "autopost"]
    if args.stories:
        cmd_parts.append("--stories")
    if args.style:
        cmd_parts.extend(["--style", args.style])
    if args.tags:
        cmd_parts.extend(["--tags", args.tags])
    if args.replicate_prompt:
        cmd_parts.extend(["--replicate_prompt", args.replicate_prompt])
    if args.disable_replicate:
        cmd_parts.append("--disable_replicate")

    print("🚀 Executando publicação única:", " ".join(cmd_parts))
    try:
        result = subprocess.run(cmd_parts, check=False)
        exit_code = result.returncode
        if exit_code == 0:
            print("✅ Execução concluída com sucesso")
        else:
            print(f"⚠️ Execução concluída com código {exit_code}")
        return exit_code
    except Exception as e:
        print(f"❌ Erro ao executar publicação única: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())