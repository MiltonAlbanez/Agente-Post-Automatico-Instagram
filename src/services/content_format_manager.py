"""
Sistema de gerenciamento de formatos de conteúdo para Instagram.
Oferece diferentes estilos de posts com prompts otimizados.
"""
import random
from typing import Dict, Tuple
from .cta_manager import CTAManager, get_cta_for_post


class ContentFormatManager:
    """Gerencia diferentes formatos de conteúdo para posts do Instagram."""
    
    def __init__(self):
        self.cta_manager = CTAManager()
        self.formats = {
            "standard": {
                "weight": 40,  # 40% dos posts
                "description": "Post padrão com narrativa completa"
            },
            "quote": {
                "weight": 20,  # 20% dos posts
                "description": "Post em formato de citação inspiradora"
            },
            "tip": {
                "weight": 25,  # 25% dos posts
                "description": "Post com dica prática numerada"
            },
            "question": {
                "weight": 15,  # 15% dos posts
                "description": "Post focado em engajamento com pergunta"
            }
        }
    
    def get_random_format(self) -> str:
        """Retorna um formato aleatório baseado nos pesos definidos."""
        formats = list(self.formats.keys())
        weights = [self.formats[f]["weight"] for f in formats]
        return random.choices(formats, weights=weights)[0]
    
    def get_format_prompt(self, format_type: str, content_theme: str = None, original_text: str = None) -> str:
        """Retorna o prompt específico para o formato escolhido com CTA automático."""
        
        # Gerar CTA específico para o formato e contexto
        cta = self.cta_manager.get_cta_with_context(format_type, original_text) if original_text else self.cta_manager.get_cta_for_format(format_type, content_theme)
        
        prompts = {
            "standard": f"""
**FORMATO: POST PADRÃO**
Crie uma legenda narrativa completa seguindo a estrutura padrão:
- Gancho inicial impactante
- Desenvolvimento com conceitos de Coaching/PNL
- Termine com o call-to-action específico fornecido
- Hashtags dinâmicas contextuais

Exemplo de estrutura:
[Frase impactante inicial]

[Desenvolvimento do tema...]

{cta}

[Hashtags]
""",
            
            "quote": f"""
**FORMATO: CITAÇÃO INSPIRADORA**
Crie uma legenda em formato de citação:
- Comece com uma frase marcante entre aspas (sua própria criação, não de terceiros)
- Explique o significado prático da frase para empreendedores
- Conecte com conceitos de desenvolvimento pessoal
- Termine com o call-to-action específico fornecido
- Use emojis estratégicos (máximo 3)
- Hashtags dinâmicas contextuais

Exemplo de estrutura:
"[Frase inspiradora original]"

[Explicação prática da frase...]

{cta}

[Hashtags]
""",
            
            "tip": f"""
**FORMATO: DICA PRÁTICA**
Crie uma legenda com dica numerada:
- Título: "X dicas para [tema específico]"
- Liste 3-5 dicas práticas e aplicáveis
- Cada dica deve ser concisa e acionável
- Termine com o call-to-action específico fornecido
- Use emojis para destacar cada dica
- Hashtags dinâmicas contextuais

Exemplo de estrutura:
🎯 [Número] dicas para [tema específico]:

1️⃣ [Dica prática 1]
2️⃣ [Dica prática 2]
3️⃣ [Dica prática 3]

{cta}

[Hashtags]
""",
            
            "question": f"""
**FORMATO: ENGAJAMENTO COM PERGUNTA**
Crie uma legenda focada em engajamento:
- Comece com uma pergunta provocativa
- Desenvolva o tema brevemente (máximo 3 parágrafos)
- Faça mais 2-3 perguntas relacionadas ao longo do texto
- Termine com o call-to-action específico fornecido
- Use linguagem conversacional e próxima
- Hashtags dinâmicas contextuais

Exemplo de estrutura:
[Pergunta provocativa inicial]

[Desenvolvimento breve do tema...]

[Pergunta intermediária]

{cta}

[Hashtags]
"""
        }
        
        return prompts.get(format_type, prompts["standard"])
    
    def get_image_style_for_format(self, format_type: str) -> str:
        """Retorna o estilo de imagem mais adequado para cada formato."""
        
        image_styles = {
            "standard": "Imagem conceitual equilibrada com elementos naturais ou urbanos",
            "quote": "Imagem minimalista com espaço para texto, tons suaves, elementos abstratos",
            "tip": "Imagem dinâmica com elementos que sugiram ação e movimento",
            "question": "Imagem que convide à reflexão, elementos simétricos ou caminhos"
        }
        
        return image_styles.get(format_type, image_styles["standard"])
    
    def enhance_replicate_prompt(self, base_prompt: str, format_type: str) -> str:
        """Aprimora o prompt do Replicate baseado no formato escolhido."""
        
        format_enhancements = {
            "quote": " Composição minimalista com muito espaço negativo, ideal para sobreposição de texto.",
            "tip": " Elementos visuais dinâmicos que sugiram movimento e ação.",
            "question": " Composição que convide à contemplação e reflexão.",
            "standard": " Composição equilibrada e versátil."
        }
        
        enhancement = format_enhancements.get(format_type, format_enhancements["standard"])
        return base_prompt + enhancement
    
    def get_content_analysis(self, content: str) -> Dict[str, any]:
        """Analisa o conteúdo para sugerir o melhor formato."""
        
        content_lower = content.lower()
        
        # Indicadores para cada formato
        format_indicators = {
            "quote": ["frase", "disse", "citação", "palavras", "expressão"],
            "tip": ["dica", "passo", "método", "estratégia", "técnica", "como"],
            "question": ["pergunta", "questão", "você", "qual", "como", "por que"],
            "standard": ["história", "experiência", "jornada", "processo"]
        }
        
        scores = {}
        for format_type, indicators in format_indicators.items():
            score = sum(1 for indicator in indicators if indicator in content_lower)
            scores[format_type] = score
        
        # Formato sugerido baseado na maior pontuação
        suggested_format = max(scores, key=scores.get) if max(scores.values()) > 0 else "standard"
        
        return {
            "suggested_format": suggested_format,
            "scores": scores,
            "confidence": max(scores.values()) / len(format_indicators[suggested_format])
        }


# Função utilitária para integração
def get_format_enhanced_prompt(base_prompt: str, content: str = "", force_format: str = None, original_text: str = None) -> tuple[str, str]:
    """
    Retorna prompt aprimorado com formato específico e CTAs automáticos.
    
    Args:
        base_prompt: Prompt base da legenda
        content: Conteúdo para análise (opcional)
        force_format: Forçar formato específico (opcional)
        original_text: Texto original para contexto de CTA (opcional)
    
    Returns:
        Tuple com (prompt_aprimorado, formato_escolhido)
    """
    manager = ContentFormatManager()
    
    if force_format and force_format in manager.formats:
        chosen_format = force_format
    elif content:
        analysis = manager.get_content_analysis(content)
        chosen_format = analysis["suggested_format"]
    else:
        chosen_format = manager.get_random_format()
    
    # Identificar tema do conteúdo para CTA contextualizado
    content_theme = None
    if content or original_text:
        text_to_analyze = original_text or content
        content_theme = manager.cta_manager._identify_theme_from_text(text_to_analyze)
    
    format_prompt = manager.get_format_prompt(chosen_format, content_theme, original_text)
    enhanced_prompt = base_prompt + "\n\n" + format_prompt
    
    return enhanced_prompt, chosen_format