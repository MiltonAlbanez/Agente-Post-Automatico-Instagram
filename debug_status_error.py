#!/usr/bin/env python3
"""
Script de debug para identificar o erro da coluna 'status'
"""

import sqlite3
import os
from pathlib import Path

def debug_database_tables():
    """Debug das tabelas nos bancos de dados"""
    data_dir = Path("data")
    
    # Verificar todos os bancos
    for db_file in data_dir.glob("*.db"):
        print(f"\n=== Verificando {db_file.name} ===")
        
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Listar tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"Tabelas: {tables}")
            
            # Para cada tabela, verificar se tem coluna 'status'
            for table in tables:
                if table != 'sqlite_sequence':
                    try:
                        cursor.execute(f"PRAGMA table_info({table})")
                        columns = [col[1] for col in cursor.fetchall()]
                        has_status = 'status' in columns
                        print(f"  {table}: colunas={columns}, tem_status={has_status}")
                        
                        # Se não tem status, tentar criar um índice vai dar erro
                        if not has_status:
                            print(f"    ⚠️ Tabela {table} NÃO tem coluna 'status'")
                    except Exception as e:
                        print(f"    ❌ Erro ao verificar {table}: {e}")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Erro ao verificar {db_file}: {e}")

def test_create_index():
    """Testar criação de índice que pode estar causando o erro"""
    print("\n=== Testando criação de índice ===")
    
    # Testar nos bancos existentes
    for db_name in ['engagement_monitor.db', 'performance_optimizer.db']:
        db_path = Path("data") / db_name
        if db_path.exists():
            print(f"\nTestando {db_name}...")
            try:
                conn = sqlite3.connect(db_path)
                
                # Tentar criar o índice que pode estar causando problema
                try:
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_ltm_docs_status ON ltm_docs_index(status, service_hour);")
                    print("  ✅ Índice criado com sucesso")
                except Exception as e:
                    print(f"  ❌ Erro ao criar índice: {e}")
                
                conn.close()
                
            except Exception as e:
                print(f"  ❌ Erro de conexão: {e}")

if __name__ == "__main__":
    debug_database_tables()
    test_create_index()