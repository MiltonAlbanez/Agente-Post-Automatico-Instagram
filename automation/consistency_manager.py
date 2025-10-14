"""
Gerenciador de Consistência para Posts do Instagram
Mantém qualidade e padrões consistentes na criação de conteúdo
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib

class ConsistencyManager:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.consistency_file = Path(__file__).parent / "consistency_data.json"
        self.quality_standards_file = Path(__file__).parent / "quality_standards.json"
        
        self.logger = logging.getLogger(__name__)
        self.load_consistency_data()
        self.load_quality_standards()
        
    def load_consistency_data(self):
        """Carregar dados de consistência"""
        if self.consistency_file.exists():
            with open(self.consistency_file, 'r', encoding='utf-8') as f:
                self.consistency_data = json.load(f)
        else:
            self.consistency_data = {
                "post_history": [],
                "style_usage": {},
                "concept_frequency": {},
                "quality_scores": [],
                "last_update": None
            }
            
    def load_quality_standards(self):
        """Carregar padrões de qualidade"""
        default_standards = {
            "visual_quality": {
                "min_resolution": [1080, 1080],
                "aspect_ratios": ["1:1", "4:5", "9:16"],
                "color_harmony": True,
                "composition_rules": ["rule_of_thirds", "golden_ratio"]
            },
            "content_quality": {
                "min_caption_length": 50,
                "max_caption_length": 2200,
                "hashtag_count": {"min": 5, "max": 30},
                "emoji_usage": "moderate",
                "call_to_action": True
            },
            "consistency_rules": {
                "brand_voice": "friendly_professional",
                "posting_frequency": "3_per_day",
                "style_variation": 0.7,
                "concept_repetition_limit": 7
            },
            "engagement_targets": {
                "min_likes_rate": 0.03,
                "min_comments_rate": 0.005,
                "min_saves_rate": 0.01,
                "growth_rate_target": 0.02
            }
        }
        
        if self.quality_standards_file.exists():
            with open(self.quality_standards_file, 'r', encoding='utf-8') as f:
                self.quality_standards = json.load(f)
        else:
            self.quality_standards = default_standards
            self.save_quality_standards()
            
    def save_consistency_data(self):
        """Salvar dados de consistência"""
        self.consistency_data["last_update"] = datetime.now().isoformat()
        with open(self.consistency_file, 'w', encoding='utf-8') as f:
            json.dump(self.consistency_data, f, indent=2, ensure_ascii=False)
            
    def save_quality_standards(self):
        """Salvar padrões de qualidade"""
        with open(self.quality_standards_file, 'w', encoding='utf-8') as f:
            json.dump(self.quality_standards, f, indent=2, ensure_ascii=False)
            
    def validate_post_quality(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validar qualidade do post"""
        validation_result = {
            "is_valid": True,
            "score": 0.0,
            "issues": [],
            "suggestions": []
        }
        
        # Validar conteúdo textual
        content_score = self._validate_content_quality(post_data, validation_result)
        
        # Validar consistência visual
        visual_score = self._validate_visual_consistency(post_data, validation_result)
        
        # Validar consistência de marca
        brand_score = self._validate_brand_consistency(post_data, validation_result)
        
        # Calcular score final
        validation_result["score"] = (content_score + visual_score + brand_score) / 3
        validation_result["is_valid"] = validation_result["score"] >= 0.7
        
        return validation_result
        
    def _validate_content_quality(self, post_data: Dict[str, Any], result: Dict[str, Any]) -> float:
        """Validar qualidade do conteúdo"""
        score = 1.0
        caption = post_data.get("caption", "")
        
        # Verificar comprimento da legenda
        min_length = self.quality_standards["content_quality"]["min_caption_length"]
        max_length = self.quality_standards["content_quality"]["max_caption_length"]
        
        if len(caption) < min_length:
            score -= 0.2
            result["issues"].append(f"Legenda muito curta (mínimo: {min_length} caracteres)")
            result["suggestions"].append("Adicionar mais contexto ou storytelling à legenda")
            
        if len(caption) > max_length:
            score -= 0.1
            result["issues"].append(f"Legenda muito longa (máximo: {max_length} caracteres)")
            
        # Verificar hashtags
        hashtags = post_data.get("hashtags", [])
        hashtag_limits = self.quality_standards["content_quality"]["hashtag_count"]
        
        if len(hashtags) < hashtag_limits["min"]:
            score -= 0.15
            result["issues"].append(f"Poucas hashtags (mínimo: {hashtag_limits['min']})")
            
        if len(hashtags) > hashtag_limits["max"]:
            score -= 0.1
            result["issues"].append(f"Muitas hashtags (máximo: {hashtag_limits['max']})")
            
        return max(0.0, score)
        
    def _validate_visual_consistency(self, post_data: Dict[str, Any], result: Dict[str, Any]) -> float:
        """Validar consistência visual"""
        score = 1.0
        
        # Verificar estilo visual
        visual_style = post_data.get("visual_style", {})
        
        if not visual_style:
            score -= 0.3
            result["issues"].append("Estilo visual não definido")
            result["suggestions"].append("Definir estilo visual consistente")
            
        # Verificar paleta de cores
        if not visual_style.get("color_palette"):
            score -= 0.2
            result["issues"].append("Paleta de cores não definida")
            
        return max(0.0, score)
        
    def _validate_brand_consistency(self, post_data: Dict[str, Any], result: Dict[str, Any]) -> float:
        """Validar consistência de marca"""
        score = 1.0
        
        # Verificar tom de voz
        expected_voice = self.quality_standards["consistency_rules"]["brand_voice"]
        post_voice = post_data.get("brand_voice", "")
        
        if post_voice != expected_voice:
            score -= 0.2
            result["suggestions"].append(f"Ajustar tom de voz para: {expected_voice}")
            
        # Verificar call-to-action
        if self.quality_standards["content_quality"]["call_to_action"]:
            caption = post_data.get("caption", "")
            cta_keywords = ["comente", "compartilhe", "salve", "marque", "siga", "clique", "acesse"]
            
            if not any(keyword in caption.lower() for keyword in cta_keywords):
                score -= 0.15
                result["suggestions"].append("Adicionar call-to-action à legenda")
                
        return max(0.0, score)
        
    def check_repetition_patterns(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verificar padrões de repetição"""
        result = {
            "has_repetition": False,
            "repetition_type": None,
            "last_similar_post": None,
            "days_since_similar": 0
        }
        
        # Gerar hash do conteúdo
        content_hash = self._generate_content_hash(post_data)
        
        # Verificar histórico
        repetition_limit = self.quality_standards["consistency_rules"]["concept_repetition_limit"]
        
        for historical_post in self.consistency_data["post_history"][-50:]:  # Últimos 50 posts
            if historical_post.get("content_hash") == content_hash:
                post_date = datetime.fromisoformat(historical_post["created_at"])
                days_diff = (datetime.now() - post_date).days
                
                if days_diff < repetition_limit:
                    result["has_repetition"] = True
                    result["repetition_type"] = "exact_content"
                    result["last_similar_post"] = historical_post
                    result["days_since_similar"] = days_diff
                    break
                    
        return result
        
    def _generate_content_hash(self, post_data: Dict[str, Any]) -> str:
        """Gerar hash do conteúdo para detectar repetições"""
        content_string = f"{post_data.get('title', '')}{post_data.get('caption', '')}{post_data.get('visual_concept', '')}"
        return hashlib.md5(content_string.encode()).hexdigest()
        
    def register_post(self, post_data: Dict[str, Any], quality_score: float):
        """Registrar post no histórico de consistência"""
        post_record = {
            "id": post_data.get("id", f"post_{datetime.now().timestamp()}"),
            "created_at": datetime.now().isoformat(),
            "content_hash": self._generate_content_hash(post_data),
            "visual_style": post_data.get("visual_style", {}),
            "concept": post_data.get("visual_concept", ""),
            "quality_score": quality_score,
            "engagement_data": None  # Será preenchido posteriormente
        }
        
        self.consistency_data["post_history"].append(post_record)
        
        # Manter apenas últimos 100 posts
        if len(self.consistency_data["post_history"]) > 100:
            self.consistency_data["post_history"] = self.consistency_data["post_history"][-100:]
            
        # Atualizar estatísticas
        self._update_usage_statistics(post_data)
        self.consistency_data["quality_scores"].append(quality_score)
        
        self.save_consistency_data()
        
    def _update_usage_statistics(self, post_data: Dict[str, Any]):
        """Atualizar estatísticas de uso"""
        # Atualizar frequência de conceitos
        concept = post_data.get("visual_concept", "unknown")
        if concept in self.consistency_data["concept_frequency"]:
            self.consistency_data["concept_frequency"][concept] += 1
        else:
            self.consistency_data["concept_frequency"][concept] = 1
            
        # Atualizar uso de estilos
        style = post_data.get("visual_style", {}).get("name", "unknown")
        if style in self.consistency_data["style_usage"]:
            self.consistency_data["style_usage"][style] += 1
        else:
            self.consistency_data["style_usage"][style] = 1
            
    def get_consistency_report(self) -> Dict[str, Any]:
        """Gerar relatório de consistência"""
        recent_posts = self.consistency_data["post_history"][-30:]  # Últimos 30 posts
        
        if not recent_posts:
            return {"error": "Não há dados suficientes para gerar relatório"}
            
        # Calcular métricas
        avg_quality = sum(post["quality_score"] for post in recent_posts) / len(recent_posts)
        
        # Analisar diversidade de conceitos
        recent_concepts = [post["concept"] for post in recent_posts]
        concept_diversity = len(set(recent_concepts)) / len(recent_concepts) if recent_concepts else 0
        
        # Analisar frequência de postagem
        if len(recent_posts) >= 2:
            dates = [datetime.fromisoformat(post["created_at"]) for post in recent_posts]
            dates.sort()
            intervals = [(dates[i+1] - dates[i]).total_seconds() / 3600 for i in range(len(dates)-1)]
            avg_interval = sum(intervals) / len(intervals) if intervals else 0
        else:
            avg_interval = 0
            
        return {
            "period": "últimos_30_posts",
            "total_posts": len(recent_posts),
            "average_quality_score": round(avg_quality, 2),
            "concept_diversity": round(concept_diversity, 2),
            "average_posting_interval_hours": round(avg_interval, 1),
            "most_used_concepts": self._get_top_concepts(recent_concepts),
            "quality_trend": self._calculate_quality_trend(recent_posts),
            "recommendations": self._generate_recommendations(avg_quality, concept_diversity)
        }
        
    def _get_top_concepts(self, concepts: List[str]) -> List[Dict[str, Any]]:
        """Obter conceitos mais utilizados"""
        concept_count = {}
        for concept in concepts:
            concept_count[concept] = concept_count.get(concept, 0) + 1
            
        sorted_concepts = sorted(concept_count.items(), key=lambda x: x[1], reverse=True)
        return [{"concept": concept, "count": count} for concept, count in sorted_concepts[:5]]
        
    def _calculate_quality_trend(self, recent_posts: List[Dict[str, Any]]) -> str:
        """Calcular tendência de qualidade"""
        if len(recent_posts) < 5:
            return "dados_insuficientes"
            
        first_half = recent_posts[:len(recent_posts)//2]
        second_half = recent_posts[len(recent_posts)//2:]
        
        avg_first = sum(post["quality_score"] for post in first_half) / len(first_half)
        avg_second = sum(post["quality_score"] for post in second_half) / len(second_half)
        
        if avg_second > avg_first + 0.05:
            return "melhorando"
        elif avg_second < avg_first - 0.05:
            return "declinando"
        else:
            return "estável"
            
    def _generate_recommendations(self, avg_quality: float, concept_diversity: float) -> List[str]:
        """Gerar recomendações baseadas nas métricas"""
        recommendations = []
        
        if avg_quality < 0.7:
            recommendations.append("Focar na melhoria da qualidade geral dos posts")
            
        if concept_diversity < 0.5:
            recommendations.append("Aumentar a diversidade de conceitos visuais")
            
        if avg_quality > 0.9:
            recommendations.append("Excelente qualidade! Manter o padrão atual")
            
        if concept_diversity > 0.8:
            recommendations.append("Boa diversidade de conceitos, continuar variando")
            
        return recommendations

if __name__ == "__main__":
    manager = ConsistencyManager()
    report = manager.get_consistency_report()
    print(json.dumps(report, indent=2, ensure_ascii=False))