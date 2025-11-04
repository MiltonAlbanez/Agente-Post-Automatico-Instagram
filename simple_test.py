#!/usr/bin/env python3
"""
Teste ultra-simples para Railway - sem dependências externas.
"""

import os
import time
from datetime import datetime

def main():
    """Teste básico que só usa bibliotecas padrão do Python."""
    print("🚀 TESTE RAILWAY - Iniciando...")
    print(f"⏰ Horário: {datetime.now()}")
    print(f"🐍 Python funcionando no Railway!")
    
    # Verificar variáveis de ambiente
    print("\n📋 Variáveis de ambiente:")
    for key in ['OPENAI_API_KEY', 'INSTAGRAM_ACCESS_TOKEN', 'RAILWAY_ENVIRONMENT', 'DATABASE_URL']:
        value = os.getenv(key)
        status = "✅ Configurada" if value else "❌ Não encontrada"
        print(f"  - {key}: {status}")
    
    # Loop simples para manter o container ativo
    counter = 0
    while True:
        counter += 1
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] Loop #{counter} - Sistema ativo!")
        
        # Log a cada 5 minutos
        time.sleep(300)  # 5 minutos

if __name__ == "__main__":
    main()