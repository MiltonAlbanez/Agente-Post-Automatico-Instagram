#!/usr/bin/env python3
"""
Script de migração para executar dentro do Railway
Migra dados da tabela top_trends do Supabase para o Postgres Railway
"""

import os
import sys
from pathlib import Path

# Adicionar src ao path
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
sys.path.append(str(SRC))

def main():
    print("🚀 Iniciando migração de dados...")
    
    # Verificar variáveis de ambiente
    supabase_dsn = os.getenv("SUPABASE_DB_URL")
    dest_dsn = os.getenv("DATABASE_URL")
    
    if not supabase_dsn:
        print("❌ ERRO: SUPABASE_DB_URL não encontrada")
        return 1
        
    if not dest_dsn:
        print("❌ ERRO: DATABASE_URL não encontrada")
        return 1
    
    print(f"📊 Origem: {supabase_dsn[:50]}...")
    print(f"🎯 Destino: {dest_dsn[:50]}...")
    
    # Importar e executar migração
    try:
        from scripts.migrate_db import migrate_top_trends
        
        print("🔄 Executando migração...")
        migrate_top_trends(
            source_dsn=supabase_dsn,
            dest_dsn=dest_dsn,
            copy_only_unposted=False  # Migrar todos os dados
        )
        
        print("✅ Migração concluída com sucesso!")
        return 0
        
    except Exception as e:
        print(f"❌ ERRO na migração: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())