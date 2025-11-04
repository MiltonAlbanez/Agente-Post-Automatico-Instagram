"""
Sistema de Gerenciamento de Temas Semanais
Implementa o plano de postagem semanal temático com cunho espiritual
"""
import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class WeeklyThemeManager:
    """Gerencia os temas semanais e slots de horário para postagens."""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            # Determinar o caminho correto baseado na localização do arquivo atual
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent
            config_path = project_root / "config" / "weekly_thematic_config.json"
        
        self.config_path = Path(config_path)
        self.weekly_config = self._load_weekly_config()
        
    def _load_weekly_config(self) -> Dict:
        """Carrega a configuração semanal temática."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config.get("weekly_thematic_system", {})
        except Exception as e:
            print(f"Erro ao carregar configuração semanal: {e}")
            return {}
    
    def get_current_day_theme(self, day_of_week: int = None) -> Dict:
        """
        Obtém o tema do dia atual.
        
        Args:
            day_of_week: Dia da semana (1=Segunda, 7=Domingo). Se None, usa o dia atual.
            
        Returns:
            Configuração completa do dia
        """
        if day_of_week is None:
            day_of_week = datetime.now().isoweekday()
        
        day_config = self.weekly_config.get("daily_themes", {}).get(str(day_of_week), {})
        
        if not day_config:
            print(f"Configuração não encontrada para o dia {day_of_week}")
            return self._get_fallback_config()
        
        return day_config
    
    def get_time_slot_config(self, day_of_week: int = None, time_slot: str = "morning") -> Dict:
        """
        Obtém a configuração específica de um slot de tempo.
        
        Args:
            day_of_week: Dia da semana (1=Segunda, 7=Domingo)
            time_slot: "morning", "midday", ou "evening"
            
        Returns:
            Configuração do slot específico
        """
        day_config = self.get_current_day_theme(day_of_week)
        slot_config = day_config.get(time_slot, {})
        
        # Adicionar informações do dia ao slot
        slot_config["day_name"] = day_config.get("day_name", "")
        slot_config["main_theme"] = day_config.get("main_theme", "")
        slot_config["objective"] = day_config.get("objective", "")
        slot_config["is_special_day"] = day_config.get("special_day", False)
        
        return slot_config
    
    def determine_current_time_slot(self) -> str:
        """
        Determina o slot de tempo atual baseado no horário.
        
        Returns:
            "morning", "midday", ou "evening"
        """
        current_hour = datetime.now().hour
        
        # Baseado nos horários do sistema:
        # Feed: 06:00, 12:00, 19:00 UTC
        # Stories: 09:00, 15:00, 21:00 UTC
        
        if 6 <= current_hour < 12:
            return "morning"
        elif 12 <= current_hour < 18:
            return "midday"
        else:
            return "evening"
    
    def get_current_slot_config(self) -> Dict:
        """Obtém a configuração do slot atual baseado no dia e horário."""
        current_day = datetime.now().isoweekday()
        current_slot = self.determine_current_time_slot()
        
        return self.get_time_slot_config(current_day, current_slot)
    
    def generate_content_prompt(self, day_of_week: int = None, time_slot: str = None, 
                              custom_theme: str = None) -> Tuple[str, Dict]:
        """
        Gera prompt de conteúdo baseado no tema semanal.
        
        Args:
            day_of_week: Dia da semana específico
            time_slot: Slot de tempo específico
            custom_theme: Tema personalizado (opcional)
            
        Returns:
            Tuple com (prompt_de_conteudo, metadados)
        """
        if time_slot is None:
            time_slot = self.determine_current_time_slot()
        
        slot_config = self.get_time_slot_config(day_of_week, time_slot)
        
        if not slot_config:
            return self._generate_fallback_prompt(custom_theme)
        
        # Construir prompt baseado na configuração
        base_prompt = slot_config.get("prompt_focus", "")
        content_type = slot_config.get("content_type", "")
        main_theme = slot_config.get("main_theme", "")
        
        # Adicionar contexto espiritual se for manhã
        spiritual_context = ""
        if slot_config.get("spiritual_focus", False):
            spiritual_context = " IMPORTANTE: Este conteúdo DEVE ter cunho espiritual obrigatório, conectando fé, propósito divino e desenvolvimento pessoal."
        
        # Construir prompt final
        content_prompt = f"""
TEMA DO DIA: {main_theme}
TIPO DE CONTEÚDO: {content_type}
SLOT: {slot_config.get('slot_name', time_slot)}

INSTRUÇÃO ESPECÍFICA: {base_prompt}

{spiritual_context}

DIRETRIZES GERAIS:
- Tom: Inspirador, Autoridade, Cristão-orientado
- Foco: Desenvolvimento Pessoal e PNL
- CTA Sugerido: {slot_config.get('cta_suggestion', 'Interaja nos comentários')}
- Integrar conceitos de PNL de forma natural
- Manter coerência com o tema do dia
"""
        
        metadata = {
            "day_name": slot_config.get("day_name", ""),
            "main_theme": main_theme,
            "time_slot": time_slot,
            "content_type": content_type,
            "spiritual_focus": slot_config.get("spiritual_focus", False),
            "is_special_day": slot_config.get("is_special_day", False),
            "cta_suggestion": slot_config.get("cta_suggestion", ""),
            "style": slot_config.get("style", "")
        }
        
        return content_prompt, metadata
    
    def generate_image_prompt(self, day_of_week: int = None, time_slot: str = None) -> Tuple[str, Dict]:
        """
        Gera prompt de imagem baseado no estilo visual do tema.
        
        Returns:
            Tuple com (prompt_de_imagem, metadados_visuais)
        """
        if time_slot is None:
            time_slot = self.determine_current_time_slot()
        
        slot_config = self.get_time_slot_config(day_of_week, time_slot)
        
        if not slot_config:
            return self._generate_fallback_image_prompt()
        
        # Obter estilo visual específico
        visual_style = slot_config.get("style", "professional, clean, inspiring")
        main_theme = slot_config.get("main_theme", "")
        content_type = slot_config.get("content_type", "")
        
        # Construir prompt de imagem
        image_prompt = f"""
Professional photography with {visual_style} aesthetic. 
Theme: {main_theme} - {content_type}.
Visual metaphor for personal development and spiritual growth.
High quality, cinematic lighting, inspiring composition.
"""
        
        # Adicionar elementos específicos baseados no slot
        if time_slot == "morning":
            image_prompt += " Morning light, sunrise elements, sense of new beginning and hope."
        elif time_slot == "midday":
            image_prompt += " Clear, focused lighting, action-oriented elements, productivity theme."
        else:  # evening
            image_prompt += " Warm, contemplative lighting, reflective mood, depth and wisdom."
        
        # Adicionar elementos especiais para sábado
        if slot_config.get("is_special_day", False):
            image_prompt += " Peaceful, restorative elements, connection with nature and spirituality."
        
        metadata = {
            "visual_style": visual_style,
            "time_slot": time_slot,
            "theme_integration": True,
            "spiritual_elements": slot_config.get("spiritual_focus", False)
        }
        
        return image_prompt, metadata
    
    def get_hashtag_suggestions(self, day_of_week: int = None, time_slot: str = None) -> List[str]:
        """Obtém sugestões de hashtags baseadas no tema do dia."""
        slot_config = self.get_time_slot_config(day_of_week, time_slot)
        hashtag_config = self.weekly_config.get("hashtag_suggestions", {})
        
        suggested_hashtags = []
        
        # Hashtags sempre presentes
        suggested_hashtags.extend(hashtag_config.get("coaching", []))
        
        # Hashtags baseadas no slot
        if slot_config.get("spiritual_focus", False):
            suggested_hashtags.extend(hashtag_config.get("spiritual", []))
        
        # Hashtags baseadas no tema do dia
        main_theme = slot_config.get("main_theme", "").lower()
        if "empreendedorismo" in main_theme or "vendas" in main_theme:
            suggested_hashtags.extend(hashtag_config.get("business", []))
        elif slot_config.get("is_special_day", False):
            suggested_hashtags.extend(hashtag_config.get("weekend", []))
        
        # Remover duplicatas e limitar quantidade
        return list(set(suggested_hashtags))[:10]
    
    def _get_fallback_config(self) -> Dict:
        """Configuração de fallback caso não encontre o dia específico."""
        return {
            "day_name": "Dia Genérico",
            "main_theme": "Desenvolvimento Pessoal",
            "objective": "Inspirar crescimento e transformação",
            "morning": {
                "spiritual_focus": True,
                "style": "clean, inspiring, natural light",
                "prompt_focus": "Crie uma mensagem inspiradora que conecte fé e desenvolvimento pessoal.",
                "content_type": "Motivação espiritual",
                "cta_suggestion": "Reflita e compartilhe"
            }
        }
    
    def _generate_fallback_prompt(self, custom_theme: str = None) -> Tuple[str, Dict]:
        """Gera prompt de fallback."""
        theme = custom_theme or "desenvolvimento pessoal e crescimento espiritual"
        
        prompt = f"""
TEMA: {theme}
INSTRUÇÃO: Crie conteúdo inspirador focado em desenvolvimento pessoal com tom cristão-orientado.
Integre conceitos de PNL e coaching de forma natural.
"""
        
        metadata = {
            "fallback_mode": True,
            "theme": theme,
            "spiritual_focus": True
        }
        
        return prompt, metadata
    
    def _generate_fallback_image_prompt(self) -> Tuple[str, Dict]:
        """Gera prompt de imagem de fallback."""
        prompt = "Professional photography, inspiring and clean aesthetic, personal development theme, natural lighting, high quality composition."
        
        metadata = {
            "fallback_mode": True,
            "style": "professional_clean"
        }
        
        return prompt, metadata


# Função utilitária para integração fácil
def get_weekly_themed_content(day_of_week: int = None, time_slot: str = None, 
                            custom_theme: str = None) -> Tuple[str, str, Dict]:
    """
    Função utilitária para obter conteúdo temático semanal.
    
    Returns:
        Tuple com (prompt_conteudo, prompt_imagem, metadados_completos)
    """
    manager = WeeklyThemeManager()
    
    content_prompt, content_metadata = manager.generate_content_prompt(
        day_of_week, time_slot, custom_theme
    )
    
    image_prompt, image_metadata = manager.generate_image_prompt(
        day_of_week, time_slot
    )
    
    hashtags = manager.get_hashtag_suggestions(day_of_week, time_slot)
    
    # Combinar metadados
    combined_metadata = {
        **content_metadata,
        "image_style": image_metadata.get("visual_style", ""),
        "hashtag_suggestions": hashtags,
        "system_version": "weekly_thematic_v1.0"
    }
    
    return content_prompt, image_prompt, combined_metadata


# Função para verificar se é horário de postagem matinal (cunho espiritual obrigatório)
def is_morning_spiritual_time() -> bool:
    """Verifica se é horário de postagem matinal que requer cunho espiritual."""
    manager = WeeklyThemeManager()
    current_slot = manager.determine_current_time_slot()
    current_config = manager.get_current_slot_config()
    
    return current_slot == "morning" and current_config.get("spiritual_focus", False)