#!/usr/bin/env python3
"""
Script de teste para verificar o algoritmo de detecção de pessoas
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.stories_image_processor import StoriesImageProcessor

def test_detection_with_image(image_url):
    """Testa o algoritmo de detecção com uma imagem específica"""
    
    print(f"Testando detecção com imagem: {image_url}")
    print("-" * 60)
    
    # Inicializar o processador
    processor = StoriesImageProcessor()
    
    # Baixar e processar a imagem
    try:
        image = processor.download_image(image_url)
        print(f"Imagem baixada com sucesso: {image.size}")
        
        # Testar detecção de melhor área
        test_text = "Este é um texto de teste para verificar o posicionamento automático em Stories do Instagram"
        # Simular altura do texto (aproximadamente 200px para um texto longo)
        text_height = 200
        best_area = processor.detect_best_text_area(image, text_height)
        print(f"Melhor área detectada: {best_area}")
        
        # Testar cada seção individualmente
        sections = ["top", "center", "bottom"]
        for section in sections:
            # Testar detecção de pessoa diretamente na imagem
            # Converter para array numpy para análise
            import numpy as np
            img_array = np.array(image)
            height = img_array.shape[0]
            section_height = height // 3
            
            if section == "top":
                section_data = img_array[:section_height]
            elif section == "center":
                section_data = img_array[section_height:2*section_height]
            else:  # bottom
                section_data = img_array[2*section_height:]
            
            person_score = processor._detect_person_like_features(section_data)
            print(f"Score de pessoa na seção {section}: {person_score:.2f}")
        
        print("-" * 60)
        print("Teste concluído!")
        
    except Exception as e:
        print(f"Erro durante o teste: {e}")

if __name__ == "__main__":
    # URL da imagem que sabemos que tem problema
    # Vamos usar uma URL de exemplo primeiro
    test_url = "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=600&fit=crop"
    
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    
    test_detection_with_image(test_url)