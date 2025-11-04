#!/usr/bin/env python3
"""
Script para verificar a estrutura das tabelas nos bancos de dados existentes
"""

import sqlite3
import os
from pathlib import Path

def check_database_schema(db_path):
    """Verifica a estrutura das tabelas em um banco de dados"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Listar todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"\n=== {os.path.basename(db_path)} ===")
        print(f"Tabelas encontradas: {tables}")
        
        # Verificar estrutura da tabela ltm_docs_index se existir
        if 'ltm_docs_index' in tables:
            cursor.execute("PRAGMA table_info(ltm_docs_index)")
            columns = cursor.fetchall()
            print("\nEstrutura da tabela ltm_docs_index:")
            for col in columns:
                print(f"  {col[1]} ({col[2]}) - {col}")
        else:
            print("Tabela ltm_docs_index não encontrada")
            
        conn.close()
        
    except Exception as e:
        print(f"Erro ao verificar {db_path}: {e}")

def main():
    data_dir = Path("data")
    if not data_dir.exists():
        print("Diretório 'data' não encontrado")
        return
    
    # Verificar todos os arquivos .db
    db_files = list(data_dir.glob("*.db"))
    
    if not db_files:
        print("Nenhum arquivo .db encontrado no diretório data")
        return
    
    print(f"Verificando {len(db_files)} bancos de dados...")
    
    for db_file in db_files:
        check_database_schema(db_file)

if __name__ == "__main__":
    main()