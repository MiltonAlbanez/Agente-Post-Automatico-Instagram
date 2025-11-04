"""
Sistema de CTAs (Call-to-Action) específicos para cada formato de post.
Gera chamadas para ação coerentes com o assunto e formato do conteúdo.
"""

import random
from typing import Dict, List


class CTAManager:
    """Gerencia CTAs específicos para diferentes formatos de post."""
    
    def __init__(self):
        self.ctas_by_format = {
            "standard": {
                "engagement": [
                    "💬 Qual sua experiência com isso? Conta nos comentários!",
                    "🤔 E você, como aplica isso no seu dia a dia?",
                    "👇 Deixa sua opinião aqui embaixo!",
                    "💭 O que você pensa sobre isso? Vamos conversar!",
                    "🗣️ Compartilha sua visão nos comentários!"
                ],
                "action": [
                    "🚀 Salva este post para aplicar depois!",
                    "📌 Salva para não esquecer e coloca em prática!",
                    "💾 Salva este conteúdo e compartilha com quem precisa!",
                    "⭐ Marca alguém que precisa ver isso!",
                    "🔄 Compartilha se achou útil!"
                ],
                "follow": [
                    "👥 Me segue para mais conteúdos como este!",
                    "🔔 Ativa as notificações para não perder nenhum post!",
                    "📱 Segue para receber dicas diárias de crescimento!",
                    "✨ Me acompanha para mais insights valiosos!",
                    "🎯 Segue para transformar sua mentalidade!"
                ]
            },
            
            "quote": {
                "reflection": [
                    "🤔 Como essa frase se aplica à sua jornada?",
                    "💭 Qual parte dessa reflexão mais te tocou?",
                    "🎯 Em que momento da sua vida isso faz mais sentido?",
                    "✨ Como você interpretaria essa mensagem?",
                    "🌟 Que insights essa frase desperta em você?"
                ],
                "sharing": [
                    "📤 Marca alguém que precisa ler isso hoje!",
                    "💌 Compartilha com quem está precisando dessa energia!",
                    "🤝 Marca aquela pessoa que vai se identificar!",
                    "💪 Envia para quem está enfrentando desafios!",
                    "🎁 Presenteia alguém com essa reflexão!"
                ],
                "personal": [
                    "📝 Conta como você vive isso na prática!",
                    "🗣️ Qual sua interpretação pessoal dessa frase?",
                    "💬 Como isso se conecta com sua experiência?",
                    "🎪 Compartilha um exemplo da sua vida!",
                    "🌱 Como isso te ajuda no seu crescimento?"
                ]
            },
            
            "tip": {
                "implementation": [
                    "🎯 Qual dessas dicas você vai testar primeiro?",
                    "💪 Escolhe uma e coloca em prática hoje mesmo!",
                    "📋 Salva e cria seu plano de ação!",
                    "⚡ Qual dica faz mais sentido para seu momento atual?",
                    "🚀 Implementa uma por semana e vê os resultados!"
                ],
                "results": [
                    "📊 Volta aqui para contar os resultados!",
                    "💬 Testa e compartilha como foi a experiência!",
                    "🎉 Aplica e celebra suas conquistas nos comentários!",
                    "📈 Conta depois como essas dicas impactaram sua rotina!",
                    "✅ Marca quando conseguir aplicar todas!"
                ],
                "community": [
                    "🤝 Adiciona suas próprias dicas nos comentários!",
                    "💡 Tem alguma dica extra? Compartilha com a galera!",
                    "🔄 Marca alguém que também precisa dessas dicas!",
                    "👥 Vamos criar uma corrente de dicas úteis!",
                    "🌟 Qual dica funcionou melhor para você?"
                ]
            },
            
            "question": {
                "direct_answer": [
                    "💬 Responde aí: qual sua opinião sincera?",
                    "🗣️ Conta sua experiência nos comentários!",
                    "💭 E aí, o que você pensa sobre isso?",
                    "🤔 Qual sua resposta para essa pergunta?",
                    "👇 Deixa sua resposta aqui embaixo!"
                ],
                "story_sharing": [
                    "📖 Compartilha sua história relacionada a isso!",
                    "🎭 Conta um exemplo da sua vida!",
                    "💫 Qual sua experiência com essa situação?",
                    "🌟 Tem alguma história interessante sobre isso?",
                    "📝 Relata como você lidou com isso!"
                ],
                "debate": [
                    "⚖️ Vamos debater isso de forma construtiva!",
                    "🤝 Quero ouvir diferentes perspectivas!",
                    "💡 Cada opinião enriquece a discussão!",
                    "🌈 Vamos trocar ideias e aprender juntos!",
                    "🎯 Argumenta seu ponto de vista!"
                ]
            }
        }
        
        # CTAs temáticos baseados no conteúdo
        self.thematic_ctas = {
            "crescimento": [
                "🌱 Como você está investindo no seu crescimento?",
                "📈 Qual seu próximo passo na jornada de evolução?",
                "🎯 Que área da sua vida precisa de mais atenção?"
            ],
            "performance": [
                "⚡ Como você otimiza sua performance diária?",
                "🏆 Qual sua estratégia para alcançar resultados?",
                "💪 O que te motiva a dar o seu melhor?"
            ],
            "mindset": [
                "🧠 Como você trabalha sua mentalidade?",
                "✨ Que crenças você precisa transformar?",
                "🔄 Como você lida com mudanças de perspectiva?"
            ],
            "produtividade": [
                "⏰ Qual sua técnica favorita de produtividade?",
                "📋 Como você organiza suas prioridades?",
                "🎯 O que te ajuda a manter o foco?"
            ],
            "liderança": [
                "👥 Como você desenvolve suas habilidades de liderança?",
                "🌟 Qual característica de um líder mais te inspira?",
                "🤝 Como você influencia positivamente as pessoas?"
            ]
        }
    
    def get_cta_for_format(self, format_type: str, content_theme: str = None) -> str:
        """
        Retorna um CTA apropriado para o formato e tema do post.
        
        Args:
            format_type: Tipo do formato (standard, quote, tip, question)
            content_theme: Tema do conteúdo para CTAs temáticos
        
        Returns:
            String com o CTA selecionado
        """
        # Primeiro, tentar CTA temático se o tema for identificado
        if content_theme and content_theme in self.thematic_ctas:
            if random.random() < 0.3:  # 30% de chance de usar CTA temático
                return random.choice(self.thematic_ctas[content_theme])
        
        # Usar CTA específico do formato
        format_ctas = self.ctas_by_format.get(format_type, self.ctas_by_format["standard"])
        
        # Selecionar categoria aleatória dentro do formato
        category = random.choice(list(format_ctas.keys()))
        return random.choice(format_ctas[category])
    
    def get_multiple_ctas(self, format_type: str, count: int = 2, content_theme: str = None) -> List[str]:
        """
        Retorna múltiplos CTAs para o mesmo formato (útil para A/B testing).
        
        Args:
            format_type: Tipo do formato
            count: Número de CTAs a retornar
            content_theme: Tema do conteúdo
        
        Returns:
            Lista de CTAs únicos
        """
        ctas = []
        format_ctas = self.ctas_by_format.get(format_type, self.ctas_by_format["standard"])
        
        # Coletar todos os CTAs disponíveis para o formato
        all_ctas = []
        for category_ctas in format_ctas.values():
            all_ctas.extend(category_ctas)
        
        # Adicionar CTAs temáticos se disponíveis
        if content_theme and content_theme in self.thematic_ctas:
            all_ctas.extend(self.thematic_ctas[content_theme])
        
        # Selecionar CTAs únicos
        selected_ctas = random.sample(all_ctas, min(count, len(all_ctas)))
        return selected_ctas
    
    def get_cta_with_context(self, format_type: str, original_text: str = None) -> str:
        """
        Retorna um CTA contextualizado baseado no texto original do post.
        
        Args:
            format_type: Tipo do formato
            original_text: Texto original para análise de contexto
        
        Returns:
            CTA contextualizado
        """
        # Identificar tema baseado no texto original
        content_theme = self._identify_theme_from_text(original_text) if original_text else None
        
        return self.get_cta_for_format(format_type, content_theme)
    
    def _identify_theme_from_text(self, text: str) -> str:
        """Identifica o tema principal baseado no texto."""
        if not text:
            return None
        
        text_lower = text.lower()
        
        # Palavras-chave para cada tema
        theme_keywords = {
            "crescimento": ["crescimento", "evolução", "desenvolvimento", "progresso", "melhoria"],
            "performance": ["performance", "resultado", "eficiência", "otimização", "produtividade"],
            "mindset": ["mentalidade", "mindset", "pensamento", "crença", "perspectiva"],
            "liderança": ["liderança", "líder", "equipe", "gestão", "influência"],
            "produtividade": ["produtividade", "foco", "organização", "tempo", "prioridade"]
        }
        
        # Contar ocorrências de palavras-chave
        theme_scores = {}
        for theme, keywords in theme_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                theme_scores[theme] = score
        
        # Retornar tema com maior pontuação
        if theme_scores:
            return max(theme_scores, key=theme_scores.get)
        
        return None


# Função utilitária para uso direto
def get_cta_for_post(format_type: str, content_theme: str = None, original_text: str = None) -> str:
    """
    Função utilitária para obter um CTA para um post.
    
    Args:
        format_type: Tipo do formato do post
        content_theme: Tema do conteúdo (opcional)
        original_text: Texto original para análise de contexto (opcional)
    
    Returns:
        CTA apropriado para o post
    """
    cta_manager = CTAManager()
    
    if original_text:
        return cta_manager.get_cta_with_context(format_type, original_text)
    else:
        return cta_manager.get_cta_for_format(format_type, content_theme)