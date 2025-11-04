#!/usr/bin/env python3
"""
Script para testar diretamente o processamento de Stories
"""

import sys
from pathlib import Path
# Garantir que o diretório raiz (que contém 'src') está no PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from src.services.stories_image_processor import StoriesImageProcessor

def test_stories_direct():
    """Testa o processamento direto de Stories"""
    
    # Imagem com pessoa
    image_url = "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=600&fit=crop"
    
    # Texto longo
    text = """🌟 Transforme sua mentalidade e alcance o sucesso! 

A verdadeira liderança vai além do individual e é sobre inspirar o crescimento de todos ao nosso redor. Com a Programação Neurolinguística (PNL), aprendemos a Modelagem de Excelência, que nos permite transformar a nossa vida ao estudar os grandes líderes do passado.

🚀 Pronto para fazer parte dessa jornada? Identifique modelos de sucesso, adote novas crenças e pratique diariamente. Vamos expandir juntos nossa visão e impactar o mundo!

#Liderança #PNL #ModelagemDeExcelência #CrescimentoPessoal #Inspiração #Sucesso #Transformação"""
    
    print("=" * 60)
    print("🧪 TESTE DIRETO DE STORIES")
    print("=" * 60)
    print(f"Imagem: {image_url}")
    print(f"Texto: {text[:100]}...")
    print("=" * 60)
    
    try:
        # Inicializar processador
        processor = StoriesImageProcessor()
        
        print("1. Processando imagem para Stories com texto...")
        
        # Processar imagem
        processed_image_path = processor.process_and_save_for_stories_with_text(
            image_url=image_url,
            text=text,
            background_type="gradient",
            text_position="auto"
        )
        
        print(f"✅ Imagem processada salva em: {processed_image_path}")
        
        # Verificar se o arquivo foi criado
        if os.path.exists(processed_image_path):
            file_size = os.path.getsize(processed_image_path)
            print(f"✅ Arquivo criado com sucesso ({file_size} bytes)")
            
            # Verificar dimensões da imagem
            from PIL import Image
            with Image.open(processed_image_path) as img:
                print(f"✅ Imagem final: {img.size} - {img.mode}")
        else:
            print("❌ Arquivo não foi criado")
            
        # Limpar arquivo temporário
        try:
            os.remove(processed_image_path)
            print("✅ Arquivo temporário limpo")
        except Exception as e:
            print(f"Erro ao remover arquivo temporário {processed_image_path}: {e}")
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 60)
    print("✅ Teste direto de Stories concluído!")

if __name__ == "__main__":
    test_stories_direct()