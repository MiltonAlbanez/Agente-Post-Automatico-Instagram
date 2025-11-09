#!/usr/bin/env python3
"""
Teste simplificado do sistema de automação Railway
Executa o multirun real uma vez para testar a funcionalidade
"""

import subprocess
import sys
import os
from datetime import datetime

def log_message(message):
    """Log com timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def execute_real_multirun():
    """
    Executar multirun real
    """
    try:
        log_message("Executando multirun real...")
        
        # Executar o comando multirun
        result = subprocess.run(
            [sys.executable, "src/main.py", "multirun", "--limit", "1", "--only", "Milton_Albanez"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos de timeout
        )
        
        if result.returncode == 0:
            log_message("Multirun executado com sucesso!")
            log_message(f"Output: {result.stdout}")
        else:
            log_message(f"Erro no multirun: {result.stderr}")
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        log_message("Timeout no multirun - processo demorou mais de 5 minutos")
        return False
    except Exception as e:
        log_message(f"Erro inesperado no multirun: {str(e)}")
        return False

def main():
    """Função principal do teste"""
    log_message("=== INICIANDO TESTE SIMPLIFICADO ===")
    
    # Verificar se estamos no diretório correto
    if not os.path.exists("src/main.py"):
        log_message("ERRO: Arquivo src/main.py não encontrado!")
        log_message("Certifique-se de estar no diretório raiz do projeto")
        return
    
    # Executar multirun real
    success = execute_real_multirun()
    
    if success:
        log_message("✅ TESTE CONCLUÍDO COM SUCESSO!")
    else:
        log_message("❌ TESTE FALHOU!")
    
    log_message("=== FIM DO TESTE ===")

if __name__ == "__main__":
    main()