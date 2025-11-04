"""
Sistema de Otimização Automática de Performance
Ajusta automaticamente conceitos visuais e estratégias baseado na performance dos posts.
"""
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import statistics
from dataclasses import dataclass

from .engagement_monitor import EngagementMonitor, ConceptPerformance
from .superior_concept_manager import SuperiorConceptManager


@dataclass
class OptimizationAction:
    """Ação de otimização a ser executada."""
    action_type: str  # 'adjust_weight', 'disable_concept', 'boost_concept', 'modify_elements'
    concept_name: str
    current_value: float
    new_value: float
    reason: str
    confidence: float
    timestamp: str


@dataclass
class OptimizationReport:
    """Relatório de otimização executada."""
    optimization_date: str
    actions_taken: List[OptimizationAction]
    performance_before: Dict
    expected_improvement: Dict
    success_metrics: Dict


class PerformanceOptimizer:
    """Sistema de otimização automática baseado em performance."""
    
    def __init__(self, db_path: str = "data/performance_optimizer.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.engagement_monitor = EngagementMonitor()
        self.concept_manager = SuperiorConceptManager()
        self.config_path = Path("config/superior_concepts.json")
        self._init_database()
    
    def _init_database(self):
        """Inicializa banco de dados para otimização."""
        with sqlite3.connect(self.db_path) as conn:
            # Tabela para histórico de otimizações
            conn.execute("""
                CREATE TABLE IF NOT EXISTS optimization_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    optimization_date DATE,
                    concept_name TEXT,
                    action_type TEXT,
                    old_value REAL,
                    new_value REAL,
                    reason TEXT,
                    confidence REAL,
                    performance_before REAL,
                    performance_after REAL,
                    success_rate REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela para configurações dinâmicas
            conn.execute("""
                CREATE TABLE IF NOT EXISTS dynamic_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    config_key TEXT UNIQUE,
                    config_value TEXT,
                    last_updated TIMESTAMP,
                    auto_generated BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Tabela para métricas de sucesso
            conn.execute("""
                CREATE TABLE IF NOT EXISTS optimization_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_date DATE,
                    total_optimizations INTEGER,
                    successful_optimizations INTEGER,
                    avg_improvement_rate REAL,
                    best_performing_concept TEXT,
                    worst_performing_concept TEXT,
                    overall_engagement_trend TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    async def run_optimization_cycle(self, days_analysis: int = 7) -> OptimizationReport:
        """
        Executa um ciclo completo de otimização.
        
        Args:
            days_analysis: Quantos dias de dados analisar
        """
        print("🔄 Iniciando ciclo de otimização automática...")
        
        # 1. Coletar dados de performance
        print("📊 Coletando dados de performance...")
        await self.engagement_monitor.collect_metrics_for_recent_posts(days_analysis * 24)
        
        # 2. Analisar performance dos conceitos
        print("🔍 Analisando performance dos conceitos...")
        concept_performances = self.engagement_monitor.analyze_concept_performance(days_analysis)
        
        # 3. Identificar oportunidades de otimização
        print("💡 Identificando oportunidades de otimização...")
        optimization_actions = self._identify_optimization_opportunities(concept_performances)
        
        # 4. Executar otimizações
        print("⚡ Executando otimizações...")
        executed_actions = []
        for action in optimization_actions:
            if await self._execute_optimization_action(action):
                executed_actions.append(action)
        
        # 5. Gerar relatório
        print("📋 Gerando relatório de otimização...")
        report = self._generate_optimization_report(executed_actions, concept_performances)
        
        # 6. Salvar histórico
        self._save_optimization_history(executed_actions)
        
        print(f"✅ Otimização concluída! {len(executed_actions)} ações executadas.")
        return report
    
    def _identify_optimization_opportunities(self, performances: List[ConceptPerformance]) -> List[OptimizationAction]:
        """Identifica oportunidades de otimização baseado na performance."""
        actions = []
        
        if not performances:
            return actions
        
        # Carregar configuração atual
        current_config = self._load_current_config()
        current_weights = current_config.get("rotation_strategy", {}).get("weight_distribution", {})
        
        # Calcular performance média geral
        avg_engagement = statistics.mean([p.avg_engagement_rate for p in performances])
        
        for performance in performances:
            concept_name = performance.concept_name
            current_weight = current_weights.get(concept_name, 0.1)
            
            # Regra 1: Boost conceitos com alta performance
            if (performance.avg_engagement_rate > avg_engagement * 1.2 and 
                performance.trend_direction == "up" and 
                current_weight < 0.3):
                
                new_weight = min(current_weight * 1.3, 0.35)
                actions.append(OptimizationAction(
                    action_type="boost_concept",
                    concept_name=concept_name,
                    current_value=current_weight,
                    new_value=new_weight,
                    reason=f"Alta performance ({performance.avg_engagement_rate}%) com tendência crescente",
                    confidence=0.85,
                    timestamp=datetime.now().isoformat()
                ))
            
            # Regra 2: Reduzir peso de conceitos com baixa performance
            elif (performance.avg_engagement_rate < avg_engagement * 0.7 and 
                  performance.trend_direction == "down" and 
                  current_weight > 0.05):
                
                new_weight = max(current_weight * 0.7, 0.05)
                actions.append(OptimizationAction(
                    action_type="adjust_weight",
                    concept_name=concept_name,
                    current_value=current_weight,
                    new_value=new_weight,
                    reason=f"Baixa performance ({performance.avg_engagement_rate}%) com tendência decrescente",
                    confidence=0.75,
                    timestamp=datetime.now().isoformat()
                ))
            
            # Regra 3: Desabilitar temporariamente conceitos muito ruins
            elif (performance.avg_engagement_rate < avg_engagement * 0.5 and 
                  performance.total_posts >= 3):
                
                actions.append(OptimizationAction(
                    action_type="disable_concept",
                    concept_name=concept_name,
                    current_value=current_weight,
                    new_value=0.01,
                    reason=f"Performance muito baixa ({performance.avg_engagement_rate}%) - desabilitação temporária",
                    confidence=0.9,
                    timestamp=datetime.now().isoformat()
                ))
        
        # Regra 4: Rebalancear pesos para somar 1.0
        if actions:
            actions = self._rebalance_weights(actions, current_weights)
        
        return actions
    
    def _rebalance_weights(self, actions: List[OptimizationAction], current_weights: Dict) -> List[OptimizationAction]:
        """Rebalanceia os pesos para que a soma seja 1.0."""
        # Aplicar mudanças temporariamente para calcular novo total
        temp_weights = current_weights.copy()
        
        for action in actions:
            temp_weights[action.concept_name] = action.new_value
        
        # Calcular fator de normalização
        total_weight = sum(temp_weights.values())
        if total_weight == 0:
            return actions
        
        normalization_factor = 1.0 / total_weight
        
        # Ajustar todos os pesos proporcionalmente
        for action in actions:
            action.new_value *= normalization_factor
        
        return actions
    
    async def _execute_optimization_action(self, action: OptimizationAction) -> bool:
        """Executa uma ação de otimização específica."""
        try:
            if action.action_type in ["boost_concept", "adjust_weight", "disable_concept"]:
                return await self._update_concept_weight(action.concept_name, action.new_value)
            elif action.action_type == "modify_elements":
                return await self._modify_concept_elements(action.concept_name, action.new_value)
            
            return False
            
        except Exception as e:
            print(f"Erro ao executar ação {action.action_type}: {e}")
            return False
    
    async def _update_concept_weight(self, concept_name: str, new_weight: float) -> bool:
        """Atualiza o peso de um conceito na configuração."""
        try:
            # Carregar configuração atual
            config = self._load_current_config()
            
            # Atualizar peso
            if "rotation_strategy" not in config:
                config["rotation_strategy"] = {}
            if "weight_distribution" not in config["rotation_strategy"]:
                config["rotation_strategy"]["weight_distribution"] = {}
            
            config["rotation_strategy"]["weight_distribution"][concept_name] = round(new_weight, 3)
            
            # Salvar configuração
            return self._save_config(config)
            
        except Exception as e:
            print(f"Erro ao atualizar peso do conceito {concept_name}: {e}")
            return False
    
    async def _modify_concept_elements(self, concept_name: str, modification_value: float) -> bool:
        """Modifica elementos específicos de um conceito."""
        # Implementação futura para modificar elementos específicos
        # Por exemplo, ajustar paleta de cores, objetos, etc.
        return True
    
    def _load_current_config(self) -> Dict:
        """Carrega a configuração atual dos conceitos."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config.get("superior_visual_concepts", {})
        except Exception as e:
            print(f"Erro ao carregar configuração: {e}")
            return {}
    
    def _save_config(self, config: Dict) -> bool:
        """Salva a configuração atualizada."""
        try:
            # Carregar configuração completa
            with open(self.config_path, 'r', encoding='utf-8') as f:
                full_config = json.load(f)
            
            # Atualizar seção específica
            full_config["superior_visual_concepts"] = config
            
            # Salvar
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(full_config, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Erro ao salvar configuração: {e}")
            return False
    
    def _generate_optimization_report(self, actions: List[OptimizationAction], 
                                    performances: List[ConceptPerformance]) -> OptimizationReport:
        """Gera relatório detalhado da otimização."""
        
        # Calcular métricas antes da otimização
        performance_before = {
            "avg_engagement": statistics.mean([p.avg_engagement_rate for p in performances]) if performances else 0,
            "total_concepts": len(performances),
            "best_concept": performances[0].concept_name if performances else None,
            "worst_concept": performances[-1].concept_name if performances else None
        }
        
        # Estimar melhorias esperadas
        expected_improvement = {
            "engagement_boost": sum([0.1 for a in actions if a.action_type == "boost_concept"]),
            "weight_adjustments": len([a for a in actions if a.action_type == "adjust_weight"]),
            "concepts_optimized": len(set([a.concept_name for a in actions]))
        }
        
        # Métricas de sucesso
        success_metrics = {
            "actions_executed": len(actions),
            "high_confidence_actions": len([a for a in actions if a.confidence > 0.8]),
            "optimization_coverage": len(set([a.concept_name for a in actions])) / max(len(performances), 1)
        }
        
        return OptimizationReport(
            optimization_date=datetime.now().isoformat(),
            actions_taken=actions,
            performance_before=performance_before,
            expected_improvement=expected_improvement,
            success_metrics=success_metrics
        )
    
    def _save_optimization_history(self, actions: List[OptimizationAction]):
        """Salva histórico de otimizações no banco."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                for action in actions:
                    conn.execute("""
                        INSERT INTO optimization_history 
                        (optimization_date, concept_name, action_type, old_value, 
                         new_value, reason, confidence, performance_before)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        datetime.now().date().isoformat(),
                        action.concept_name,
                        action.action_type,
                        action.current_value,
                        action.new_value,
                        action.reason,
                        action.confidence,
                        0.0  # performance_before será atualizada posteriormente
                    ))
        except Exception as e:
            print(f"Erro ao salvar histórico: {e}")
    
    def get_optimization_insights(self, days_back: int = 30) -> Dict:
        """Gera insights sobre otimizações realizadas."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Estatísticas gerais
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_optimizations,
                        COUNT(DISTINCT concept_name) as concepts_optimized,
                        AVG(confidence) as avg_confidence,
                        COUNT(CASE WHEN action_type = 'boost_concept' THEN 1 END) as boosts,
                        COUNT(CASE WHEN action_type = 'adjust_weight' THEN 1 END) as adjustments,
                        COUNT(CASE WHEN action_type = 'disable_concept' THEN 1 END) as disables
                    FROM optimization_history 
                    WHERE optimization_date > date('now', '-{} days')
                """.format(days_back))
                
                stats = cursor.fetchone()
                
                # Conceitos mais otimizados
                cursor = conn.execute("""
                    SELECT concept_name, COUNT(*) as optimization_count
                    FROM optimization_history 
                    WHERE optimization_date > date('now', '-{} days')
                    GROUP BY concept_name
                    ORDER BY optimization_count DESC
                    LIMIT 5
                """.format(days_back))
                
                top_optimized = cursor.fetchall()
            
            return {
                "period_days": days_back,
                "total_optimizations": stats[0] or 0,
                "concepts_optimized": stats[1] or 0,
                "avg_confidence": round(stats[2] or 0, 2),
                "action_breakdown": {
                    "boosts": stats[3] or 0,
                    "adjustments": stats[4] or 0,
                    "disables": stats[5] or 0
                },
                "most_optimized_concepts": [
                    {"concept": row[0], "optimizations": row[1]} 
                    for row in top_optimized
                ],
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Erro ao gerar insights: {e}")
            return {}
    
    async def schedule_optimization(self, interval_hours: int = 24):
        """Agenda otimização automática em intervalos regulares."""
        import asyncio
        
        while True:
            try:
                print(f"⏰ Executando otimização automática agendada...")
                report = await self.run_optimization_cycle()
                
                print(f"✅ Otimização concluída: {len(report.actions_taken)} ações executadas")
                
                # Aguardar próximo ciclo
                await asyncio.sleep(interval_hours * 3600)
                
            except Exception as e:
                print(f"Erro na otimização agendada: {e}")
                await asyncio.sleep(3600)  # Tentar novamente em 1 hora


# Função utilitária para executar otimização
async def run_performance_optimization():
    """Executa otimização de performance."""
    optimizer = PerformanceOptimizer()
    report = await optimizer.run_optimization_cycle()
    
    print("\n📊 RELATÓRIO DE OTIMIZAÇÃO")
    print("=" * 50)
    print(f"Data: {report.optimization_date}")
    print(f"Ações executadas: {len(report.actions_taken)}")
    
    for action in report.actions_taken:
        print(f"\n🔧 {action.action_type.upper()}")
        print(f"   Conceito: {action.concept_name}")
        print(f"   Valor: {action.current_value:.3f} → {action.new_value:.3f}")
        print(f"   Razão: {action.reason}")
        print(f"   Confiança: {action.confidence:.1%}")
    
    return report


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_performance_optimization())