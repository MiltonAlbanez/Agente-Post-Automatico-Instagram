#!/usr/bin/env python3
"""
Teste final após correção do import
"""

import sys
import os

print("🔍 TESTE FINAL - IMPORT CORRIGIDO")
print("=" * 50)

# Limpar completamente o cache
modules_to_clear = [mod for mod in sys.modules.keys() if 'instagram' in mod or 'pipeline' in mod]
for mod in modules_to_clear:
    del sys.modules[mod]
    print(f"🧹 Removido do cache: {mod}")

# Adicionar src ao path
sys.path.insert(0, 'src')

print(f"\n📁 Python path: {sys.path[:2]}")

# Verificar o arquivo atual
print("\n📄 VERIFICANDO ARQUIVO ATUAL")
print("=" * 50)

with open('src/pipeline/generate_and_publish.py', 'r', encoding='utf-8') as f:
    first_line = f.readline().strip()
    print(f"Primeira linha: {first_line}")

if 'from services.instagram_client_robust' in first_line:
    print("✅ Import correto encontrado!")
else:
    print("❌ Import ainda incorreto!")

print("\n🔄 IMPORTANDO NOVAMENTE")
print("=" * 50)

try:
    # Import direto do InstagramClientRobust
    from services.instagram_client_robust import InstagramClientRobust
    print(f"✅ InstagramClientRobust: {InstagramClientRobust.__name__}")
    
    # Import do pipeline
    from pipeline.generate_and_publish import InstagramClient
    print(f"✅ InstagramClient do pipeline: {InstagramClient}")
    print(f"   Nome da classe: {InstagramClient.__name__}")
    print(f"   Módulo: {InstagramClient.__module__}")
    print(f"   Tem _make_request_with_retry: {hasattr(InstagramClient, '_make_request_with_retry')}")
    print(f"   Tem publish_complete_robust: {hasattr(InstagramClient, 'publish_complete_robust')}")
    
    # Verificar se são a mesma classe
    if InstagramClient is InstagramClientRobust:
        print("🎉 SUCESSO TOTAL: São a mesma classe!")
    elif InstagramClient.__name__ == 'InstagramClientRobust':
        print("🎉 SUCESSO: É InstagramClientRobust!")
    else:
        print(f"❌ FALHA: É {InstagramClient.__name__}")
        
        # Debug adicional
        print(f"\nDEBUG:")
        print(f"InstagramClientRobust ID: {id(InstagramClientRobust)}")
        print(f"InstagramClient ID: {id(InstagramClient)}")
        
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print("\n📊 RESULTADO FINAL")
print("=" * 50)