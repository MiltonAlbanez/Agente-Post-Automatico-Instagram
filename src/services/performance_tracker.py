"""
Sistema de Rastreamento de Performance para monitorar engajamento dos posts.
"""
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path


class PerformanceTracker:
    """Rastreia e analisa performance dos posts do Instagram."""
    
    def __init__(self, db_path: str = "data/performance.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Inicializa o banco de dados de performance."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS post_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id TEXT UNIQUE,
                    account_name TEXT,
                    content_format TEXT,
                    hashtags TEXT,
                    image_style TEXT,
                    published_at TIMESTAMP,
                    likes INTEGER DEFAULT 0,
                    comments INTEGER DEFAULT 0,
                    shares INTEGER DEFAULT 0,
                    reach INTEGER DEFAULT 0,
                    impressions INTEGER DEFAULT 0,
                    engagement_rate REAL DEFAULT 0.0,
                    last_updated TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS format_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_format TEXT,
                    total_posts INTEGER DEFAULT 0,
                    avg_likes REAL DEFAULT 0.0,
                    avg_comments REAL DEFAULT 0.0,
                    avg_engagement_rate REAL DEFAULT 0.0,
                    best_performing_hashtags TEXT,
                    last_calculated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS hashtag_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hashtag TEXT UNIQUE,
                    usage_count INTEGER DEFAULT 0,
                    total_likes INTEGER DEFAULT 0,
                    total_comments INTEGER DEFAULT 0,
                    avg_engagement_rate REAL DEFAULT 0.0,
                    last_used TIMESTAMP,
                    performance_score REAL DEFAULT 0.0
                )
            """)
    
    def log_post(self, post_data: Dict) -> bool:
        """
        Registra um novo post para rastreamento.
        
        Args:
            post_data: Dados do post incluindo post_id, account_name, content_format, etc.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO post_performance 
                    (post_id, account_name, content_format, hashtags, image_style, published_at, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    post_data.get('post_id'),
                    post_data.get('account_name'),
                    post_data.get('content_format'),
                    json.dumps(post_data.get('hashtags', [])),
                    post_data.get('image_style'),
                    post_data.get('published_at', datetime.now().isoformat()),
                    datetime.now().isoformat()
                ))
            return True
        except Exception as e:
            print(f"Erro ao registrar post: {e}")
            return False
    
    def update_metrics(self, post_id: str, metrics: Dict) -> bool:
        """
        Atualiza métricas de engajamento de um post.
        
        Args:
            post_id: ID do post
            metrics: Dicionário com likes, comments, shares, reach, impressions
        """
        try:
            # Calcular taxa de engajamento
            impressions = metrics.get('impressions', 0)
            likes = metrics.get('likes', 0)
            comments = metrics.get('comments', 0)
            shares = metrics.get('shares', 0)
            
            engagement_rate = 0.0
            if impressions > 0:
                engagement_rate = ((likes + comments + shares) / impressions) * 100
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE post_performance 
                    SET likes = ?, comments = ?, shares = ?, reach = ?, 
                        impressions = ?, engagement_rate = ?, last_updated = ?
                    WHERE post_id = ?
                """, (
                    likes, comments, shares, 
                    metrics.get('reach', 0), impressions, 
                    engagement_rate, datetime.now().isoformat(), post_id
                ))
            
            # Atualizar performance de hashtags
            self._update_hashtag_performance(post_id, metrics)
            return True
        except Exception as e:
            print(f"Erro ao atualizar métricas: {e}")
            return False
    
    def _update_hashtag_performance(self, post_id: str, metrics: Dict):
        """Atualiza performance individual das hashtags."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Buscar hashtags do post
                cursor = conn.execute(
                    "SELECT hashtags FROM post_performance WHERE post_id = ?", 
                    (post_id,)
                )
                result = cursor.fetchone()
                if not result:
                    return
                
                hashtags = json.loads(result[0])
                likes = metrics.get('likes', 0)
                comments = metrics.get('comments', 0)
                impressions = metrics.get('impressions', 0)
                
                engagement_rate = 0.0
                if impressions > 0:
                    engagement_rate = ((likes + comments) / impressions) * 100
                
                # Atualizar cada hashtag
                for hashtag in hashtags:
                    conn.execute("""
                        INSERT OR REPLACE INTO hashtag_performance 
                        (hashtag, usage_count, total_likes, total_comments, 
                         avg_engagement_rate, last_used, performance_score)
                        VALUES (
                            ?, 
                            COALESCE((SELECT usage_count FROM hashtag_performance WHERE hashtag = ?), 0) + 1,
                            COALESCE((SELECT total_likes FROM hashtag_performance WHERE hashtag = ?), 0) + ?,
                            COALESCE((SELECT total_comments FROM hashtag_performance WHERE hashtag = ?), 0) + ?,
                            ?,
                            ?,
                            ?
                        )
                    """, (
                        hashtag, hashtag, hashtag, likes, hashtag, comments,
                        engagement_rate, datetime.now().isoformat(),
                        engagement_rate * 0.7 + (likes + comments) * 0.3  # Score ponderado
                    ))
        except Exception as e:
            print(f"Erro ao atualizar performance de hashtags: {e}")
    
    def get_format_performance(self) -> Dict[str, Dict]:
        """Retorna análise de performance por formato de conteúdo."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT 
                        content_format,
                        COUNT(*) as total_posts,
                        AVG(likes) as avg_likes,
                        AVG(comments) as avg_comments,
                        AVG(engagement_rate) as avg_engagement_rate,
                        MAX(engagement_rate) as max_engagement_rate
                    FROM post_performance 
                    WHERE content_format IS NOT NULL
                    GROUP BY content_format
                    ORDER BY avg_engagement_rate DESC
                """)
                
                results = {}
                for row in cursor.fetchall():
                    format_name = row[0]
                    results[format_name] = {
                        'total_posts': row[1],
                        'avg_likes': round(row[2], 2),
                        'avg_comments': round(row[3], 2),
                        'avg_engagement_rate': round(row[4], 2),
                        'max_engagement_rate': round(row[5], 2)
                    }
                
                return results
        except Exception as e:
            print(f"Erro ao analisar performance por formato: {e}")
            return {}
    
    def get_top_hashtags(self, limit: int = 20) -> List[Dict]:
        """Retorna as hashtags com melhor performance."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT hashtag, usage_count, avg_engagement_rate, 
                           performance_score, last_used
                    FROM hashtag_performance 
                    WHERE usage_count >= 2
                    ORDER BY performance_score DESC 
                    LIMIT ?
                """, (limit,))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'hashtag': row[0],
                        'usage_count': row[1],
                        'avg_engagement_rate': round(row[2], 2),
                        'performance_score': round(row[3], 2),
                        'last_used': row[4]
                    })
                
                return results
        except Exception as e:
            print(f"Erro ao buscar top hashtags: {e}")
            return []
    
    def get_performance_insights(self) -> Dict:
        """Retorna insights gerais de performance."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Estatísticas gerais
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_posts,
                        AVG(likes) as avg_likes,
                        AVG(comments) as avg_comments,
                        AVG(engagement_rate) as avg_engagement_rate,
                        MAX(engagement_rate) as best_engagement_rate
                    FROM post_performance
                """)
                general_stats = cursor.fetchone()
                
                # Melhor dia da semana
                cursor = conn.execute("""
                    SELECT 
                        strftime('%w', published_at) as day_of_week,
                        AVG(engagement_rate) as avg_engagement
                    FROM post_performance 
                    WHERE published_at IS NOT NULL
                    GROUP BY strftime('%w', published_at)
                    ORDER BY avg_engagement DESC
                    LIMIT 1
                """)
                best_day = cursor.fetchone()
                
                # Melhor horário
                cursor = conn.execute("""
                    SELECT 
                        strftime('%H', published_at) as hour,
                        AVG(engagement_rate) as avg_engagement
                    FROM post_performance 
                    WHERE published_at IS NOT NULL
                    GROUP BY strftime('%H', published_at)
                    ORDER BY avg_engagement DESC
                    LIMIT 1
                """)
                best_hour = cursor.fetchone()
                
                days_map = {
                    '0': 'Domingo', '1': 'Segunda', '2': 'Terça', 
                    '3': 'Quarta', '4': 'Quinta', '5': 'Sexta', '6': 'Sábado'
                }
                
                return {
                    'total_posts': general_stats[0] if general_stats else 0,
                    'avg_likes': round(general_stats[1], 2) if general_stats[1] else 0,
                    'avg_comments': round(general_stats[2], 2) if general_stats[2] else 0,
                    'avg_engagement_rate': round(general_stats[3], 2) if general_stats[3] else 0,
                    'best_engagement_rate': round(general_stats[4], 2) if general_stats[4] else 0,
                    'best_day_of_week': days_map.get(str(best_day[0]), 'N/A') if best_day else 'N/A',
                    'best_hour': f"{best_hour[0]}:00" if best_hour else 'N/A'
                }
        except Exception as e:
            print(f"Erro ao gerar insights: {e}")
            return {}
    
    def get_optimization_recommendations(self) -> List[str]:
        """Retorna recomendações baseadas na análise de performance."""
        recommendations = []
        
        try:
            format_performance = self.get_format_performance()
            top_hashtags = self.get_top_hashtags(10)
            insights = self.get_performance_insights()
            
            # Recomendações baseadas em formatos
            if format_performance:
                best_format = max(format_performance.items(), key=lambda x: x[1]['avg_engagement_rate'])
                recommendations.append(
                    f"📈 Formato '{best_format[0]}' tem melhor engajamento ({best_format[1]['avg_engagement_rate']}%). Use mais frequentemente."
                )
                
                worst_format = min(format_performance.items(), key=lambda x: x[1]['avg_engagement_rate'])
                if worst_format[1]['avg_engagement_rate'] < best_format[1]['avg_engagement_rate'] * 0.7:
                    recommendations.append(
                        f"⚠️ Formato '{worst_format[0]}' tem baixo engajamento. Considere ajustar a abordagem."
                    )
            
            # Recomendações baseadas em hashtags
            if top_hashtags:
                top_3_hashtags = [h['hashtag'] for h in top_hashtags[:3]]
                recommendations.append(
                    f"🏷️ Hashtags de alta performance: {', '.join(top_3_hashtags)}. Use com mais frequência."
                )
            
            # Recomendações baseadas em timing
            if insights.get('best_day_of_week') != 'N/A':
                recommendations.append(
                    f"📅 Melhor dia para postar: {insights['best_day_of_week']} às {insights.get('best_hour', 'N/A')}."
                )
            
            # Recomendações gerais
            if insights.get('avg_engagement_rate', 0) < 2.0:
                recommendations.append(
                    "💡 Taxa de engajamento baixa. Experimente mais perguntas diretas e calls-to-action."
                )
            
            if len(recommendations) == 0:
                recommendations.append("📊 Dados insuficientes para recomendações. Continue postando para gerar insights.")
            
            return recommendations
            
        except Exception as e:
            print(f"Erro ao gerar recomendações: {e}")
            return ["❌ Erro ao analisar dados de performance."]


# Função utilitária para integração
def track_post_performance(post_id: str, account_name: str, content_format: str, 
                          hashtags: List[str], image_style: str = "standard", 
                          custom_metadata: Dict = None) -> bool:
    """
    Função utilitária para registrar um post no sistema de tracking.
    
    Args:
        post_id: ID único do post
        account_name: Nome da conta
        content_format: Formato do conteúdo (quote, tip, question, standard)
        hashtags: Lista de hashtags utilizadas
        image_style: Estilo da imagem utilizada
        custom_metadata: Metadados adicionais (opcional)
    
    Returns:
        bool: True se registrado com sucesso
    """
    tracker = PerformanceTracker()
    post_data = {
        'post_id': post_id,
        'account_name': account_name,
        'content_format': content_format,
        'hashtags': hashtags,
        'image_style': image_style,
        'published_at': datetime.now().isoformat()
    }
    
    # Adicionar metadados customizados se fornecidos
    if custom_metadata:
        post_data.update(custom_metadata)
    
    return tracker.log_post(post_data)