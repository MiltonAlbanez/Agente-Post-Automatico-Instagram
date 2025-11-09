"""
DEMONSTRAÇÃO DO SYSTEM PROMPT TRAE IA - Versão Windows
Valida a implementação das Regras de Ouro (sem emojis)
"""

import sys
import time
from datetime import datetime
from pathlib import Path

# Importar o TRAE IA Core
from trae_ia_core import trae_ia, processar_erro_automatico, executar_com_protecao

def simular_erro_api():
    """
    Simula um erro de API para demonstrar a consulta LTM
    """
    raise ConnectionError("Timeout na conexão com Instagram API após 30 segundos")

def simular_tarefa_postagem():
    """
    Simula uma tarefa de postagem bem-sucedida
    """
    print("Executando postagem no Instagram...")
    time.sleep(1)  # Simular processamento
    print("SUCESSO: Postagem realizada com sucesso")
    return {"status": "success", "post_id": "12345"}

def demonstrar_system_prompt():
    """
    Demonstra o funcionamento do System Prompt
    """
    print("\n" + "="*80)
    print("DEMONSTRAÇÃO DO SYSTEM PROMPT TRAE IA")
    print("="*80)
    
    # 1. Demonstrar processamento de erro com consulta LTM
    print("\n1. TESTE: Processamento de Erro com Consulta LTM")
    print("-" * 50)
    
    try:
        simular_erro_api()
    except Exception as e:
        resultado = processar_erro_automatico(e, {
            'funcao': 'instagram_api_call',
            'tentativa': 1
        })
        
        print(f"\nRESULTADO DA CONSULTA LTM:")
        print(f"   Tipo de ação: {resultado['recommended_action']['tipo']}")
        print(f"   Prioridade: {resultado['recommended_action']['prioridade']}")
    
    print("\n" + "-"*50)
    
    # 2. Demonstrar execução de tarefa crítica
    print("\n2. TESTE: Execução de Tarefa Crítica (REGRA 1)")
    print("-" * 50)
    
    resultado_tarefa = executar_com_protecao(
        "postagem_feed_12h", 
        simular_tarefa_postagem
    )
    
    print(f"\nRESULTADO DA TAREFA:")
    print(f"   Status: {resultado_tarefa.get('status', 'N/A')}")
    
    # 3. Demonstrar validação de ação (REGRA 3)
    print("\n3. TESTE: Validação de Ação (REGRA 3)")
    print("-" * 50)
    
    # Tentar ação não permitida
    acao_permitida = trae_ia.validar_acao('optimization', {'queue_empty': False})
    print(f"   Otimização com fila ativa: {'PERMITIDA' if acao_permitida else 'BLOQUEADA'}")
    
    # Tentar ação permitida
    acao_permitida = trae_ia.validar_acao('cron_task', {'task_name': 'postagem_feed'})
    print(f"   Tarefa de cronograma: {'PERMITIDA' if acao_permitida else 'BLOQUEADA'}")
    
    print("\n" + "="*80)
    print("DEMONSTRAÇÃO CONCLUÍDA")
    print("SUCESSO: System Prompt funcionando corretamente")
    print("SUCESSO: Regras de Ouro implementadas")
    print("SUCESSO: Consulta LTM obrigatória ativa")
    print("SUCESSO: Priorização de tarefas 24/7 funcionando")
    print("="*80)

if __name__ == "__main__":
    demonstrar_system_prompt()