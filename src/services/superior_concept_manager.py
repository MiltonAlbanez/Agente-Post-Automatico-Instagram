"""
Sistema de Gerenciamento de Conceitos Superiores
Replica os conceitos das 3 imagens superiores mantendo qualidade e harmonia
"""
import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class SuperiorConceptManager:
    """Gerencia a aplicação dos conceitos visuais superiores."""
    
    def __init__(self, config_path: str = "config/superior_concepts.json"):
        self.config_path = Path(config_path)
        self.concepts_config = self._load_concepts_config()
        self.last_used_concept = None
        self.concept_usage_history = []
        
    def _load_concepts_config(self) -> Dict:
        """Carrega configurações dos conceitos superiores."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar config de conceitos superiores: {e}")
            return self._get_fallback_config()
    
    def _get_fallback_config(self) -> Dict:
        """Configuração de fallback caso o arquivo não exista."""
        return {
            "superior_visual_concepts": {
                "concept_categories": {
                    "professional_animal_portrait": {"weight": 0.25},
                    "unique_beach_composition": {"weight": 0.35},
                    "iconic_coastal_landscape": {"weight": 0.40}
                }
            }
        }
    
    def get_next_superior_concept(self, content_theme: str = None, force_concept: str = None) -> Tuple[str, Dict]:
        """
        Seleciona o próximo conceito superior baseado na rotação inteligente.
        
        Args:
            content_theme: Tema do conteúdo para adaptação sutil
            force_concept: Forçar um conceito específico (para testes)
        
        Returns:
            Tuple com (prompt_gerado, metadata_do_conceito)
        """
        concepts = self.concepts_config["superior_visual_concepts"]["concept_categories"]
        
        if force_concept and force_concept in concepts:
            selected_concept = force_concept
        else:
            selected_concept = self._select_concept_intelligently(concepts)
        
        # Gerar prompt baseado no conceito selecionado
        prompt, metadata = self._generate_concept_prompt(selected_concept, content_theme)
        
        # Registrar uso para rotação inteligente
        self._register_concept_usage(selected_concept)
        
        return prompt, metadata
    
    def _select_concept_intelligently(self, concepts: Dict) -> str:
        """Seleciona conceito baseado em pesos e histórico de uso."""
        # Evitar repetir o último conceito usado
        available_concepts = [name for name in concepts.keys() if name != self.last_used_concept]
        
        if not available_concepts:
            available_concepts = list(concepts.keys())
        
        # Aplicar pesos para seleção
        weights = [concepts[concept].get("weight", 0.33) for concept in available_concepts]
        
        # Ajustar pesos baseado no histórico recente (últimas 5 imagens)
        recent_history = self.concept_usage_history[-5:]
        for i, concept in enumerate(available_concepts):
            recent_usage = recent_history.count(concept)
            if recent_usage > 2:  # Se usado mais de 2 vezes nas últimas 5
                weights[i] *= 0.5  # Reduzir peso pela metade
        
        # Seleção ponderada
        selected_concept = random.choices(available_concepts, weights=weights)[0]
        return selected_concept
    
    def _generate_concept_prompt(self, concept_name: str, content_theme: str = None) -> Tuple[str, Dict]:
        """Gera prompt específico para o conceito selecionado."""
        concept_config = self.concepts_config["superior_visual_concepts"]["concept_categories"][concept_name]
        
        if concept_name == "professional_animal_portrait":
            return self._generate_animal_portrait_prompt(concept_config, content_theme)
        elif concept_name == "unique_beach_composition":
            return self._generate_beach_composition_prompt(concept_config, content_theme)
        elif concept_name == "iconic_coastal_landscape":
            return self._generate_coastal_landscape_prompt(concept_config, content_theme)
        else:
            # Fallback para conceito desconhecido
            return self._generate_fallback_prompt(content_theme)
    
    def _generate_animal_portrait_prompt(self, config: Dict, theme: str = None) -> Tuple[str, Dict]:
        """Gera prompt para retrato animal profissional."""
        animal = random.choice(config.get("animals", ["black labrador"]))
        base_prompt = config["prompt_template"].format(animal_type=animal)
        
        # Adaptação sutil ao tema do conteúdo
        if theme:
            theme_adaptations = {
                "crescimento": "representing growth and development",
                "liderança": "showing leadership and confidence", 
                "transformação": "symbolizing transformation and change",
                "sucesso": "embodying success and achievement",
                "inovação": "expressing innovation and creativity"
            }
            for keyword, adaptation in theme_adaptations.items():
                if keyword in theme.lower():
                    base_prompt += f", {adaptation}"
                    break
        
        metadata = {
            "concept_type": "professional_animal_portrait",
            "animal_selected": animal,
            "theme_integration": theme is not None,
            "quality_mode": "superior_concept"
        }
        
        return base_prompt, metadata
    
    def _generate_beach_composition_prompt(self, config: Dict, theme: str = None) -> Tuple[str, Dict]:
        """Gera prompt para composição única na praia."""
        objects = random.choice(config.get("object_sets", ["tea cups and saucer with steam"]))
        base_prompt = config["prompt_template"].format(objects=objects)
        
        # Adaptação temática através dos objetos
        if theme:
            theme_objects = {
                "crescimento": "growing plants and seeds",
                "liderança": "compass and leadership tools",
                "transformação": "butterfly chrysalis and transformation symbols",
                "sucesso": "golden trophy and achievement symbols",
                "inovação": "innovative gadgets and creative tools"
            }
            for keyword, themed_objects in theme_objects.items():
                if keyword in theme.lower():
                    objects = themed_objects
                    base_prompt = config["prompt_template"].format(objects=objects)
                    break
        
        metadata = {
            "concept_type": "unique_beach_composition",
            "objects_selected": objects,
            "theme_integration": theme is not None,
            "quality_mode": "superior_concept"
        }
        
        return base_prompt, metadata
    
    def _generate_coastal_landscape_prompt(self, config: Dict, theme: str = None) -> Tuple[str, Dict]:
        """Gera prompt para paisagem costeira icônica."""
        landmark = random.choice(config.get("landmarks", ["Golden Gate Bridge"]))
        time_of_day = random.choice(config.get("times_of_day", ["golden hour"]))
        
        base_prompt = config["prompt_template"].format(
            landmark=landmark,
            time_of_day=time_of_day
        )
        
        # Adaptação temática através da atmosfera
        if theme:
            theme_atmospheres = {
                "crescimento": "with upward perspective symbolizing growth",
                "liderança": "commanding and majestic view",
                "transformação": "during dramatic weather change",
                "sucesso": "bathed in triumphant golden light",
                "inovação": "with modern architectural elements"
            }
            for keyword, atmosphere in theme_atmospheres.items():
                if keyword in theme.lower():
                    base_prompt += f", {atmosphere}"
                    break
        
        metadata = {
            "concept_type": "iconic_coastal_landscape",
            "landmark_selected": landmark,
            "time_of_day": time_of_day,
            "theme_integration": theme is not None,
            "quality_mode": "superior_concept"
        }
        
        return base_prompt, metadata
    
    def _generate_fallback_prompt(self, theme: str = None) -> Tuple[str, Dict]:
        """Prompt de fallback caso conceito não seja reconhecido."""
        base_prompt = "Professional photography, ultra-detailed, perfect composition, cinematic lighting, award-winning quality"
        
        if theme:
            base_prompt += f", inspired by themes of {theme}"
        
        metadata = {
            "concept_type": "fallback",
            "theme_integration": theme is not None,
            "quality_mode": "fallback"
        }
        
        return base_prompt, metadata
    
    def _register_concept_usage(self, concept_name: str):
        """Registra o uso do conceito para rotação inteligente."""
        self.last_used_concept = concept_name
        self.concept_usage_history.append(concept_name)
        
        # Manter apenas os últimos 20 usos para eficiência
        if len(self.concept_usage_history) > 20:
            self.concept_usage_history = self.concept_usage_history[-20:]
    
    def get_concept_statistics(self) -> Dict:
        """Retorna estatísticas de uso dos conceitos."""
        if not self.concept_usage_history:
            return {"message": "Nenhum conceito usado ainda"}
        
        total_uses = len(self.concept_usage_history)
        concept_counts = {}
        
        for concept in self.concept_usage_history:
            concept_counts[concept] = concept_counts.get(concept, 0) + 1
        
        statistics = {
            "total_images_generated": total_uses,
            "last_concept_used": self.last_used_concept,
            "concept_distribution": {
                concept: {
                    "count": count,
                    "percentage": round((count / total_uses) * 100, 1)
                }
                for concept, count in concept_counts.items()
            }
        }
        
        return statistics
    
    def reset_usage_history(self):
        """Reseta o histórico de uso (útil para testes)."""
        self.concept_usage_history = []
        self.last_used_concept = None


def get_superior_concept_prompt(content_theme: str = None, 
                              force_concept: str = None) -> Tuple[str, Dict]:
    """
    Função utilitária para obter prompt baseado nos conceitos superiores.
    
    Args:
        content_theme: Tema do conteúdo para adaptação
        force_concept: Forçar conceito específico
    
    Returns:
        Tuple com (prompt, metadata)
    """
    manager = SuperiorConceptManager()
    return manager.get_next_superior_concept(content_theme, force_concept)