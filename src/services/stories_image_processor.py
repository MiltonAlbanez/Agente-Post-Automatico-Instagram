import io
import requests
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageFont
import numpy as np
from typing import Tuple, Optional
import tempfile
import os
import random


class StoriesImageProcessor:
    """
    Serviço para processar imagens para o formato Stories do Instagram (9:16 - 1080x1920)
    """
    
    # Dimensões padrão para Stories do Instagram
    STORIES_WIDTH = 1080
    STORIES_HEIGHT = 1920
    STORIES_RATIO = STORIES_HEIGHT / STORIES_WIDTH  # 16:9 = 1.777...
    
    def __init__(self):
        pass
    
    def download_image(self, image_url: str) -> Image.Image:
        """
        Baixa uma imagem de uma URL e retorna um objeto PIL Image
        """
        try:
            # Normalizar URL para preferir JPEG em hosts comuns (evitar WEBP)
            normalized_url = image_url
            try:
                if "images.unsplash.com" in image_url:
                    # Forçar JPEG em vez de auto=format que pode retornar WEBP
                    if "auto=format" in normalized_url:
                        normalized_url = normalized_url.replace("auto=format", "fm=jpg")
                    elif "fm=" not in normalized_url:
                        sep = "&" if "?" in normalized_url else "?"
                        normalized_url = f"{normalized_url}{sep}fm=jpg"
                elif "picsum.photos" in image_url and not image_url.lower().endswith(".jpg"):
                    # picsum suporta formato via parâmetros; garantir JPEG
                    sep = "&" if "?" in normalized_url else "?"
                    normalized_url = f"{normalized_url}{sep}format=jpg"
            except Exception:
                normalized_url = image_url

            # Sessão com retries exponenciais para maior robustez
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry

            retry_strategy = Retry(
                total=3,
                connect=3,
                read=3,
                backoff_factor=1.5,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET"],
            )

            adapter = HTTPAdapter(max_retries=retry_strategy)
            session = requests.Session()
            session.mount("http://", adapter)
            session.mount("https://", adapter)

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
                "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
            }

            response = session.get(normalized_url, timeout=60, headers=headers)
            response.raise_for_status()
            return Image.open(io.BytesIO(response.content)).convert('RGB')
        except Exception as e:
            raise RuntimeError(f"Erro ao baixar imagem: {e}")
    
    def get_dominant_colors(self, image: Image.Image, num_colors: int = 3) -> list:
        """
        Extrai as cores dominantes da imagem para criar o gradiente de fundo
        """
        # Redimensionar para acelerar o processamento
        small_image = image.resize((150, 150))
        
        # Converter para array numpy
        img_array = np.array(small_image)
        pixels = img_array.reshape(-1, 3)
        
        # Usar k-means simples para encontrar cores dominantes
        try:
            from sklearn.cluster import KMeans
            kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
            kmeans.fit(pixels)
            colors = kmeans.cluster_centers_.astype(int)
            return [tuple(color) for color in colors]
        except ImportError:
            # Fallback se sklearn não estiver disponível
            return self._get_dominant_colors_simple(image, num_colors)
    
    def _get_dominant_colors_simple(self, image: Image.Image, num_colors: int = 3) -> list:
        """
        Método alternativo para extrair cores dominantes sem sklearn
        """
        # Reduzir cores da imagem
        quantized = image.quantize(colors=num_colors)
        palette = quantized.getpalette()
        
        # Extrair as cores mais frequentes
        colors = []
        for i in range(num_colors):
            r = palette[i * 3]
            g = palette[i * 3 + 1]
            b = palette[i * 3 + 2]
            colors.append((r, g, b))
        
        return colors
    
    def create_gradient_background(self, width: int, height: int, colors: list) -> Image.Image:
        """
        Cria um fundo com gradiente baseado nas cores dominantes
        """
        # Criar imagem base
        background = Image.new('RGB', (width, height))
        
        if len(colors) < 2:
            # Se só temos uma cor, usar um gradiente suave dela
            base_color = colors[0] if colors else (128, 128, 128)
            # Criar variações mais claras e escuras
            colors = [
                tuple(max(0, min(255, c + 30)) for c in base_color),
                base_color,
                tuple(max(0, min(255, c - 30)) for c in base_color)
            ]
        
        # Criar gradiente vertical
        for y in range(height):
            # Calcular posição no gradiente (0.0 a 1.0)
            position = y / height
            
            # Interpolar entre as cores
            if position <= 0.5:
                # Primeira metade: cor 0 para cor 1
                t = position * 2
                color = self._interpolate_color(colors[0], colors[1], t)
            else:
                # Segunda metade: cor 1 para cor 2 (se existir)
                t = (position - 0.5) * 2
                end_color = colors[2] if len(colors) > 2 else colors[1]
                color = self._interpolate_color(colors[1], end_color, t)
            
            # Desenhar linha horizontal
            for x in range(width):
                background.putpixel((x, y), color)
        
        # Aplicar blur suave para suavizar o gradiente
        background = background.filter(ImageFilter.GaussianBlur(radius=2))
        
        return background
    
    def _interpolate_color(self, color1: tuple, color2: tuple, t: float) -> tuple:
        """
        Interpola entre duas cores RGB
        """
        return tuple(
            int(color1[i] + (color2[i] - color1[i]) * t)
            for i in range(3)
        )
    
    def create_blurred_background(self, image: Image.Image, width: int, height: int) -> Image.Image:
        """
        Cria um fundo borrado baseado na imagem original
        """
        # Redimensionar a imagem para cobrir toda a área
        img_ratio = image.width / image.height
        target_ratio = width / height
        
        if img_ratio > target_ratio:
            # Imagem é mais larga, ajustar pela altura
            new_height = height
            new_width = int(height * img_ratio)
        else:
            # Imagem é mais alta, ajustar pela largura
            new_width = width
            new_height = int(width / img_ratio)
        
        # Redimensionar e centralizar
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Cortar para o tamanho exato
        left = (new_width - width) // 2
        top = (new_height - height) // 2
        background = resized.crop((left, top, left + width, top + height))
        
        # Aplicar blur pesado
        background = background.filter(ImageFilter.GaussianBlur(radius=15))
        
        # Reduzir opacidade/saturação
        enhancer = ImageEnhance.Color(background)
        background = enhancer.enhance(0.3)  # Reduzir saturação
        
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.7)  # Escurecer um pouco
        
        return background
    
    def process_image_for_stories(self, image_url: str, background_type: str = "gradient") -> Image.Image:
        """
        Processa uma imagem para o formato Stories (9:16)
        
        Args:
            image_url: URL da imagem original
            background_type: "gradient" ou "blurred" para tipo de fundo
            
        Returns:
            Image.Image: Imagem processada no formato 9:16
        """
        # Baixar imagem original
        original_image = self.download_image(image_url)
        
        # Verificar se já está no formato correto
        current_ratio = original_image.height / original_image.width
        if abs(current_ratio - self.STORIES_RATIO) < 0.01:
            # Já está próximo do formato 9:16, apenas redimensionar
            return original_image.resize((self.STORIES_WIDTH, self.STORIES_HEIGHT), Image.Resampling.LANCZOS)
        
        # Criar fundo baseado no tipo escolhido
        if background_type == "blurred":
            background = self.create_blurred_background(
                original_image, self.STORIES_WIDTH, self.STORIES_HEIGHT
            )
        else:  # gradient
            dominant_colors = self.get_dominant_colors(original_image)
            background = self.create_gradient_background(
                self.STORIES_WIDTH, self.STORIES_HEIGHT, dominant_colors
            )
        
        # Calcular dimensões para centralizar a imagem original
        img_ratio = original_image.width / original_image.height
        
        if img_ratio > (self.STORIES_WIDTH / self.STORIES_HEIGHT):
            # Imagem é mais larga, ajustar pela largura
            new_width = self.STORIES_WIDTH
            new_height = int(self.STORIES_WIDTH / img_ratio)
        else:
            # Imagem é mais alta, ajustar pela altura
            new_height = self.STORIES_HEIGHT
            new_width = int(self.STORIES_HEIGHT * img_ratio)
        
        # Redimensionar imagem original mantendo proporção
        resized_image = original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Calcular posição para centralizar
        x_offset = (self.STORIES_WIDTH - new_width) // 2
        y_offset = (self.STORIES_HEIGHT - new_height) // 2
        
        # Colar imagem redimensionada no fundo
        background.paste(resized_image, (x_offset, y_offset))
        
        return background
    
    def save_processed_image(self, processed_image: Image.Image, quality: int = 95) -> str:
        """
        Salva a imagem processada em um arquivo temporário e retorna o caminho
        """
        # Criar arquivo temporário
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        temp_path = temp_file.name
        temp_file.close()
        
        # Salvar imagem
        processed_image.save(temp_path, 'JPEG', quality=quality, optimize=True)
        
        return temp_path
    
    def process_and_save_for_stories(self, image_url: str, background_type: str = "gradient") -> str:
        """
        Processa uma imagem para Stories e salva em arquivo temporário
        
        Returns:
            str: Caminho do arquivo temporário com a imagem processada
        """
        processed_image = self.process_image_for_stories(image_url, background_type)
        return self.save_processed_image(processed_image)
    
    def generate_short_catchphrase(self, content: str, caption: str = None) -> str:
        """
        Gera uma frase curta e impactante baseada no conteúdo do post
        
        Args:
            content: Conteúdo principal do post
            caption: Caption do post (opcional)
            
        Returns:
            str: Frase curta de efeito (máximo 3-4 palavras)
        """
        # Combinar conteúdo e caption para análise
        full_text = content
        if caption:
            full_text += " " + caption
        
        # Converter para minúsculas para análise
        text_lower = full_text.lower()
        
        # Palavras-chave para diferentes tipos de conteúdo
        leadership_keywords = ["liderança", "líder", "autoridade", "comando", "gestão", "equipe", "influência"]
        pnl_keywords = ["pnl", "programação", "neurolinguística", "modelagem", "excelência", "comportamento"]
        growth_keywords = ["crescimento", "desenvolvimento", "evolução", "progresso", "melhoria", "transformação"]
        inspiration_keywords = ["inspiração", "motivação", "sucesso", "conquista", "realização", "objetivo"]
        business_keywords = ["negócio", "empresa", "vendas", "marketing", "estratégia", "resultado"]
        
        # Detectar categoria do conteúdo e selecionar frases apropriadas
        if any(keyword in text_lower for keyword in leadership_keywords):
            catchphrases = [
                "Autoridade é Liderança",
                "Lidere com Propósito",
                "Influência Positiva",
                "Liderança Autêntica",
                "Comando Inspirador",
                "Líder Transformador"
            ]
        elif any(keyword in text_lower for keyword in pnl_keywords):
            catchphrases = [
                "Excelência em Ação",
                "Modelagem de Sucesso",
                "Transformação Mental",
                "Programação Positiva",
                "Mente Poderosa",
                "Mudança Consciente"
            ]
        elif any(keyword in text_lower for keyword in growth_keywords):
            catchphrases = [
                "Crescimento Contínuo",
                "Evolução Pessoal",
                "Desenvolvimento Total",
                "Progresso Constante",
                "Transformação Real",
                "Melhoria Contínua"
            ]
        elif any(keyword in text_lower for keyword in inspiration_keywords):
            catchphrases = [
                "Inspiração Diária",
                "Sucesso Garantido",
                "Conquiste Seus Sonhos",
                "Realize o Impossível",
                "Motivação Pura",
                "Objetivo Alcançado"
            ]
        elif any(keyword in text_lower for keyword in business_keywords):
            catchphrases = [
                "Resultados Excepcionais",
                "Estratégia Vencedora",
                "Negócio de Sucesso",
                "Performance Superior",
                "Vendas Explosivas",
                "ROI Garantido"
            ]
        else:
            # Frases genéricas para qualquer conteúdo
            catchphrases = [
                "Impacto Transformador",
                "Diferencial Único",
                "Qualidade Superior",
                "Excelência Total",
                "Resultado Perfeito",
                "Mudança Positiva"
            ]
        
        # Selecionar frase aleatória
        selected_phrase = random.choice(catchphrases)
        return selected_phrase
    
    def add_text_to_stories_image(self, image: Image.Image, text: str, position: str = "auto") -> Image.Image:
        """
        Adiciona texto estilizado à imagem dos Stories
        
        Args:
            image: Imagem PIL processada para Stories
            text: Texto a ser adicionado
            position: Posição do texto ("top", "center", "bottom", "auto")
                     "auto" usa detecção inteligente para encontrar a melhor área
        
        Returns:
            Image.Image: Imagem com texto adicionado
        """
        # Criar uma cópia da imagem para não modificar a original
        img_with_text = image.copy()
        draw = ImageDraw.Draw(img_with_text)
        
        # Detectar se é uma frase curta (até 4 palavras)
        word_count = len(text.split())
        is_short_phrase = word_count <= 4
        
        # Configurações de texto baseadas no tipo
        if is_short_phrase:
            max_width = self.STORIES_WIDTH - 80  # Margem menor para frases curtas
        else:
            max_width = self.STORIES_WIDTH - 120  # Margem padrão para textos longos
        
        # Tentar carregar fonte personalizada, usar padrão se não encontrar
        try:
            if is_short_phrase:
                # Fonte maior para frases curtas e impactantes
                font_size = 96
                font = ImageFont.truetype("arial.ttf", font_size)
            else:
                # Fonte padrão para textos longos
                font_size = 72
                font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.load_default()
                font_size = 60 if is_short_phrase else 40
            except:
                font = ImageFont.load_default()
                font_size = 60 if is_short_phrase else 40
        
        # Quebrar texto em linhas para caber na largura
        lines = []
        words = text.split()
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
                    # Palavra muito longa, forçar quebra
                    lines.append(word)
        
        if current_line:
            lines.append(current_line)
        
        # Calcular altura total do texto
        line_height = font_size + 10  # Espaçamento entre linhas
        total_text_height = len(lines) * line_height
        
        # Determinar posição Y baseada na posição escolhida
        if position == "auto" or position is None:
            if is_short_phrase:
                # Para frases curtas, priorizar posições que não interfiram com o conteúdo
                detected_position = self.detect_best_text_area_for_short_phrase(image, total_text_height)
            else:
                # Usar detecção padrão para textos longos
                detected_position = self.detect_best_text_area(image, total_text_height)
            position = detected_position
        
        # Posicionamento otimizado baseado no tipo de texto
        if is_short_phrase:
            # Posições mais próximas das bordas para frases curtas
            if position == "top":
                start_y = 100  # Mais próximo do topo
            elif position == "center":
                start_y = (self.STORIES_HEIGHT - total_text_height) // 2
            else:  # bottom
                start_y = self.STORIES_HEIGHT - total_text_height - 100  # Mais próximo do fundo
        else:
            # Posições padrão para textos longos
            if position == "top":
                start_y = 150  # Margem do topo
            elif position == "center":
                start_y = (self.STORIES_HEIGHT - total_text_height) // 2
            else:  # bottom
                start_y = self.STORIES_HEIGHT - total_text_height - 150  # Margem do fundo
        
        # Desenhar cada linha de texto
        for i, line in enumerate(lines):
            # Calcular posição X para centralizar
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (self.STORIES_WIDTH - text_width) // 2
            y = start_y + (i * line_height)
            
            # Desenhar sombra do texto (para melhor legibilidade)
            shadow_offset = 3
            draw.text((x + shadow_offset, y + shadow_offset), line, font=font, fill=(0, 0, 0, 180))
            
            # Desenhar texto principal em branco
            draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
        
        return img_with_text
    
    def process_image_for_stories_with_text(self, image_url: str, text: str = None, 
                                          background_type: str = "gradient", 
                                          text_position: str = "auto") -> Image.Image:
        """
        Processa uma imagem para Stories e adiciona texto se fornecido
        
        Args:
            image_url: URL da imagem original
            text: Texto a ser adicionado (opcional)
            background_type: "gradient" ou "blurred" para tipo de fundo
            text_position: Posição do texto ("top", "center", "bottom")
            
        Returns:
            Image.Image: Imagem processada no formato 9:16 com texto
        """
        # Processar imagem para formato Stories
        processed_image = self.process_image_for_stories(image_url, background_type)
        
        # Adicionar texto se fornecido
        if text and text.strip():
            processed_image = self.add_text_to_stories_image(processed_image, text, text_position)
        
        return processed_image
    
    def process_and_save_for_stories_with_text(self, image_url: str, text: str = None,
                                             background_type: str = "gradient",
                                             text_position: str = "auto") -> str:
        """
        Processa uma imagem para Stories com texto e salva em arquivo temporário
        
        Args:
            image_url: URL da imagem original
            text: Texto a ser adicionado (opcional)
            background_type: "gradient" ou "blurred" para tipo de fundo
            text_position: Posição do texto ("top", "center", "bottom")
            
        Returns:
            str: Caminho do arquivo temporário com a imagem processada
        """
        processed_image = self.process_image_for_stories_with_text(
            image_url, text, background_type, text_position
        )
        return self.save_processed_image(processed_image)
    
    def detect_best_text_area(self, image: Image.Image, text_height: int) -> str:
        """
        Detecta a melhor área da imagem para posicionar o texto
        baseado na análise de complexidade visual e detecção de pessoas
        """
        # Converter para RGB se necessário
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Redimensionar para análise mais rápida
        analysis_img = image.resize((270, 480))  # 1/4 do tamanho original
        img_array = np.array(analysis_img)
        
        # Dividir imagem em 3 seções: topo, centro, fundo
        height = img_array.shape[0]
        section_height = height // 3
        
        sections = {
            'top': img_array[0:section_height],
            'center': img_array[section_height:2*section_height], 
            'bottom': img_array[2*section_height:]
        }
        
        section_scores = {}
        
        for section_name, section_data in sections.items():
            # Calcular variância de cores (complexidade visual)
            variance = np.var(section_data)
            
            # Calcular uniformidade de cores
            section_flat = section_data.reshape(-1, 3)
            unique_colors = len(np.unique(section_flat.view(np.dtype((np.void, section_flat.dtype.itemsize * 3)))))
            uniformity = 1.0 / (unique_colors + 1)  # Mais uniforme = melhor para texto
            
            # Calcular brilho médio
            brightness = np.mean(section_data)
            
            # Detectar bordas (complexidade estrutural)
            gray_section = np.mean(section_data, axis=2)
            edges = np.abs(np.gradient(gray_section)).sum()
            edge_density = edges / gray_section.size
            
            # Detectar possível presença de pessoas/rostos
            person_penalty = self._detect_person_like_features(section_data)
            
            # Penalizar seções com pessoas detectadas
            position_penalty = 1.0
            if section_name == 'top' and person_penalty > 0.2:
                position_penalty = 0.1  # Penalidade severa para o topo
            elif section_name == 'center' and person_penalty > 0.3:
                position_penalty = 0.3  # Penalidade moderada para o centro
            elif person_penalty > 0.4:
                position_penalty = 0.2  # Penalidade alta para qualquer seção
            
            # Score final: menor complexidade visual = melhor para texto
            base_score = (1.0 / (variance + 1)) * uniformity * (1.0 / (edge_density + 1))
            score = base_score * position_penalty * (1.0 - person_penalty * 0.8)
            
            section_scores[section_name] = score
        
        # Encontrar a seção com melhor score
        best_section = max(section_scores, key=section_scores.get)
        
        # Lógica adicional para textos muito longos
        available_height = self.STORIES_HEIGHT // 3 - 100  # Margem de segurança
        
        if text_height > available_height:
            return 'bottom'  # Sempre forçar bottom para textos longos
        
        # Lógica conservadora para evitar pessoas
        top_person_penalty = self._detect_person_like_features(
            np.array(image.resize((270, 480)))[:160]  # Seção top
        )
        if best_section == 'top' and top_person_penalty > 0.15:
            return 'bottom'
        
        # Se o melhor score for 'top' mas com baixo score, usar 'bottom'
        if best_section == 'top' and section_scores['top'] < 0.01:
            return 'bottom'
        
        # Se o melhor score for 'center' mas detectar pessoa, usar 'bottom'
        if best_section == 'center':
            center_person_penalty = self._detect_person_like_features(
                np.array(image.resize((270, 480)))[160:320]  # Seção center
            )
            if center_person_penalty > 0.25:
                return 'bottom'
        
        return best_section
    
    def detect_best_text_area_for_short_phrase(self, image: Image.Image, text_height: int) -> str:
        """
        Detecta a melhor área para posicionar frases curtas de efeito
        Prioriza posições que maximizem o impacto visual sem interferir com pessoas
        """
        # Redimensionar para análise mais rápida
        analysis_image = image.resize((270, 480))
        img_array = np.array(analysis_image)
        
        # Definir seções específicas para frases curtas (mais focadas)
        sections = {
            'top': img_array[:120],      # Seção superior menor
            'bottom': img_array[360:]    # Seção inferior menor
        }
        
        section_scores = {}
        
        for section_name, section_data in sections.items():
            # Detectar pessoas na seção
            person_penalty = self._detect_person_like_features(section_data)
            
            # Analisar uniformidade da área (melhor para legibilidade)
            gray_section = np.mean(section_data, axis=2)
            variance = np.var(gray_section)
            
            # Analisar contraste (importante para frases de impacto)
            brightness = np.mean(gray_section)
            contrast_score = 1.0 if brightness < 128 else 0.8  # Preferir fundos escuros
            
            # Penalidades específicas para frases curtas
            if section_name == 'top':
                position_bonus = 1.2  # Topo é visualmente mais impactante
                person_penalty_multiplier = 2.0  # Penalidade dobrada para pessoas no topo
            else:  # bottom
                position_bonus = 1.0
                person_penalty_multiplier = 1.5
            
            # Score final para frases curtas
            base_score = (1.0 / (variance + 1)) * contrast_score * position_bonus
            final_score = base_score * (1.0 - person_penalty * person_penalty_multiplier)
            
            section_scores[section_name] = max(final_score, 0.01)  # Evitar scores negativos
        
        # Escolher a melhor posição
        best_position = max(section_scores, key=section_scores.get)
        
        # Lógica de segurança: se detectar pessoa no topo, forçar bottom
        if best_position == 'top':
            top_person_penalty = self._detect_person_like_features(sections['top'])
            if top_person_penalty > 0.1:  # Muito sensível para frases curtas
                return 'bottom'
        
        return best_position
    
    def _detect_person_like_features(self, section_data: np.ndarray) -> float:
        """
        Detecta características que podem indicar presença de pessoas
        Retorna um valor entre 0.0 (sem pessoa) e 1.0 (muito provável pessoa)
        """
        # Converter para tons de cinza para análise
        gray = np.mean(section_data, axis=2)
        
        # Detectar tons de pele (faixas de cor típicas)
        skin_pixels = 0
        total_pixels = section_data.shape[0] * section_data.shape[1]
        
        for i in range(section_data.shape[0]):
            for j in range(section_data.shape[1]):
                # Converter para inteiros Python para evitar overflow de uint8
                r_u8, g_u8, b_u8 = section_data[i, j]
                r = int(r_u8)
                g = int(g_u8)
                b = int(b_u8)
                # Faixas típicas de tons de pele (com diferenças calculadas em inteiro)
                if (r > 95 and g > 40 and b > 20 and 
                    (max(r, g, b) - min(r, g, b)) > 15 and
                    abs(r - g) > 15 and r > g and r > b):
                    skin_pixels += 1
        
        skin_ratio = skin_pixels / total_pixels
        
        # Detectar padrões circulares/ovais (possíveis rostos)
        try:
            from scipy import ndimage
            # Aplicar filtro para detectar formas circulares
            laplacian = ndimage.laplace(gray)
            circular_features = np.sum(np.abs(laplacian)) / gray.size
            circular_score = min(circular_features / 100.0, 1.0)  # Normalizar
        except ImportError:
            # Fallback se scipy não estiver disponível
            circular_score = 0.0
        
        # Detectar variação de brilho típica de rostos
        brightness_var = np.var(gray)
        brightness_score = min(brightness_var / 1000.0, 1.0)  # Normalizar
        
        # Score final combinado
        person_score = (skin_ratio * 0.6 + circular_score * 0.2 + brightness_score * 0.2)
        
        return min(person_score, 1.0)

    def cleanup_temp_file(self, file_path: str):
        """
        Remove arquivo temporário após uso
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            pass