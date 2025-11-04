#!/usr/bin/env python3
"""
Teste forçando o import correto
"""

import sys
import os

# Adicionar src ao path
sys.path.insert(0, 'src')

print("🔍 TESTE FORÇANDO IMPORT CORRETO")
print("=" * 50)

# Limpar qualquer cache existente
modules_to_clear = [
    'services.instagram_client_robust',
    'services.instagram_client', 
    'pipeline.generate_and_publish'
]

for module in modules_to_clear:
    if module in sys.modules:
        del sys.modules[module]
        print(f"🧹 Cache limpo: {module}")

print("\n🔧 FORÇANDO IMPORT CORRETO")
print("=" * 50)

try:
    # Primeiro, importar o InstagramClientRobust
    from services.instagram_client_robust import InstagramClientRobust
    print(f"✅ InstagramClientRobust importado: {InstagramClientRobust}")
    
    # Agora, modificar temporariamente o arquivo para garantir o import correto
    pipeline_file = 'src/pipeline/generate_and_publish.py'
    
    # Ler o arquivo atual
    with open(pipeline_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📄 Primeira linha atual: {content.split(chr(10))[0]}")
    
    # Verificar se o import está correto
    if 'from services.instagram_client_robust import InstagramClientRobust as InstagramClient' in content:
        print("✅ Import correto encontrado no arquivo")
        
        # Tentar importar diretamente
        import importlib.util
        spec = importlib.util.spec_from_file_location("pipeline.generate_and_publish", pipeline_file)
        pipeline_module = importlib.util.module_from_spec(spec)
        
        # Adicionar ao sys.modules antes de executar
        sys.modules['pipeline.generate_and_publish'] = pipeline_module
        
        # Executar o módulo
        spec.loader.exec_module(pipeline_module)
        
        # Verificar qual classe foi importada
        instagram_client_class = getattr(pipeline_module, 'InstagramClient', None)
        
        if instagram_client_class:
            print(f"✅ Classe importada: {instagram_client_class}")
            print(f"   Nome: {instagram_client_class.__name__}")
            print(f"   Módulo: {instagram_client_class.__module__}")
            
            if instagram_client_class.__name__ == 'InstagramClientRobust':
                print("🎉 SUCESSO: Import forçado funcionou!")
            else:
                print(f"❌ AINDA FALHOU: {instagram_client_class.__name__}")
        else:
            print("❌ InstagramClient não encontrado")
            
    else:
        print("❌ Import incorreto no arquivo")
        
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print("\n📊 CONCLUSÃO")
print("=" * 50)