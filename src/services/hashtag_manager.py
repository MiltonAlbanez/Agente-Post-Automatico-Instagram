"""
Sistema de Hashtags Dinâmicas para otimizar engajamento e variedade de conteúdo.
"""
import random
from datetime import datetime
from typing import List, Dict


class HashtagManager:
    """Gerencia hashtags dinâmicas, sazonais e de tendências."""
    
    def __init__(self):
        self.base_hashtags = [
            "#Empreendedorismo", "#Coaching", "#PNL", "#DesenvolvimentoPessoal", 
            "#SucessoDigital", "#JornadaEmpreendedora"
        ]
        
        # Hashtags sazonais por mês
        self.seasonal_hashtags = {
            1: ["#NovoAno", "#MetasAnuais", "#RecomeçoEmpresarial", "#PlanejamentoEstrategico"],
            2: ["#FocoEResultados", "#ProdutividadeMaxima", "#DesafioFevereiro"],
            3: ["#MulherEmpreendedora", "#LiderançaFeminina", "#InovacaoEmpresarial"],
            4: ["#RenovacaoEmpresarial", "#CrescimentoSustentavel", "#TransformacaoDigital"],
            5: ["#TrabalhoEVida", "#MotivacaoMaio", "#DesenvolvimentoProfissional"],
            6: ["#MeioDoAno", "#AvaliacaoMetas", "#AjusteDeRota"],
            7: ["#FeriasEstrategicas", "#DescansoAtivo", "#ReflexaoEmpresarial"],
            8: ["#RetomadaEstrategica", "#AceleracaoNegocios", "#FocoTotal"],
            9: ["#PrimaveraEmpresarial", "#NovosCiclos", "#RenovacaoMental"],
            10: ["#UltimoTrimestre", "#SprintFinal", "#ResultadosConcretos"],
            11: ["#GratidaoEmpresarial", "#BalancoAnual", "#PreparacaoFuturo"],
            12: ["#FechamentoAno", "#PlanejamentoFuturo", "#ReflexaoAnual"]
        }
        
        # Hashtags por dia da semana
        self.weekly_hashtags = {
            0: ["#SegundaMotivacional", "#InicioSemana", "#FocoTotal"],  # Segunda
            1: ["#TercaTransformacao", "#DesenvolvimentoContinuo"],      # Terça
            2: ["#QuartaWisdom", "#ConhecimentoPoder", "#AprendizadoContinuo"],  # Quarta
            3: ["#QuintaQuebra", "#InovacaoEmpresarial", "#Criatividade"],  # Quinta
            4: ["#SextaReflexiva", "#BalancoSemanal", "#PreparacaoWeekend"],  # Sexta
            5: ["#SabadoEstrategico", "#PlanejamentoWeekend"],           # Sábado
            6: ["#DomingoReflexao", "#DescansoAtivo", "#PreparacaoSemana"]  # Domingo
        }
        
        # Hashtags de tendências (atualizadas periodicamente)
        self.trending_hashtags = [
            "#InteligenciaArtificial", "#AutomacaoEmpresarial", "#MarketingDigital",
            "#VendasOnline", "#InfluencerMarketing", "#ContentMarketing",
            "#PersonalBranding", "#NetworkingDigital", "#MindsetEmpreendedor",
            "#LiderancaDigital", "#InovacaoDisruptiva", "#StartupMindset",
            "#EconomiaDigital", "#FuturoDoTrabalho", "#TransformacaoMental"
        ]
        
        # Hashtags específicas por tema/contexto
        self.contextual_hashtags = {
            "lideranca": ["#LiderancaAutentica", "#GestaoDeEquipes", "#InfluenciaPositiva"],
            "vendas": ["#VendasEstrategicas", "#NegociacaoEficaz", "#RelacionamentoCliente"],
            "mindset": ["#MindsetVencedor", "#CrencasLimitantes", "#Autoconhecimento"],
            "produtividade": ["#ProdutividadeInteligente", "#GestaoTempo", "#FocoEResultados"],
            "inovacao": ["#InovacaoEmpresarial", "#CriatividadeEstrategica", "#DisrupcaoPositiva"],
            "networking": ["#NetworkingEstrategico", "#RelacionamentoProfissional", "#ConexoesPoder"],
            "financas": ["#EducacaoFinanceira", "#InvestimentoInteligente", "#LiberdadeFinanceira"]
        }
    
    def get_dynamic_hashtags(self, context: str = None, include_seasonal: bool = True, 
                           include_weekly: bool = True, include_trending: bool = True) -> List[str]:
        """
        Gera uma lista de hashtags dinâmicas baseada no contexto e data atual.
        
        Args:
            context: Contexto específico (lideranca, vendas, mindset, etc.)
            include_seasonal: Incluir hashtags sazonais
            include_weekly: Incluir hashtags do dia da semana
            include_trending: Incluir hashtags de tendência
        
        Returns:
            Lista de hashtags otimizada para o momento atual
        """
        hashtags = self.base_hashtags.copy()
        
        # Adicionar hashtags sazonais
        if include_seasonal:
            current_month = datetime.now().month
            seasonal = self.seasonal_hashtags.get(current_month, [])
            if seasonal:
                hashtags.append(random.choice(seasonal))
        
        # Adicionar hashtags do dia da semana
        if include_weekly:
            current_weekday = datetime.now().weekday()
            weekly = self.weekly_hashtags.get(current_weekday, [])
            if weekly:
                hashtags.append(random.choice(weekly))
        
        # Adicionar hashtags de tendência
        if include_trending:
            trending = random.sample(self.trending_hashtags, min(2, len(self.trending_hashtags)))
            hashtags.extend(trending)
        
        # Adicionar hashtags contextuais
        if context and context in self.contextual_hashtags:
            contextual = random.choice(self.contextual_hashtags[context])
            hashtags.append(contextual)
        
        # Remover duplicatas mantendo ordem
        seen = set()
        unique_hashtags = []
        for tag in hashtags:
            if tag not in seen:
                unique_hashtags.append(tag)
                seen.add(tag)
        
        return unique_hashtags
    
    def get_hashtag_string(self, context: str = None, max_hashtags: int = 10) -> str:
        """
        Retorna uma string formatada com hashtags dinâmicas.
        
        Args:
            context: Contexto específico
            max_hashtags: Número máximo de hashtags
        
        Returns:
            String formatada com hashtags separadas por espaços
        """
        hashtags = self.get_dynamic_hashtags(context)
        return " ".join(hashtags[:max_hashtags])
    
    def analyze_content_context(self, content: str) -> str:
        """
        Analisa o conteúdo para determinar o contexto mais apropriado.
        
        Args:
            content: Texto do conteúdo a ser analisado
        
        Returns:
            Contexto identificado ou None
        """
        content_lower = content.lower()
        
        context_keywords = {
            "lideranca": ["líder", "liderança", "equipe", "gestão", "comando"],
            "vendas": ["venda", "cliente", "negociação", "proposta", "conversão"],
            "mindset": ["mindset", "mentalidade", "crença", "pensamento", "atitude"],
            "produtividade": ["produtividade", "eficiência", "tempo", "foco", "resultado"],
            "inovacao": ["inovação", "criatividade", "novo", "transformação", "mudança"],
            "networking": ["networking", "relacionamento", "conexão", "rede", "contato"],
            "financas": ["dinheiro", "investimento", "financeiro", "lucro", "receita"]
        }
        
        for context, keywords in context_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                return context
        
        return None
    
    def generate_trending_hashtags(self, context: str = None, keywords: List[str] = None) -> List[str]:
        """
        Gera hashtags focadas em tendências e popularidade.
        
        Args:
            context: Contexto do conteúdo
            keywords: Palavras-chave adicionais
        
        Returns:
            Lista de hashtags trending
        """
        hashtags = []
        
        # Priorizar hashtags trending
        hashtags.extend(random.sample(self.trending_hashtags, min(6, len(self.trending_hashtags))))
        
        # Adicionar algumas hashtags base populares
        popular_base = ["#Empreendedorismo", "#SucessoDigital", "#DesenvolvimentoPessoal"]
        hashtags.extend(popular_base)
        
        # Hashtags sazonais atuais
        current_month = datetime.now().month
        if current_month in self.seasonal_hashtags:
            seasonal = random.sample(self.seasonal_hashtags[current_month], 2)
            hashtags.extend(seasonal)
        
        # Hashtags do dia da semana
        current_weekday = datetime.now().weekday()
        if current_weekday in self.weekly_hashtags:
            weekly = random.sample(self.weekly_hashtags[current_weekday], 1)
            hashtags.extend(weekly)
        
        # Remover duplicatas e limitar
        unique_hashtags = list(dict.fromkeys(hashtags))
        return unique_hashtags[:12]
    
    def generate_niche_hashtags(self, context: str = None, keywords: List[str] = None) -> List[str]:
        """
        Gera hashtags focadas em nicho específico e menos competitivas.
        
        Args:
            context: Contexto do conteúdo
            keywords: Palavras-chave adicionais
        
        Returns:
            Lista de hashtags de nicho
        """
        hashtags = []
        
        # Hashtags base específicas do nicho
        niche_base = ["#CoachingPNL", "#JornadaEmpreendedora", "#MindsetEmpreendedor"]
        hashtags.extend(niche_base)
        
        # Hashtags específicas por contexto
        context_specific = {
            "lideranca": ["#LiderancaAutentica", "#GestaoHumanizada", "#LiderCoach"],
            "vendas": ["#VendasConsultivas", "#RelacionamentoCliente", "#NegociacaoGanha"],
            "mindset": ["#TransformacaoMental", "#CrencasLimitantes", "#MudancaMindset"],
            "produtividade": ["#FocoEResultados", "#GestaoTempo", "#EficienciaMaxima"],
            "inovacao": ["#InovacaoEmpresarial", "#CriatividadeEmpresarial", "#DisrupcaoPositiva"],
            "networking": ["#NetworkingEstrategico", "#RelacionamentoProfissional", "#ConexoesValiosas"],
            "financas": ["#EducacaoFinanceira", "#InvestimentoInteligente", "#LiberdadeFinanceira"]
        }
        
        if context and context in context_specific:
            hashtags.extend(context_specific[context])
        
        # Adicionar algumas hashtags menos competitivas
        niche_specific = [
            "#EmpreendedorismoBrasil", "#CoachingBrasil", "#PNLPratica",
            "#DesenvolvimentoHumano", "#TransformacaoPessoal", "#CrescimentoSustentavel",
            "#LiderancaConsciente", "#NegociosConscientes", "#ImpactoPositivo"
        ]
        hashtags.extend(random.sample(niche_specific, 4))
        
        # Hashtags sazonais mais específicas
        current_month = datetime.now().month
        if current_month in self.seasonal_hashtags:
            seasonal = random.sample(self.seasonal_hashtags[current_month], 1)
            hashtags.extend(seasonal)
        
        # Remover duplicatas e limitar
        unique_hashtags = list(dict.fromkeys(hashtags))
        return unique_hashtags[:12]


# Função utilitária para integração fácil
def get_optimized_hashtags(content: str = "", max_hashtags: int = 10) -> str:
    """
    Função utilitária para obter hashtags otimizadas rapidamente.
    
    Args:
        content: Conteúdo para análise de contexto
        max_hashtags: Número máximo de hashtags
    
    Returns:
        String com hashtags otimizadas
    """
    manager = HashtagManager()
    context = manager.analyze_content_context(content) if content else None
    return manager.get_hashtag_string(context, max_hashtags)