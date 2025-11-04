"""
Sistema Avançado de Monitoramento de Engagement
Coleta automaticamente métricas do Instagram e analisa performance dos conceitos visuais.
"""
import json
import sqlite3
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import statistics
from dataclasses import dataclass

from .instagram_client_robust import InstagramClientRobust as InstagramClient
from .performance_tracker import PerformanceTracker
from .superior_concept_manager import SuperiorConceptManager


@dataclass
class EngagementMetrics:
    """Estrutura para métricas de engagement."""
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    reach: int = 0
    impressions: int = 0
    engagement_rate: float = 0.0
    timestamp: str = ""


@dataclass
class ConceptPerformance:
    """Performance de um conceito visual."""
    concept_name: str
    total_posts: int
    avg_engagement_rate: float
    avg_likes: int
    avg_comments: int
    best_performing_post: str
    trend_direction: str  # 'up', 'down', 'stable'
    recommendation: str


class EngagementMonitor:
    """Monitor avançado de engagement com análise de conceitos visuais."""
    
    def __init__(self, db_path: str = "data/engagement_monitor.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.performance_tracker = PerformanceTracker()
        self.concept_manager = SuperiorConceptManager()
        self._init_database()
    
    def _init_database(self):
        """Inicializa banco de dados específico para monitoramento."""
        with sqlite3.connect(self.db_path) as conn:
            # Tabela para histórico de métricas
            conn.execute("""
                CREATE TABLE IF NOT EXISTS engagement_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id TEXT,
                    account_name TEXT,
                    concept_used TEXT,
                    collection_timestamp TIMESTAMP,
                    likes INTEGER,
                    comments INTEGER,
                    shares INTEGER,
                    saves INTEGER,
                    reach INTEGER,
                    impressions INTEGER,
                    engagement_rate REAL,
                    hours_since_post INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela para análise de conceitos
            conn.execute("""
                CREATE TABLE IF NOT EXISTS concept_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    concept_name TEXT,
                    analysis_date DATE,
                    total_posts INTEGER,
                    avg_engagement_rate REAL,
                    avg_likes REAL,
                    avg_comments REAL,
                    trend_direction TEXT,
                    performance_score REAL,
                    recommendation TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela para alertas e insights
            conn.execute("""
                CREATE TABLE IF NOT EXISTS engagement_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_type TEXT,
                    message TEXT,
                    severity TEXT,
                    post_id TEXT,
                    concept_name TEXT,
                    metric_value REAL,
                    threshold_value REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved BOOLEAN DEFAULT FALSE
                )
            """)
    
    async def collect_metrics_for_recent_posts(self, hours_back: int = 24) -> List[EngagementMetrics]:
        """
        Coleta métricas para posts recentes.
        
        Args:
            hours_back: Quantas horas atrás buscar posts
        """
        try:
            # Buscar posts recentes do banco
            with sqlite3.connect(self.performance_tracker.db_path) as conn:
                cursor = conn.execute("""
                    SELECT post_id, account_name, published_at, image_style
                    FROM post_performance 
                    WHERE published_at > datetime('now', '-{} hours')
                    ORDER BY published_at DESC
                """.format(hours_back))
                
                recent_posts = cursor.fetchall()
            
            metrics_collected = []
            
            for post_id, account_name, published_at, concept_used in recent_posts:
                # Simular coleta de métricas (em produção, usar API do Instagram)
                metrics = await self._collect_post_metrics(post_id, account_name)
                
                if metrics:
                    # Calcular horas desde publicação
                    pub_time = datetime.fromisoformat(published_at)
                    hours_since = (datetime.now() - pub_time).total_seconds() / 3600
                    
                    # Salvar no histórico
                    self._save_metrics_history(
                        post_id, account_name, concept_used, 
                        metrics, int(hours_since)
                    )
                    
                    metrics_collected.append(metrics)
            
            return metrics_collected
            
        except Exception as e:
            print(f"Erro ao coletar métricas: {e}")
            return []
    
    async def _collect_post_metrics(self, post_id: str, account_name: str) -> Optional[EngagementMetrics]:
        """
        Coleta métricas específicas de um post.
        
        Args:
            post_id: ID do post
            account_name: Nome da conta
        """
        try:
            # Em produção, usar Instagram Basic Display API ou Instagram Graph API
            # Por agora, simular dados realistas baseados em padrões
            
            # Simular métricas baseadas em tempo desde publicação
            import random
            
            # Métricas simuladas mais realistas
            base_likes = random.randint(50, 300)
            base_comments = random.randint(5, 25)
            base_shares = random.randint(2, 15)
            base_saves = random.randint(10, 50)
            base_reach = random.randint(500, 2000)
            base_impressions = random.randint(800, 3000)
            
            engagement_rate = ((base_likes + base_comments + base_shares + base_saves) / base_impressions) * 100
            
            return EngagementMetrics(
                likes=base_likes,
                comments=base_comments,
                shares=base_shares,
                saves=base_saves,
                reach=base_reach,
                impressions=base_impressions,
                engagement_rate=round(engagement_rate, 2),
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            print(f"Erro ao coletar métricas do post {post_id}: {e}")
            return None
    
    def _save_metrics_history(self, post_id: str, account_name: str, 
                            concept_used: str, metrics: EngagementMetrics, 
                            hours_since: int):
        """Salva métricas no histórico."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO engagement_history 
                    (post_id, account_name, concept_used, collection_timestamp,
                     likes, comments, shares, saves, reach, impressions, 
                     engagement_rate, hours_since_post)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    post_id, account_name, concept_used, metrics.timestamp,
                    metrics.likes, metrics.comments, metrics.shares, metrics.saves,
                    metrics.reach, metrics.impressions, metrics.engagement_rate,
                    hours_since
                ))
        except Exception as e:
            print(f"Erro ao salvar histórico: {e}")
    
    def track_post(self, post_data: Dict):
        """
        Registra um post para monitoramento futuro.
        
        Args:
            post_data: Dicionário com dados do post (timestamp, status, type, post_id, concept)
        """
        try:
            # Extrair dados do post
            post_id = post_data.get('post_id', 'unknown')
            concept = post_data.get('concept', 'unknown')
            timestamp = post_data.get('timestamp', datetime.now().isoformat())
            status = post_data.get('status', 'unknown')
            post_type = post_data.get('type', 'unknown')
            
            # Registrar no banco para monitoramento futuro
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO engagement_history 
                    (post_id, account_name, concept_used, collection_timestamp,
                     likes, comments, shares, saves, reach, impressions, 
                     engagement_rate, hours_since_post)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    post_id, post_type, concept, timestamp,
                    0, 0, 0, 0, 0, 0, 0.0, 0  # Valores iniciais, serão atualizados posteriormente
                ))
            
            print(f"✅ Post {post_id} registrado para monitoramento (conceito: {concept})")
            
        except Exception as e:
            print(f"Erro ao registrar post para monitoramento: {e}")
    
    def analyze_concept_performance(self, days_back: int = 7) -> List[ConceptPerformance]:
        """
        Analisa performance dos conceitos visuais.
        
        Args:
            days_back: Quantos dias analisar
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT 
                        concept_used,
                        COUNT(*) as total_posts,
                        AVG(engagement_rate) as avg_engagement,
                        AVG(likes) as avg_likes,
                        AVG(comments) as avg_comments,
                        MAX(engagement_rate) as max_engagement,
                        post_id
                    FROM engagement_history 
                    WHERE collection_timestamp > datetime('now', '-{} days')
                    GROUP BY concept_used
                    HAVING total_posts > 0
                    ORDER BY avg_engagement DESC
                """.format(days_back))
                
                results = cursor.fetchall()
            
            concept_performances = []
            
            for row in results:
                concept_name, total_posts, avg_engagement, avg_likes, avg_comments, max_engagement, best_post = row
                
                # Analisar tendência
                trend = self._analyze_trend(concept_name, days_back)
                
                # Gerar recomendação
                recommendation = self._generate_recommendation(
                    concept_name, avg_engagement, trend, total_posts
                )
                
                concept_performances.append(ConceptPerformance(
                    concept_name=concept_name or "Conceito Desconhecido",
                    total_posts=total_posts,
                    avg_engagement_rate=round(avg_engagement, 2),
                    avg_likes=int(avg_likes),
                    avg_comments=int(avg_comments),
                    best_performing_post=best_post,
                    trend_direction=trend,
                    recommendation=recommendation
                ))
            
            # Salvar análise no banco
            self._save_concept_analysis(concept_performances)
            
            return concept_performances
            
        except Exception as e:
            print(f"Erro ao analisar performance dos conceitos: {e}")
            return []
    
    def _analyze_trend(self, concept_name: str, days_back: int) -> str:
        """Analisa tendência de performance de um conceito."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT engagement_rate, collection_timestamp
                    FROM engagement_history 
                    WHERE concept_used = ? 
                    AND collection_timestamp > datetime('now', '-{} days')
                    ORDER BY collection_timestamp ASC
                """.format(days_back), (concept_name,))
                
                data = cursor.fetchall()
            
            if len(data) < 3:
                return "stable"
            
            # Dividir em duas metades para comparar
            mid_point = len(data) // 2
            first_half = [row[0] for row in data[:mid_point]]
            second_half = [row[0] for row in data[mid_point:]]
            
            avg_first = statistics.mean(first_half)
            avg_second = statistics.mean(second_half)
            
            # Calcular diferença percentual
            diff_percent = ((avg_second - avg_first) / avg_first) * 100
            
            if diff_percent > 10:
                return "up"
            elif diff_percent < -10:
                return "down"
            else:
                return "stable"
                
        except Exception as e:
            print(f"Erro ao analisar tendência: {e}")
            return "stable"
    
    def _generate_recommendation(self, concept_name: str, avg_engagement: float, 
                               trend: str, total_posts: int) -> str:
        """Gera recomendação baseada na performance."""
        if avg_engagement > 8.0 and trend == "up":
            return f"🚀 EXCELENTE: Conceito '{concept_name}' está performando muito bem! Use mais frequentemente."
        elif avg_engagement > 6.0 and trend in ["up", "stable"]:
            return f"✅ BOM: Conceito '{concept_name}' tem boa performance. Continue usando."
        elif avg_engagement > 4.0 and trend == "down":
            return f"⚠️ ATENÇÃO: Conceito '{concept_name}' está perdendo performance. Considere ajustes."
        elif avg_engagement < 4.0:
            return f"🔄 REVISAR: Conceito '{concept_name}' precisa de otimização ou substituição."
        elif total_posts < 3:
            return f"📊 DADOS INSUFICIENTES: Conceito '{concept_name}' precisa de mais posts para análise."
        else:
            return f"📈 MONITORAR: Conceito '{concept_name}' está estável. Continue monitorando."
    
    def _save_concept_analysis(self, performances: List[ConceptPerformance]):
        """Salva análise de conceitos no banco."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                for perf in performances:
                    # Calcular score de performance
                    score = (perf.avg_engagement_rate * 0.6) + (perf.avg_likes / 100 * 0.3) + (perf.avg_comments / 10 * 0.1)
                    
                    conn.execute("""
                        INSERT INTO concept_analytics 
                        (concept_name, analysis_date, total_posts, avg_engagement_rate,
                         avg_likes, avg_comments, trend_direction, performance_score, recommendation)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        perf.concept_name, datetime.now().date().isoformat(),
                        perf.total_posts, perf.avg_engagement_rate,
                        perf.avg_likes, perf.avg_comments, perf.trend_direction,
                        round(score, 2), perf.recommendation
                    ))
        except Exception as e:
            print(f"Erro ao salvar análise: {e}")
    
    def generate_engagement_report(self, days_back: int = 7) -> Dict:
        """Gera relatório completo de engagement."""
        try:
            # Coletar dados gerais
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_posts,
                        AVG(engagement_rate) as avg_engagement,
                        MAX(engagement_rate) as max_engagement,
                        MIN(engagement_rate) as min_engagement,
                        AVG(likes) as avg_likes,
                        AVG(comments) as avg_comments
                    FROM engagement_history 
                    WHERE collection_timestamp > datetime('now', '-{} days')
                """.format(days_back))
                
                general_stats = cursor.fetchone()
            
            # Analisar conceitos
            concept_performances = self.analyze_concept_performance(days_back)
            
            # Identificar alertas
            alerts = self._check_performance_alerts()
            
            report = {
                "period_days": days_back,
                "generated_at": datetime.now().isoformat(),
                "general_stats": {
                    "total_posts": general_stats[0] or 0,
                    "avg_engagement_rate": round(general_stats[1] or 0, 2),
                    "max_engagement_rate": round(general_stats[2] or 0, 2),
                    "min_engagement_rate": round(general_stats[3] or 0, 2),
                    "avg_likes": int(general_stats[4] or 0),
                    "avg_comments": int(general_stats[5] or 0)
                },
                "concept_performance": [
                    {
                        "concept": perf.concept_name,
                        "posts": perf.total_posts,
                        "engagement_rate": perf.avg_engagement_rate,
                        "likes": perf.avg_likes,
                        "comments": perf.avg_comments,
                        "trend": perf.trend_direction,
                        "recommendation": perf.recommendation
                    }
                    for perf in concept_performances
                ],
                "alerts": alerts,
                "top_performing_concept": concept_performances[0].concept_name if concept_performances else None,
                "recommendations": self._generate_overall_recommendations(concept_performances)
            }
            
            return report
            
        except Exception as e:
            print(f"Erro ao gerar relatório: {e}")
            return {}
    
    def _check_performance_alerts(self) -> List[Dict]:
        """Verifica alertas de performance."""
        alerts = []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Verificar posts com engagement muito baixo
                cursor = conn.execute("""
                    SELECT post_id, concept_used, engagement_rate
                    FROM engagement_history 
                    WHERE engagement_rate < 2.0 
                    AND collection_timestamp > datetime('now', '-24 hours')
                """)
                
                low_engagement = cursor.fetchall()
                
                for post_id, concept, rate in low_engagement:
                    alerts.append({
                        "type": "low_engagement",
                        "severity": "warning",
                        "message": f"Post {post_id} com conceito '{concept}' tem engagement muito baixo ({rate}%)",
                        "post_id": post_id,
                        "concept": concept,
                        "value": rate
                    })
        
        except Exception as e:
            print(f"Erro ao verificar alertas: {e}")
        
        return alerts
    
    def _generate_overall_recommendations(self, performances: List[ConceptPerformance]) -> List[str]:
        """Gera recomendações gerais baseadas na análise."""
        recommendations = []
        
        if not performances:
            recommendations.append("📊 Colete mais dados para gerar recomendações precisas.")
            return recommendations
        
        # Identificar melhor conceito
        best_concept = performances[0]
        recommendations.append(
            f"🏆 Conceito '{best_concept.concept_name}' é o mais eficaz "
            f"({best_concept.avg_engagement_rate}% engagement). Use mais frequentemente."
        )
        
        # Identificar conceitos em declínio
        declining = [p for p in performances if p.trend_direction == "down"]
        if declining:
            recommendations.append(
                f"⚠️ {len(declining)} conceito(s) em declínio. "
                f"Considere revisar: {', '.join([p.concept_name for p in declining[:3]])}"
            )
        
        # Sugerir diversificação
        if len(performances) < 5:
            recommendations.append(
                "🎨 Considere adicionar mais conceitos visuais para diversificar o conteúdo."
            )
        
        return recommendations


# Função utilitária para executar monitoramento
async def run_engagement_monitoring():
    """Executa ciclo completo de monitoramento."""
    monitor = EngagementMonitor()
    
    print("🔍 Coletando métricas de posts recentes...")
    await monitor.collect_metrics_for_recent_posts(24)
    
    print("📊 Analisando performance dos conceitos...")
    performances = monitor.analyze_concept_performance(7)
    
    print("📋 Gerando relatório de engagement...")
    report = monitor.generate_engagement_report(7)
    
    return report


if __name__ == "__main__":
    # Teste do sistema
    asyncio.run(run_engagement_monitoring())