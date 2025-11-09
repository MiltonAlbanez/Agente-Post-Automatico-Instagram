import sqlite3
import os
from datetime import datetime, timedelta

def check_performance_databases():
    """Verificar bancos de dados de performance e engagement"""
    
    databases = [
        'data/performance.db',
        'data/engagement_monitor.db',
        'data/performance_optimizer.db',
        'data/ab_testing.db'
    ]
    
    for db_path in databases:
        print(f"\n🔍 Verificando: {db_path}")
        
        if not os.path.exists(db_path):
            print(f"❌ Banco de dados não encontrado: {db_path}")
            continue
            
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Verificar tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"📊 Tabelas: {[t[0] for t in tables]}")
            
            # Para cada tabela, verificar registros recentes
            for table in tables:
                table_name = table[0]
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    print(f"  - {table_name}: {count} registros")
                    
                    # Tentar buscar registros recentes (últimas 24 horas)
                    try:
                        # Tentar diferentes formatos de timestamp
                        timestamp_columns = ['timestamp', 'created_at', 'date', 'time']
                        
                        for ts_col in timestamp_columns:
                            try:
                                yesterday = datetime.now() - timedelta(days=1)
                                yesterday_str = yesterday.strftime('%Y-%m-%d %H:%M:%S')
                                
                                cursor.execute(f"SELECT * FROM {table_name} WHERE {ts_col} > ? ORDER BY {ts_col} DESC LIMIT 5", (yesterday_str,))
                                recent_records = cursor.fetchall()
                                
                                if recent_records:
                                    print(f"    📅 Registros recentes (últimas 24h) via {ts_col}:")
                                    for record in recent_records:
                                        print(f"      - {record}")
                                    break
                                    
                            except sqlite3.OperationalError:
                                continue
                                
                    except Exception as e:
                        print(f"    ⚠️ Erro ao buscar registros recentes: {e}")
                        
                except sqlite3.OperationalError as e:
                    print(f"  ❌ Erro ao acessar tabela {table_name}: {e}")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Erro ao verificar {db_path}: {e}")

def check_today_posts():
    """Verificar posts de hoje especificamente"""
    print(f"\n🎯 Verificando posts de hoje ({datetime.now().strftime('%Y-%m-%d')})...")
    
    # Verificar no banco de engagement
    db_path = 'data/engagement_monitor.db'
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Buscar posts de hoje
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                try:
                    cursor.execute(f"SELECT * FROM {table_name} WHERE timestamp LIKE ? OR created_at LIKE ?", (f'{today}%', f'{today}%'))
                    today_posts = cursor.fetchall()
                    
                    if today_posts:
                        print(f"📱 Posts de hoje em {table_name}:")
                        for post in today_posts:
                            print(f"  - {post}")
                            
                except sqlite3.OperationalError:
                    continue
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Erro ao verificar posts de hoje: {e}")

if __name__ == "__main__":
    print("🔍 DIAGNÓSTICO DOS BANCOS DE DADOS")
    print("=" * 50)
    
    check_performance_databases()
    check_today_posts()
    
    print("\n✅ Diagnóstico concluído!")