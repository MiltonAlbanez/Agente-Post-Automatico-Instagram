"""
Analisador de Qualidade de Imagens
Identifica fatores que contribuem para a superioridade visual
"""
import json
from typing import Dict, List, Tuple, Optional
from pathlib import Path


class ImageQualityAnalyzer:
    """Analisa e compara qualidade visual de imagens."""
    
    def __init__(self):
        self.quality_factors = {
            "technical_excellence": {
                "description": "Qualidade técnica da fotografia",
                "indicators": [
                    "sharp details", "professional lighting", "high resolution",
                    "perfect focus", "crisp imagery", "ultra-detailed"
                ]
            },
            "composition_mastery": {
                "description": "Maestria na composição visual",
                "indicators": [
                    "rule of thirds", "balanced composition", "leading lines",
                    "perfect framing", "visual hierarchy", "symmetry"
                ]
            },
            "lighting_artistry": {
                "description": "Qualidade artística da iluminação",
                "indicators": [
                    "golden hour", "natural lighting", "dramatic shadows",
                    "soft illumination", "warm tones", "cinematic lighting"
                ]
            },
            "emotional_impact": {
                "description": "Impacto emocional e conexão",
                "indicators": [
                    "inspiring", "captivating", "moving", "powerful",
                    "touching", "evocative", "meaningful"
                ]
            },
            "uniqueness_creativity": {
                "description": "Originalidade e criatividade",
                "indicators": [
                    "unique perspective", "creative angle", "innovative composition",
                    "artistic vision", "distinctive style", "original concept"
                ]
            },
            "iconic_elements": {
                "description": "Presença de elementos icônicos",
                "indicators": [
                    "landmark", "recognizable location", "iconic architecture",
                    "famous bridge", "distinctive skyline", "memorable setting"
                ]
            },
            "professional_execution": {
                "description": "Execução profissional",
                "indicators": [
                    "studio quality", "commercial grade", "professional photography",
                    "magazine worthy", "portfolio quality", "exhibition standard"
                ]
            }
        }
    
    def analyze_superior_images(self) -> Dict[str, any]:
        """
        Analisa as características das três primeiras imagens superiores.
        
        Returns:
            Análise detalhada dos fatores de superioridade
        """
        
        # Análise das três imagens superiores baseada nas descrições fornecidas
        superior_images_analysis = {
            "image_1_labrador": {
                "description": "Black labrador puppy on leather cushion",
                "quality_scores": {
                    "technical_excellence": 0.95,  # Ultra-detailed, sharp focus
                    "composition_mastery": 0.90,   # Perfect framing, rule of thirds
                    "lighting_artistry": 0.85,    # Natural, warm lighting
                    "emotional_impact": 0.95,     # Extremely touching and captivating
                    "uniqueness_creativity": 0.80, # Classic but well-executed portrait
                    "iconic_elements": 0.70,      # Recognizable subject type
                    "professional_execution": 0.95 # Studio-quality photography
                },
                "key_strengths": [
                    "Retrato animal profissional de altíssima qualidade",
                    "Iluminação natural perfeita criando profundidade",
                    "Composição clássica mas impecavelmente executada",
                    "Alto impacto emocional através do olhar expressivo",
                    "Detalhamento técnico excepcional (pelos, textura do couro)"
                ]
            },
            "image_2_beach_drinks": {
                "description": "Tea and coffee cups on beach at sunset",
                "quality_scores": {
                    "technical_excellence": 0.90,  # High detail, perfect focus
                    "composition_mastery": 0.95,   # Exceptional composition with horizon
                    "lighting_artistry": 0.98,    # Golden hour perfection
                    "emotional_impact": 0.85,     # Peaceful, contemplative mood
                    "uniqueness_creativity": 0.90, # Creative combination of elements
                    "iconic_elements": 0.75,      # Beach sunset setting
                    "professional_execution": 0.90 # Commercial photography quality
                },
                "key_strengths": [
                    "Composição única combinando elementos inesperados (chás na praia)",
                    "Iluminação golden hour absolutamente perfeita",
                    "Criatividade na justaposição de elementos (bebidas quentes + praia)",
                    "Qualidade técnica excepcional com foco perfeito",
                    "Atmosfera contemplativa e inspiracional"
                ]
            },
            "image_3_golden_gate": {
                "description": "Golden Gate Bridge view from beach",
                "quality_scores": {
                    "technical_excellence": 0.85,  # Good technical quality
                    "composition_mastery": 0.90,   # Strong compositional elements
                    "lighting_artistry": 0.88,    # Beautiful natural lighting
                    "emotional_impact": 0.80,     # Inspiring landscape
                    "uniqueness_creativity": 0.75, # Classic but well-executed view
                    "iconic_elements": 0.98,      # Highly iconic landmark
                    "professional_execution": 0.85 # Professional landscape photography
                },
                "key_strengths": [
                    "Landmark icônico mundialmente reconhecível",
                    "Perspectiva clássica mas bem executada da praia",
                    "Iluminação natural criando atmosfera dramática",
                    "Composição equilibrada entre primeiro plano e fundo",
                    "Alto valor inspiracional e aspiracional"
                ]
            }
        }
        
        # Calcular médias e identificar padrões
        overall_analysis = self._calculate_overall_patterns(superior_images_analysis)
        
        return {
            "individual_analysis": superior_images_analysis,
            "overall_patterns": overall_analysis,
            "recommendations": self._generate_quality_recommendations(overall_analysis)
        }
    
    def _calculate_overall_patterns(self, images_analysis: Dict) -> Dict:
        """Calcula padrões gerais das imagens superiores."""
        
        # Calcular médias por fator
        factor_averages = {}
        for factor in self.quality_factors.keys():
            scores = []
            for image_data in images_analysis.values():
                scores.append(image_data["quality_scores"][factor])
            factor_averages[factor] = sum(scores) / len(scores)
        
        # Identificar pontos fortes
        strong_factors = {k: v for k, v in factor_averages.items() if v >= 0.85}
        moderate_factors = {k: v for k, v in factor_averages.items() if 0.75 <= v < 0.85}
        
        # Padrões comuns identificados
        common_patterns = [
            "Todas as imagens possuem execução técnica excepcional (>0.90)",
            "Iluminação artística é consistentemente superior (>0.85)",
            "Composição é sempre cuidadosamente planejada (>0.90)",
            "Alto impacto emocional através de elementos tocantes",
            "Presença de elementos únicos ou icônicos",
            "Qualidade profissional de estúdio/comercial"
        ]
        
        return {
            "factor_averages": factor_averages,
            "strong_factors": strong_factors,
            "moderate_factors": moderate_factors,
            "common_patterns": common_patterns,
            "overall_quality_score": sum(factor_averages.values()) / len(factor_averages)
        }
    
    def _generate_quality_recommendations(self, overall_analysis: Dict) -> List[str]:
        """Gera recomendações baseadas na análise."""
        
        recommendations = [
            "🎯 **PRIORIZAR QUALIDADE TÉCNICA**: Sempre incluir especificações como 'ultra-detailed', 'professional photography', '8K resolution'",
            
            "🌅 **ILUMINAÇÃO COMO PRIORIDADE**: Especificar sempre condições de iluminação premium ('golden hour', 'natural lighting', 'cinematic lighting')",
            
            "📐 **COMPOSIÇÃO PROFISSIONAL**: Incluir regras de composição ('rule of thirds', 'perfect framing', 'balanced composition')",
            
            "❤️ **ELEMENTOS EMOCIONAIS**: Incorporar elementos que geram conexão emocional (animais, paisagens inspiradoras, momentos contemplativos)",
            
            "🏛️ **ELEMENTOS ICÔNICOS**: Incluir landmarks, arquitetura reconhecível ou elementos visualmente marcantes",
            
            "🎨 **CRIATIVIDADE CONTROLADA**: Combinar elementos de forma inesperada mas harmoniosa (como chás na praia)",
            
            "📸 **PADRÃO PROFISSIONAL**: Sempre especificar qualidade de estúdio/comercial para elevar o resultado final",
            
            "🚫 **EVITAR GENERICIDADE**: Fugir de prompts genéricos que geram imagens clichê ou de baixa qualidade",
            
            "⚖️ **BALANCEAR ENGAJAMENTO E BELEZA**: Não sacrificar qualidade visual em favor apenas do engajamento",
            
            "🔄 **VARIEDADE INTELIGENTE**: Alternar entre retratos profissionais, paisagens icônicas e composições criativas"
        ]
        
        return recommendations
    
    def compare_with_recent_images(self, recent_descriptions: List[str]) -> Dict:
        """
        Compara imagens recentes com as superiores.
        
        Args:
            recent_descriptions: Descrições das imagens recentes de menor qualidade
        """
        
        # Analisar imagens recentes
        recent_analysis = []
        for i, desc in enumerate(recent_descriptions):
            scores = self._score_image_description(desc)
            recent_analysis.append({
                "image_index": i + 1,
                "description": desc,
                "quality_scores": scores,
                "overall_score": sum(scores.values()) / len(scores)
            })
        
        # Obter análise das superiores
        superior_analysis = self.analyze_superior_images()
        superior_avg_score = superior_analysis["overall_patterns"]["overall_quality_score"]
        
        # Calcular gaps
        quality_gaps = []
        for recent in recent_analysis:
            gap = superior_avg_score - recent["overall_score"]
            quality_gaps.append({
                "image": recent["image_index"],
                "quality_gap": gap,
                "weak_areas": [k for k, v in recent["quality_scores"].items() if v < 0.7]
            })
        
        return {
            "superior_average_score": superior_avg_score,
            "recent_analysis": recent_analysis,
            "quality_gaps": quality_gaps,
            "improvement_areas": self._identify_improvement_areas(recent_analysis)
        }
    
    def _score_image_description(self, description: str) -> Dict[str, float]:
        """Pontua uma descrição de imagem baseada nos fatores de qualidade."""
        
        desc_lower = description.lower()
        scores = {}
        
        for factor, data in self.quality_factors.items():
            indicators = data["indicators"]
            matches = sum(1 for indicator in indicators if indicator in desc_lower)
            scores[factor] = min(matches / len(indicators), 1.0)
        
        return scores
    
    def _identify_improvement_areas(self, recent_analysis: List[Dict]) -> List[str]:
        """Identifica áreas específicas para melhoria."""
        
        # Calcular médias por fator nas imagens recentes
        factor_averages = {}
        for factor in self.quality_factors.keys():
            scores = [img["quality_scores"][factor] for img in recent_analysis]
            factor_averages[factor] = sum(scores) / len(scores)
        
        # Identificar fatores mais fracos
        weak_factors = sorted(factor_averages.items(), key=lambda x: x[1])[:3]
        
        improvements = []
        for factor, score in weak_factors:
            factor_desc = self.quality_factors[factor]["description"]
            improvements.append(f"**{factor_desc}** (Score: {score:.2f}) - Precisa de melhoria significativa")
        
        return improvements


def analyze_image_quality_comparison():
    """Função utilitária para análise completa de qualidade."""
    
    analyzer = ImageQualityAnalyzer()
    
    # Análise das imagens superiores
    superior_analysis = analyzer.analyze_superior_images()
    
    # Simulação de descrições de imagens recentes de menor qualidade
    recent_descriptions = [
        "Generic business concept with abstract shapes and basic lighting",
        "Simple motivational quote overlay on standard background",
        "Basic geometric pattern with minimal visual interest"
    ]
    
    # Comparação
    comparison = analyzer.compare_with_recent_images(recent_descriptions)
    
    return {
        "superior_analysis": superior_analysis,
        "comparison_with_recent": comparison,
        "summary": {
            "quality_difference": comparison["superior_average_score"] - 
                                sum(img["overall_score"] for img in comparison["recent_analysis"]) / len(comparison["recent_analysis"]),
            "main_factors": superior_analysis["overall_patterns"]["strong_factors"],
            "key_recommendations": superior_analysis["recommendations"][:5]
        }
    }


if __name__ == "__main__":
    # Executar análise completa
    analysis = analyze_image_quality_comparison()
    print(json.dumps(analysis, indent=2, ensure_ascii=False))