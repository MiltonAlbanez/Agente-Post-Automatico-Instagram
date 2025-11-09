"""
Framework de A/B Testing para otimizar diferentes estilos de conteúdo.
"""
import json
import sqlite3
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass


@dataclass
class ABTestVariant:
    """Representa uma variante de teste A/B."""
    id: str
    name: str
    description: str
    config: Dict
    weight: float = 1.0  # Peso para distribuição de tráfego


@dataclass
class ABTest:
    """Representa um teste A/B completo."""
    id: str
    name: str
    description: str
    variants: List[ABTestVariant]
    start_date: datetime
    end_date: Optional[datetime] = None
    status: str = "active"  # active, paused, completed
    target_metric: str = "engagement_rate"
    minimum_sample_size: int = 20


class ABTestingFramework:
    """Framework para gerenciar testes A/B de conteúdo."""
    
    def __init__(self, db_path: str = "data/ab_testing.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
        self._load_default_tests()
    
    def _init_database(self):
        """Inicializa o banco de dados de A/B testing."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ab_tests (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    variants TEXT,
                    start_date TIMESTAMP,
                    end_date TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    target_metric TEXT DEFAULT 'engagement_rate',
                    minimum_sample_size INTEGER DEFAULT 20,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ab_test_assignments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_id TEXT,
                    variant_id TEXT,
                    post_id TEXT,
                    account_name TEXT,
                    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (test_id) REFERENCES ab_tests (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ab_test_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_id TEXT,
                    variant_id TEXT,
                    post_id TEXT,
                    metric_name TEXT,
                    metric_value REAL,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (test_id) REFERENCES ab_tests (id)
                )
            """)
    
    def _load_default_tests(self):
        """Carrega testes A/B padrão se não existirem."""
        default_tests = [
            {
                "id": "content_format_test",
                "name": "Teste de Formatos de Conteúdo",
                "description": "Compara performance entre diferentes formatos de post",
                "variants": [
                    {
                        "id": "quote_variant",
                        "name": "Formato Citação",
                        "description": "Posts em formato de citação inspiradora",
                        "config": {"force_format": "quote"},
                        "weight": 1.0
                    },
                    {
                        "id": "tip_variant", 
                        "name": "Formato Dica",
                        "description": "Posts com dicas práticas numeradas",
                        "config": {"force_format": "tip"},
                        "weight": 1.0
                    },
                    {
                        "id": "question_variant",
                        "name": "Formato Pergunta",
                        "description": "Posts focados em engajamento com perguntas",
                        "config": {"force_format": "question"},
                        "weight": 1.0
                    }
                ]
            },
            {
                "id": "hashtag_strategy_test",
                "name": "Teste de Estratégias de Hashtag",
                "description": "Compara diferentes abordagens de hashtags",
                "variants": [
                    {
                        "id": "trending_hashtags",
                        "name": "Hashtags Trending",
                        "description": "Foco em hashtags populares e sazonais",
                        "config": {"hashtag_strategy": "trending"},
                        "weight": 1.0
                    },
                    {
                        "id": "niche_hashtags",
                        "name": "Hashtags Nicho",
                        "description": "Foco em hashtags específicas do nicho",
                        "config": {"hashtag_strategy": "niche"},
                        "weight": 1.0
                    }
                ]
            },
            {
                "id": "image_style_test",
                "name": "Teste de Estilos de Imagem",
                "description": "Compara diferentes estilos visuais",
                "variants": [
                    {
                        "id": "minimalist_style",
                        "name": "Estilo Minimalista",
                        "description": "Imagens limpas e minimalistas",
                        "config": {"image_style": "minimalist"},
                        "weight": 1.0
                    },
                    {
                        "id": "dynamic_style",
                        "name": "Estilo Dinâmico",
                        "description": "Imagens com elementos dinâmicos e movimento",
                        "config": {"image_style": "dynamic"},
                        "weight": 1.0
                    }
                ]
            }
        ]
        
        for test_data in default_tests:
            if not self.get_test(test_data["id"]):
                self.create_test(
                    test_id=test_data["id"],
                    name=test_data["name"],
                    description=test_data["description"],
                    variants=test_data["variants"]
                )
    
    def create_test(self, test_id: str, name: str, description: str, 
                   variants: List[Dict], target_metric: str = "engagement_rate",
                   minimum_sample_size: int = 20) -> bool:
        """Cria um novo teste A/B."""
        try:
            test = ABTest(
                id=test_id,
                name=name,
                description=description,
                variants=[ABTestVariant(**v) for v in variants],
                start_date=datetime.now(),
                target_metric=target_metric,
                minimum_sample_size=minimum_sample_size
            )
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO ab_tests 
                    (id, name, description, variants, start_date, target_metric, minimum_sample_size)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    test.id, test.name, test.description,
                    json.dumps([v.__dict__ for v in test.variants]),
                    test.start_date.isoformat(),
                    test.target_metric, test.minimum_sample_size
                ))
            
            print(f"Teste A/B '{name}' criado com sucesso.")
            return True
        except Exception as e:
            print(f"Erro ao criar teste A/B: {e}")
            return False
    
    def get_test(self, test_id: str) -> Optional[ABTest]:
        """Recupera um teste A/B pelo ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT * FROM ab_tests WHERE id = ?", (test_id,)
                )
                row = cursor.fetchone()
                if not row:
                    return None
                
                variants_data = json.loads(row[3])
                variants = [ABTestVariant(**v) for v in variants_data]
                
                return ABTest(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    variants=variants,
                    start_date=datetime.fromisoformat(row[4]),
                    end_date=datetime.fromisoformat(row[5]) if row[5] else None,
                    status=row[6],
                    target_metric=row[7],
                    minimum_sample_size=row[8]
                )
        except Exception as e:
            print(f"Erro ao recuperar teste A/B: {e}")
            return None
    
    def assign_variant(self, test_id: str, account_name: str, post_id: str) -> Optional[ABTestVariant]:
        """Atribui uma variante para um post específico."""
        test = self.get_test(test_id)
        if not test or test.status != "active":
            return None
        
        try:
            # Distribuição baseada nos pesos das variantes
            variants = test.variants
            weights = [v.weight for v in variants]
            chosen_variant = random.choices(variants, weights=weights)[0]
            
            # Registrar atribuição
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO ab_test_assignments 
                    (test_id, variant_id, post_id, account_name)
                    VALUES (?, ?, ?, ?)
                """, (test_id, chosen_variant.id, post_id, account_name))
            
            return chosen_variant
        except Exception as e:
            print(f"Erro ao atribuir variante: {e}")
            return None
    
    def record_result(self, test_id: str, variant_id: str, post_id: str, 
                     metric_name: str, metric_value: float) -> bool:
        """Registra resultado de uma métrica para um teste."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO ab_test_results 
                    (test_id, variant_id, post_id, metric_name, metric_value)
                    VALUES (?, ?, ?, ?, ?)
                """, (test_id, variant_id, post_id, metric_name, metric_value))
            return True
        except Exception as e:
            print(f"Erro ao registrar resultado: {e}")
            return False
    
    def get_test_results(self, test_id: str) -> Dict:
        """Analisa resultados de um teste A/B."""
        test = self.get_test(test_id)
        if not test:
            return {}
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Estatísticas por variante
                cursor = conn.execute("""
                    SELECT 
                        variant_id,
                        COUNT(DISTINCT post_id) as sample_size,
                        AVG(metric_value) as avg_metric,
                        MIN(metric_value) as min_metric,
                        MAX(metric_value) as max_metric
                    FROM ab_test_results 
                    WHERE test_id = ? AND metric_name = ?
                    GROUP BY variant_id
                """, (test_id, test.target_metric))
                
                results = {}
                for row in cursor.fetchall():
                    variant_id = row[0]
                    variant = next((v for v in test.variants if v.id == variant_id), None)
                    
                    results[variant_id] = {
                        "variant_name": variant.name if variant else variant_id,
                        "sample_size": row[1],
                        "avg_metric": round(row[2], 2) if row[2] else 0,
                        "min_metric": round(row[3], 2) if row[3] else 0,
                        "max_metric": round(row[4], 2) if row[4] else 0,
                        "has_sufficient_data": row[1] >= test.minimum_sample_size
                    }
                
                # Determinar vencedor
                winner = None
                if results:
                    sufficient_data_variants = {
                        k: v for k, v in results.items() 
                        if v["has_sufficient_data"]
                    }
                    
                    if sufficient_data_variants:
                        winner = max(
                            sufficient_data_variants.items(),
                            key=lambda x: x[1]["avg_metric"]
                        )[0]
                
                return {
                    "test_name": test.name,
                    "target_metric": test.target_metric,
                    "status": test.status,
                    "variants": results,
                    "winner": winner,
                    "has_conclusive_results": winner is not None
                }
                
        except Exception as e:
            print(f"Erro ao analisar resultados: {e}")
            return {}
    
    def get_active_tests(self) -> List[ABTest]:
        """Retorna lista de testes ativos."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT id FROM ab_tests WHERE status = 'active'"
                )
                test_ids = [row[0] for row in cursor.fetchall()]
                
                return [self.get_test(test_id) for test_id in test_ids if self.get_test(test_id)]
        except Exception as e:
            print(f"Erro ao buscar testes ativos: {e}")
            return []
    
    def get_optimization_config(self, account_name: str, post_id: str) -> Dict:
        """
        Retorna configuração otimizada baseada em testes A/B ativos.
        
        Args:
            account_name: Nome da conta
            post_id: ID do post (pode ser temporário)
        
        Returns:
            Dict com configurações para aplicar ao post
        """
        config = {}
        active_tests = self.get_active_tests()
        
        for test in active_tests:
            variant = self.assign_variant(test.id, account_name, post_id)
            if variant:
                config.update(variant.config)
                print(f"Teste A/B '{test.name}': usando variante '{variant.name}'")
        
        return config
    
    def complete_test(self, test_id: str) -> bool:
        """Marca um teste como completo."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE ab_tests 
                    SET status = 'completed', end_date = ?
                    WHERE id = ?
                """, (datetime.now().isoformat(), test_id))
            return True
        except Exception as e:
            print(f"Erro ao completar teste: {e}")
            return False
    
    def get_recommendations(self) -> List[str]:
        """Gera recomendações baseadas nos resultados dos testes."""
        recommendations = []
        active_tests = self.get_active_tests()
        
        for test in active_tests:
            results = self.get_test_results(test.id)
            
            if results.get("has_conclusive_results"):
                winner_id = results["winner"]
                winner_data = results["variants"][winner_id]
                
                recommendations.append(
                    f"🏆 Teste '{test.name}': Variante '{winner_data['variant_name']}' "
                    f"tem melhor performance ({winner_data['avg_metric']}% {test.target_metric}). "
                    f"Considere usar mais frequentemente."
                )
            else:
                total_samples = sum(
                    v["sample_size"] for v in results.get("variants", {}).values()
                )
                needed_samples = test.minimum_sample_size * len(test.variants)
                
                if total_samples < needed_samples:
                    recommendations.append(
                        f"📊 Teste '{test.name}': Precisa de mais dados "
                        f"({total_samples}/{needed_samples} amostras). Continue testando."
                    )
        
        if not recommendations:
            recommendations.append(
                "🔬 Nenhum teste A/B ativo com resultados conclusivos. "
                "Continue postando para gerar dados."
            )
        
        return recommendations


# Função utilitária para integração
def get_ab_test_config(account_name: str, post_id: str = None) -> Dict:
    """
    Função utilitária para obter configuração de A/B testing.
    
    Args:
        account_name: Nome da conta
        post_id: ID do post (opcional, será gerado se não fornecido)
    
    Returns:
        Dict com configurações de A/B testing
    """
    if not post_id:
        post_id = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    framework = ABTestingFramework()
    return framework.get_optimization_config(account_name, post_id)