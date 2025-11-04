#!/usr/bin/env python3
"""
Script de teste para verificar o algoritmo de detecção de posicionamento de texto em Stories
"""

import sys
from pathlib import Path
# Garantir que o diretório raiz (que contém 'src') está no PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from src.services.stories_image_processor import StoriesImageProcessor
import tempfile

def test_positioning_detection():
    """
    Testa o algoritmo de detecção de posicionamento com a imagem das 21h
    """
    print("🧪 Testando algoritmo de detecção de posicionamento...")
    
    # URL da imagem que foi usada no post das 21h
    test_image_url = "https://picsum.photos/1080/1080"
    
    # Texto de teste similar ao usado
    test_text = """Teste para stories 21h
#CoachingCristão #Transformação #DesenvolvimentoPessoal #Mindset #CoachingPNL #JornadaEmpreendedora #MindsetEmpreendedor #LiderançaConsciente #CoachingBrasil #NegóciosConscientes #DesenvolvimentoHumano #ÚltimoTrimestre"""
    
    try:
        # Inicializar processador
        processor = StoriesImageProcessor()
        
        # Baixar e processar imagem
        print("📥 Baixando imagem...")
        original_image = processor.download_image(test_image_url)
        print(f"✅ Imagem baixada: {original_image.size}")
        
        # Processar para formato Stories
        print("🔄 Processando para formato Stories...")
        stories_image = processor.process_image_for_stories(test_image_url, "gradient")
        print(f"✅ Imagem processada: {stories_image.size}")
        
        # Testar detecção de área
        print("🎯 Testando detecção de área...")
        
        # Simular cálculo de altura do texto
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(stories_image)
        
        try:
            font = ImageFont.truetype("arial.ttf", 72)
            font_size = 72
        except:
            font = ImageFont.load_default()
            font_size = 40
        
        # Quebrar texto em linhas
        max_width = processor.STORIES_WIDTH - 120
        lines = []
        words = test_text.split()
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(current_line)
        
        line_height = font_size + 10
        total_text_height = len(lines) * line_height
        
        print(f"📏 Altura total do texto: {total_text_height}px")
        print(f"📝 Número de linhas: {len(lines)}")
        
        # Testar detecção
        detected_position = processor.detect_best_text_area(stories_image, total_text_height)
        print(f"🎯 Posição detectada: {detected_position}")
        
        # Testar todas as posições para comparação
        positions = ["top", "center", "bottom"]
        for pos in positions:
            print(f"\n🧪 Testando posição: {pos}")
            test_image = processor.add_text_to_stories_image(stories_image.copy(), test_text, pos)
            
            # Salvar para análise visual
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'_test_{pos}.jpg')
            test_image.save(temp_file.name, 'JPEG', quality=95)
            print(f"💾 Salvo: {temp_file.name}")
        
        # Testar com posição automática
        print(f"\n🤖 Testando posição automática...")
        auto_image = processor.add_text_to_stories_image(stories_image.copy(), test_text, "auto")
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='_test_auto.jpg')
        auto_image.save(temp_file.name, 'JPEG', quality=95)
        print(f"💾 Salvo: {temp_file.name}")
        
        print("\n✅ Teste concluído! Verifique os arquivos gerados para análise visual.")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_positioning_detection()