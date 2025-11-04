#!/usr/bin/env python3
"""
Teste simples para verificar o import da pipeline
"""

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, 'src')

print("🔍 TESTE SIMPLES DE IMPORT")
print("=" * 50)

try:
    # Importar diretamente do arquivo
    print("📁 Tentando importar de pipeline.generate_and_publish...")
    from pipeline.generate_and_publish import InstagramClient
    
    print(f"✅ Import bem-sucedido!")
    print(f"📋 Classe: {InstagramClient}")
    print(f"📋 Nome: {InstagramClient.__name__}")
    print(f"📋 Módulo: {InstagramClient.__module__}")
    
    # Verificar se tem os métodos robustos
    has_robust_method = hasattr(InstagramClient, 'publish_complete_robust')
    has_retry_method = hasattr(InstagramClient, '_make_request_with_retry')
    
    print(f"📋 Tem publish_complete_robust: {has_robust_method}")
    print(f"📋 Tem _make_request_with_retry: {has_retry_method}")
    
    if InstagramClient.__name__ == 'InstagramClientRobust':
        print("🎉 SUCESSO: É InstagramClientRobust!")
    else:
        print(f"❌ PROBLEMA: É {InstagramClient.__name__}")
        
except Exception as e:
    print(f"❌ ERRO no import: {e}")
    import traceback
    traceback.print_exc()

print("\n🔍 VERIFICANDO ARQUIVO DIRETAMENTE")
print("=" * 50)

# Verificar se o arquivo existe e ler a primeira linha
pipeline_file = 'src/pipeline/generate_and_publish.py'
if os.path.exists(pipeline_file):
    with open(pipeline_file, 'r', encoding='utf-8') as f:
        first_line = f.readline().strip()
        print(f"📄 Primeira linha do arquivo: {first_line}")
else:
    print(f"❌ Arquivo não encontrado: {pipeline_file}")