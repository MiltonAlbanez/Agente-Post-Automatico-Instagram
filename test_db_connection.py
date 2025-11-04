#!/usr/bin/env python3
"""
Teste simples para verificar a conexão com o PostgreSQL no Railway
"""

import os
import psycopg
from urllib.parse import urlparse

def test_database_connection():
    """Testa a conexão com o banco PostgreSQL"""
    try:
        # Obter DATABASE_URL do ambiente (tenta primeiro a interna, depois a pública)
        database_url = os.getenv('DATABASE_URL')
        
        if not database_url:
            # Se não encontrar DATABASE_URL, tenta usar a pública para teste local
            database_url = "postgresql://postgres:MkwPGYlDGFIUkMDzULxhhbOftVTdVLhd@centerbeam.proxy.rlwy.net:42100/railway"
            print("🔄 Usando DATABASE_PUBLIC_URL para teste local")
        
        if not database_url:
            print("❌ DATABASE_URL não encontrada nas variáveis de ambiente")
            return False
            
        print(f"🔍 DATABASE_URL encontrada: {database_url[:50]}...")
        
        # Parse da URL
        parsed = urlparse(database_url)
        
        # Conectar ao banco
        print("🔄 Tentando conectar ao PostgreSQL...")
        conn = psycopg.connect(
            host=parsed.hostname,
            port=parsed.port,
            dbname=parsed.path[1:],  # Remove o '/' inicial
            user=parsed.username,
            password=parsed.password
        )
        
        # Testar uma query simples
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print(f"✅ Conexão bem-sucedida!")
        print(f"📊 Versão do PostgreSQL: {version[0]}")
        
        # Testar criação de tabela simples
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_connection (
                id SERIAL PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message TEXT
            );
        """)
        
        # Inserir um registro de teste
        cursor.execute("""
            INSERT INTO test_connection (message) 
            VALUES ('Teste de conexão Railway PostgreSQL');
        """)
        
        # Verificar se foi inserido
        cursor.execute("SELECT COUNT(*) FROM test_connection;")
        count = cursor.fetchone()[0]
        
        print(f"📝 Registros na tabela de teste: {count}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("🎉 Teste de conexão PostgreSQL concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando teste de conexão PostgreSQL Railway...")
    success = test_database_connection()
    
    if success:
        print("\n✅ RESULTADO: PostgreSQL configurado corretamente!")
    else:
        print("\n❌ RESULTADO: Problemas na configuração do PostgreSQL")