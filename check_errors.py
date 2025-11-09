import sqlite3
import os
from datetime import datetime, timedelta

def check_error_database():
    db_path = 'data/error_reflection.db'
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados de reflexão de erros não encontrado!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"📊 Tabelas encontradas: {[t[0] for t in tables]}")
        
        # Verificar últimos erros
        cursor.execute("SELECT * FROM error_attempts ORDER BY timestamp DESC LIMIT 10")
        recent_errors = cursor.fetchall()
        
        print("\n🔍 Últimos 10 erros registrados:")
        for error in recent_errors:
            print(f"  - {error}")
        
        # Verificar erros das últimas 24 horas
        yesterday = datetime.now() - timedelta(days=1)
        yesterday_str = yesterday.strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute("SELECT * FROM error_attempts WHERE timestamp > ? ORDER BY timestamp DESC", (yesterday_str,))
        recent_24h = cursor.fetchall()
        
        print(f"\n⏰ Erros nas últimas 24 horas: {len(recent_24h)}")
        for error in recent_24h:
            print(f"  - {error}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco de dados: {e}")

if __name__ == "__main__":
    check_error_database()