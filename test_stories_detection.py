#!/usr/bin/env python3
"""
Teste específico para verificar se a detecção de posicionamento nos Stories está funcionando
"""

import sys
from pathlib import Path
# Garantir que o diretório raiz (que contém 'src') está no PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from src.services.stories_image_processor import StoriesImageProcessor
from PIL import Image
import requests
from io import BytesIO

def test_detection_with_different_images():
    """Testa a detecção com diferentes tipos de imagens"""
    
    processor = StoriesImageProcessor()
    
    # Diferentes tipos de imagens para testar
    test_images = [
        {
            "name": "Imagem com pessoa (rosto visível)",
            "url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=600&fit=crop",
            "expected": "bottom"  # Esperamos que detecte pessoa e use bottom
        },
        {
            "name": "Paisagem sem pessoas",
            "url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&h=600&fit=crop",
            "expected": "top"  # Esperamos que use top ou center
        },
        {
            "name": "Arquitetura/Prédios",
            "url": "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=400&h=600&fit=crop",
            "expected": "any"  # Qualquer posição é aceitável
        }
    ]
    
    text_curto = "Texto curto para teste"
    text_longo = """🌟 Este é um texto muito longo para testar o algoritmo de detecção automática de posicionamento nos Stories do Instagram. 

O algoritmo deve detectar automaticamente se há pessoas na imagem e posicionar o texto de forma que não sobreponha rostos ou corpos.

#Teste #Algoritmo #Stories #Instagram #Detecção #Posicionamento"""
    
    print("=" * 80)
    print("🧪 TESTE DE DETECÇÃO DE POSICIONAMENTO NOS STORIES")
    print("=" * 80)
    
    for i, test_case in enumerate(test_images, 1):
        print(f"\n{i}. Testando: {test_case['name']}")
        print(f"   URL: {test_case['url']}")
        print("-" * 60)
        
        try:
            # Baixar e processar imagem
            response = requests.get(test_case['url'])
            image = Image.open(BytesIO(response.content))
            
            # Teste com texto curto
            print("   📝 Teste com texto CURTO:")
            detected_position_short = processor.detect_best_text_area(image, 100)  # 100px de altura
            print(f"   🎯 Posição detectada: {detected_position_short}")
            
            # Teste com texto longo
            print("   📝 Teste com texto LONGO:")
            detected_position_long = processor.detect_best_text_area(image, 800)  # 800px de altura
            print(f"   🎯 Posição detectada: {detected_position_long}")
            
            # Verificar se está funcionando corretamente
            if test_case['expected'] == "bottom":
                if detected_position_short == "bottom" or detected_position_long == "bottom":
                    print("   ✅ CORRETO: Detectou pessoa e usou bottom")
                else:
                    print("   ❌ ERRO: Deveria ter detectado pessoa e usado bottom")
            elif test_case['expected'] == "top":
                if detected_position_short in ["top", "center"]:
                    print("   ✅ CORRETO: Sem pessoa detectada, usou posição apropriada")
                else:
                    print("   ⚠️  ATENÇÃO: Posição inesperada para imagem sem pessoa")
            
            # Teste completo com processamento
            print("   🖼️  Teste de processamento completo:")
            processed_path = processor.process_and_save_for_stories_with_text(
                image_url=test_case['url'],
                text=text_longo,
                background_type="gradient",
                text_position="auto"
            )
            
            if os.path.exists(processed_path):
                file_size = os.path.getsize(processed_path)
                print(f"   ✅ Imagem processada: {file_size} bytes")
                
                # Limpar arquivo temporário
                try:
                    os.remove(processed_path)
                    print("   🗑️  Arquivo temporário removido")
                except:
                    print("   ⚠️  Não foi possível remover arquivo temporário")
            else:
                print("   ❌ ERRO: Imagem não foi processada")
                
        except Exception as e:
            print(f"   ❌ ERRO no teste: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("✅ TESTE DE DETECÇÃO CONCLUÍDO")
    print("=" * 80)

if __name__ == "__main__":
    test_detection_with_different_images()