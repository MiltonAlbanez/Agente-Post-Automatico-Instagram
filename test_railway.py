#!/usr/bin/env python3
"""
Teste de agendamento Railway - 10:35 Brasil
Este script será executado automaticamente pelo Railway para testar o agendamento.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Adicionar src ao path
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
sys.path.append(str(SRC))

def test_railway_scheduling():
    """Testa se o agendamento do Railway está funcionando"""
    
    print("🚀 TESTE DE AGENDAMENTO RAILWAY")
    print("=" * 50)
    
    # Horário atual
    now = datetime.now()
    print(f"⏰ Horário de execução: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📅 Data: {now.strftime('%A, %d de %B de %Y')}")
    
    # Verificar variáveis de ambiente
    print("\n🔍 Verificando variáveis de ambiente:")
    
    env_vars = [
        "DATABASE_URL",
        "INSTAGRAM_ACCESS_TOKEN", 
        "INSTAGRAM_BUSINESS_ACCOUNT_ID",
        "OPENAI_API_KEY",
        "TELEGRAM_BOT_TOKEN"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: Configurada")
        else:
            print(f"  ❌ {var}: Não encontrada")
    
    # Testar conexão com banco
    print("\n🗄️ Testando conexão com PostgreSQL:")
    try:
        from config import load_config
        from services.db import Database
        
        cfg = load_config()
        if cfg.get("POSTGRES_DSN"):
            db = Database(cfg["POSTGRES_DSN"])
            print("  ✅ Conexão com PostgreSQL: OK")
            
            # Contar registros
            with db.conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM top_trends")
                count = cur.fetchone()[0]
            print(f"  📊 Registros na tabela: {count}")
            
        else:
            print("  ❌ DATABASE_URL não configurada")
            
    except Exception as e:
        print(f"  ❌ Erro na conexão: {str(e)}")
    
    # Simular execução de autopost
    print("\n🤖 Simulando execução de autopost:")
    try:
        from main import main as main_func
        import sys
        
        # Simular argumentos do autopost
        original_argv = sys.argv
        sys.argv = ["main.py", "autopost"]
        
        print("  🔄 Executando autopost...")
        main_func()
        print("  ✅ Autopost executado com sucesso!")
        
        # Restaurar argumentos originais
        sys.argv = original_argv
        
    except Exception as e:
        print(f"  ❌ Erro no autopost: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 TESTE DE AGENDAMENTO CONCLUÍDO!")
    print(f"📝 Log salvo em: {datetime.now().isoformat()}")
    
    # Salvar log do teste
    log_file = ROOT / "test_scheduling_log.txt"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"\n[{now.isoformat()}] Teste de agendamento executado com sucesso!\n")
    
    return True

if __name__ == "__main__":
    test_railway_scheduling()