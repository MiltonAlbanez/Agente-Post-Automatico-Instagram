"""
Sistema de Gerenciamento de Qualidade Visual
Prioriza beleza e qualidade técnica além do engajamento
"""
import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class VisualQualityManager:
    """Gerencia a qualidade visual das imagens geradas."""
    
    def __init__(self, config_path: str = "config/enhanced_prompts.json"):
        self.config_path = Path(config_path)
        self.prompts_config = self._load_prompts_config()
        
    def _load_prompts_config(self) -> Dict:
        """Carrega configurações de prompts aprimorados."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar config de prompts: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Configuração padrão caso o arquivo não exista."""
        return {
            "high_quality_prompts": {
                "professional_photography": {
                    "templates": [
                        "Professional photography, ultra-detailed, 8K resolution, perfect composition"
                    ]
                }
            },
            "quality_enhancers": {
                "technical_specs": ["ultra-detailed", "professional photography"],
                "lighting_conditions": ["golden hour lighting", "natural lighting"],
                "composition_rules": ["rule of thirds", "perfect composition"]
            }
        }
    
    def generate_high_quality_prompt(self, 
                                   content_theme: str = "growth and leadership",
                                   style_preference: str = "professional",
                                   include_landmark: bool = False) -> str:
        """
        Gera prompt otimizado para qualidade visual superior.
        
        Args:
            content_theme: Tema do conteúdo (crescimento, liderança, etc.)
            style_preference: Estilo preferido (professional, artistic, minimalist)
            include_landmark: Se deve incluir landmark icônico
        """
        
        # Selecionar categoria base
        if include_landmark and random.random() < 0.3:  # 30% chance de landmark
            return self._generate_landmark_prompt(content_theme)
        elif random.random() < 0.2:  # 20% chance de composição única
            return self._generate_unique_composition_prompt(content_theme)
        elif random.random() < 0.15:  # 15% chance de retrato animal
            return self._generate_animal_portrait_prompt(content_theme)
        else:  # 35% composição profissional padrão
            return self._generate_professional_prompt(content_theme, style_preference)
    
    def _generate_landmark_prompt(self, theme: str) -> str:
        """Gera prompt com landmark icônico."""
        config = self.prompts_config["high_quality_prompts"]["iconic_locations"]
        template = random.choice(config["templates"])
        landmark = random.choice(config["landmarks"])
        time_of_day = random.choice(["golden hour", "blue hour", "sunrise", "sunset"])
        
        base_prompt = template.format(landmark=landmark, time_of_day=time_of_day)
        return self._enhance_prompt_quality(base_prompt, theme)
    
    def _generate_unique_composition_prompt(self, theme: str) -> str:
        """Gera prompt com composição única (como chás na praia)."""
        config = self.prompts_config["high_quality_prompts"]["unique_compositions"]
        template = random.choice(config["templates"])
        combination = random.choice(config["object_combinations"])
        
        # Extrair objetos e ambiente da combinação
        parts = combination.split(" in " if " in " else " on ")
        objects = parts[0]
        environment = parts[1] if len(parts) > 1 else "beautiful setting"
        
        base_prompt = template.format(
            objects=objects, 
            location=environment,
            environment=environment,
            backdrop=environment
        )
        return self._enhance_prompt_quality(base_prompt, theme)
    
    def _generate_animal_portrait_prompt(self, theme: str) -> str:
        """Gera prompt para retrato animal profissional."""
        config = self.prompts_config["high_quality_prompts"]["animal_portraits"]
        template = random.choice(config["templates"])
        
        animals = [
            "golden retriever", "black labrador", "siberian husky", 
            "maine coon cat", "bengal cat", "border collie",
            "german shepherd", "golden cat", "white persian cat"
        ]
        animal = random.choice(animals)
        
        base_prompt = template.format(animal=animal)
        return self._enhance_prompt_quality(base_prompt, theme)
    
    def _generate_professional_prompt(self, theme: str, style: str) -> str:
        """Gera prompt profissional baseado no tema."""
        config = self.prompts_config["high_quality_prompts"]["professional_photography"]
        template = random.choice(config["templates"])
        
        # Adaptar subject baseado no tema
        subjects = {
            "growth": "ascending staircase in modern architecture",
            "leadership": "mountain peak with winding path",
            "transformation": "butterfly emerging from cocoon",
            "success": "golden sunrise over city skyline",
            "innovation": "futuristic geometric patterns",
            "teamwork": "interconnected bridge structures"
        }
        
        subject = subjects.get(theme.split()[0].lower(), "inspirational landscape")
        base_prompt = template.format(subject=subject)
        
        return self._enhance_prompt_quality(base_prompt, theme)
    
    def _enhance_prompt_quality(self, base_prompt: str, theme: str) -> str:
        """Adiciona elementos de qualidade ao prompt."""
        enhancers = self.prompts_config["quality_enhancers"]
        
        # Adicionar especificações técnicas
        tech_specs = random.sample(enhancers["technical_specs"], 2)
        
        # Adicionar condições de iluminação
        lighting = random.choice(enhancers["lighting_conditions"])
        
        # Adicionar regras de composição
        composition = random.choice(enhancers["composition_rules"])
        
        # Construir prompt final
        enhanced_prompt = f"{base_prompt}, {lighting}, {composition}"
        enhanced_prompt += f", {', '.join(tech_specs)}"
        
        # Adicionar contexto temático
        enhanced_prompt += f". Metaphorically represents {theme} and personal development."
        
        # Adicionar instruções de qualidade
        enhanced_prompt += " Avoid cluttered elements, maintain clean composition, focus on visual impact."
        
        return enhanced_prompt
    
    def get_style_variation(self, base_style: str) -> str:
        """Retorna variação de estilo para diversidade visual."""
        variations = self.prompts_config.get("style_variations", {})
        
        style_map = {
            "minimalist": "minimalist_premium",
            "dynamic": "dynamic_professional", 
            "artistic": "artistic_cinematic"
        }
        
        variation_key = style_map.get(base_style, "dynamic_professional")
        return variations.get(variation_key, "Professional high-quality photography")
    
    def should_use_high_quality_mode(self, engagement_priority: float = 0.3) -> bool:
        """
        Determina se deve usar modo de alta qualidade.
        
        Args:
            engagement_priority: Prioridade do engajamento (0.0 = só qualidade, 1.0 = só engajamento)
        """
        # Priorizar qualidade visual sobre engajamento (reduzido de 0.7 para 0.3)
        quality_weight = 1.0 - engagement_priority
        return random.random() < quality_weight + 0.6  # Aumentado bias para qualidade de 0.3 para 0.6
    
    def analyze_image_quality_factors(self, image_description: str) -> Dict[str, float]:
        """
        Analisa fatores de qualidade na descrição da imagem.
        
        Returns:
            Dict com scores de diferentes aspectos de qualidade
        """
        description_lower = image_description.lower()
        
        quality_factors = {
            "technical_quality": 0.0,
            "composition": 0.0,
            "lighting": 0.0,
            "uniqueness": 0.0,
            "emotional_impact": 0.0
        }
        
        # Palavras-chave para cada fator
        technical_keywords = ["sharp", "detailed", "professional", "high-resolution", "crisp"]
        composition_keywords = ["balanced", "symmetrical", "rule of thirds", "framed", "perspective"]
        lighting_keywords = ["golden hour", "dramatic", "soft light", "natural light", "illuminated"]
        uniqueness_keywords = ["unique", "creative", "artistic", "innovative", "distinctive"]
        emotional_keywords = ["inspiring", "powerful", "moving", "captivating", "striking"]
        
        keyword_sets = {
            "technical_quality": technical_keywords,
            "composition": composition_keywords,
            "lighting": lighting_keywords,
            "uniqueness": uniqueness_keywords,
            "emotional_impact": emotional_keywords
        }
        
        for factor, keywords in keyword_sets.items():
            score = sum(1 for keyword in keywords if keyword in description_lower)
            quality_factors[factor] = min(score / len(keywords), 1.0)
        
        return quality_factors


# Função utilitária para integração
def get_enhanced_image_prompt(content_theme: str = "growth and leadership",
                            current_style: str = "dynamic",
                            force_high_quality: bool = True) -> Tuple[str, Dict]:
    """
    Função utilitária para obter prompt aprimorado.
    
    Returns:
        Tuple[prompt_aprimorado, metadados_qualidade]
    """
    manager = VisualQualityManager()
    
    # SEMPRE usar modo de alta qualidade (mudança: force_high_quality padrão = True)
    use_high_quality = force_high_quality or manager.should_use_high_quality_mode()
    
    if use_high_quality:
        # Usar sistema de alta qualidade
        prompt = manager.generate_high_quality_prompt(
            content_theme=content_theme,
            style_preference=current_style,
            include_landmark=True
        )
        metadata = {
            "quality_mode": "high",
            "style_applied": current_style,
            "enhancement_level": "maximum"
        }
    else:
        # Usar sistema padrão com melhorias
        style_variation = manager.get_style_variation(current_style)
        prompt = f"{style_variation}. Theme: {content_theme}. Professional photography, ultra-detailed."
        metadata = {
            "quality_mode": "standard_enhanced",
            "style_applied": current_style,
            "enhancement_level": "moderate"
        }
    
    return prompt, metadata