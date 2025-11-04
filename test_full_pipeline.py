#!/usr/bin/env python3
"""
Script de teste completo para simular o pipeline real de Stories
"""

import sys
import os
from pathlib import Path
# Garantir que o diretório raiz (que contém 'src') está no PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from src.services.stories_image_processor import StoriesImageProcessor

def test_full_pipeline(image_url, text):
    """Testa o pipeline completo de processamento de Stories"""
    
    print(f"Testando pipeline completo com:")
    print(f"Imagem: {image_url}")
    print(f"Texto: {text[:50]}...")
    print("-" * 60)
    
    # Inicializar o processador
    processor = StoriesImageProcessor()
    
    try:
        # 1. Processar imagem para Stories com texto (simulando o pipeline real)
        print("1. Processando imagem para Stories com texto...")
        processed_image_path = processor.process_and_save_for_stories_with_text(
            image_url=image_url,
            text=text,
            background_type="gradient",
            text_position="auto"
        )
        
        print(f"✅ Imagem processada salva em: {processed_image_path}")
        
        # 2. Verificar se o arquivo foi criado
        if os.path.exists(processed_image_path):
            file_size = os.path.getsize(processed_image_path)
            print(f"✅ Arquivo criado com sucesso ({file_size} bytes)")
            
            # 3. Abrir e verificar a imagem processada
            from PIL import Image
            final_image = Image.open(processed_image_path)
            print(f"✅ Imagem final: {final_image.size} - {final_image.mode}")
            
            # 4. Limpar arquivo temporário
            processor.cleanup_temp_file(processed_image_path)
            print("✅ Arquivo temporário limpo")
            
        else:
            print("❌ Arquivo não foi criado")
        
        print("-" * 60)
        print("✅ Teste do pipeline completo concluído!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Usar uma imagem com pessoa para testar
    test_url = "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=600&fit=crop"
    
    # Texto longo similar ao que foi usado no post real
    test_text = """🌟 Transforme sua mentalidade e alcance o sucesso! 

No mundo dos negócios, a diferença entre quem prospera e quem apenas sobrevive está na mentalidade. É essencial para fluir e inovar, mesmo em tempos de incerteza. Encontre suas raízes invisíveis—valores, propósito e mentalidade—que encontramos a força para prosperar e transformar obstáculos em oportunidades. 

E você, como nutre suas raízes para florescer no seu caminho empreendedor?

#CoachingCristão #Transformação #DesenvolvimentoPessoal #Mindset #CoachingPNL #JornadaEmpreendedora #MindsetEmpreendedor #LiderançaConsciente #CoachingBrasil #NegóciosConscientes #DesenvolvimentoHumano #ÚltimoTrimestre"""
    
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    if len(sys.argv) > 2:
        test_text = sys.argv[2]
    
    test_full_pipeline(test_url, test_text)