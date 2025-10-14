#!/usr/bin/env python3
"""
Teste simples para verificar se o Railway consegue executar o sistema.
Este arquivo não depende de banco de dados.
"""

import os
import time
import schedule
from datetime import datetime

def test_post():
    """Função de teste que simula a criação de um post."""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] TESTE: Post automático executado com sucesso!")
    print(f"[{current_time}] Variáveis disponíveis:")
    print(f"  - OPENAI_API_KEY: {'✅ Configurada' if os.getenv('OPENAI_API_KEY') else '❌ Não encontrada'}")
    print(f"  - INSTAGRAM_ACCESS_TOKEN: {'✅ Configurada' if os.getenv('INSTAGRAM_ACCESS_TOKEN') else '❌ Não encontrada'}")
    print(f"  - RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT', 'Não encontrada')}")
    return True

def main():
    """Função principal que configura o scheduler de teste."""
    print("🚀 Iniciando sistema de teste no Railway...")
    print(f"⏰ Horário atual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Configurar um teste a cada 5 minutos
    schedule.every(5).minutes.do(test_post)
    
    # Executar um teste imediatamente
    test_post()
    
    print("📅 Scheduler configurado - teste a cada 5 minutos")
    print("🔄 Entrando no loop principal...")
    
    loop_count = 0
    while True:
        loop_count += 1
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Log a cada 10 iterações (aproximadamente a cada 10 minutos)
        if loop_count % 10 == 1:
            print(f"[{current_time}] Sistema ativo - Loop #{loop_count}")
            print(f"[{current_time}] Próximos testes agendados: {len(schedule.jobs)} jobs")
        
        # Executar tarefas pendentes
        schedule.run_pending()
        
        # Aguardar 1 minuto
        time.sleep(60)

if __name__ == "__main__":
    main()