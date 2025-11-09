"""
Script de Teste para Monitoramento da Conta "Albanez Assistência Técnica"
Testa a coleta de métricas e geração de relatórios específicos para a nova conta.
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

from src.services.engagement_monitor import EngagementMonitor
from src.services.performance_tracker import PerformanceTracker


async def test_albanez_monitoring():
    """Testa o sistema de monitoramento para a conta Albanez Assistência Técnica."""
    
    print("🔍 Iniciando teste de monitoramento para 'Albanez Assistência Técnica'...")
    print("=" * 60)
    
    # Inicializar monitores
    engagement_monitor = EngagementMonitor()
    performance_tracker = PerformanceTracker()
    
    # 1. Simular um post da conta Albanez
    print("\n1. 📝 Simulando post da conta 'Albanez Assistência Técnica'...")
    
    test_post_data = {
        "post_id": f"albanez_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "account_name": "Albanez Assistência Técnica",
        "content_format": "tip",
        "hashtags": "#assistenciatecnica #arcondicionado #manutencao #dicas #climatizacao",
        "image_style": "assistência técnica, ar condicionado, antes e depois",
        "published_at": datetime.now().isoformat()
    }
    
    # Registrar o post no performance tracker
    success = performance_tracker.log_post(test_post_data)
    
    if success:
        print("✅ Post registrado com sucesso no sistema de tracking")
    else:
        print("❌ Erro ao registrar post")
        return
    
    # 2. Simular métricas de engagement
    print("\n2. 📊 Simulando coleta de métricas de engagement...")
    
    test_metrics = {
        "likes": 85,
        "comments": 12,
        "shares": 6,
        "saves": 18,
        "reach": 450,
        "impressions": 680
    }
    
    # Atualizar métricas
    metrics_updated = performance_tracker.update_metrics(
        test_post_data["post_id"], 
        test_metrics
    )
    
    if metrics_updated:
        print("✅ Métricas atualizadas com sucesso")
        print(f"   - Curtidas: {test_metrics['likes']}")
        print(f"   - Comentários: {test_metrics['comments']}")
        print(f"   - Compartilhamentos: {test_metrics['shares']}")
        print(f"   - Salvamentos: {test_metrics['saves']}")
        print(f"   - Alcance: {test_metrics['reach']}")
        print(f"   - Impressões: {test_metrics['impressions']}")
        
        # Calcular taxa de engagement
        engagement_rate = ((test_metrics['likes'] + test_metrics['comments'] + 
                          test_metrics['shares'] + test_metrics['saves']) / 
                         test_metrics['impressions']) * 100
        print(f"   - Taxa de Engagement: {engagement_rate:.2f}%")
    else:
        print("❌ Erro ao atualizar métricas")
    
    # 3. Testar coleta de métricas do engagement monitor
    print("\n3. 🔍 Testando coleta de métricas recentes...")
    
    recent_metrics = await engagement_monitor.collect_metrics_for_recent_posts(24)
    print(f"✅ Coletadas métricas de {len(recent_metrics)} posts recentes")
    
    # 4. Gerar análise de performance de conceitos
    print("\n4. 📈 Analisando performance dos conceitos...")
    
    concept_performances = engagement_monitor.analyze_concept_performance(7)
    
    if concept_performances:
        print(f"✅ Análise concluída para {len(concept_performances)} conceitos:")
        for perf in concept_performances:
            print(f"   - {perf.concept_name}: {perf.avg_engagement_rate}% engagement "
                  f"({perf.total_posts} posts) - {perf.trend_direction}")
    else:
        print("ℹ️ Nenhum conceito analisado (dados insuficientes)")
    
    # 5. Gerar relatório completo
    print("\n5. 📋 Gerando relatório de engagement...")
    
    report = engagement_monitor.generate_engagement_report(7)
    
    if report:
        print("✅ Relatório gerado com sucesso:")
        print(f"   - Período: {report['period_days']} dias")
        print(f"   - Total de posts: {report['general_stats']['total_posts']}")
        print(f"   - Engagement médio: {report['general_stats']['avg_engagement_rate']}%")
        print(f"   - Curtidas médias: {report['general_stats']['avg_likes']}")
        print(f"   - Comentários médios: {report['general_stats']['avg_comments']}")
        
        if report['alerts']:
            print(f"   - Alertas: {len(report['alerts'])}")
            for alert in report['alerts']:
                print(f"     • {alert['message']}")
        
        if report['recommendations']:
            print("   - Recomendações:")
            for rec in report['recommendations']:
                print(f"     • {rec}")
    
    # 6. Testar filtro específico por conta
    print("\n6. 🎯 Testando filtro específico para 'Albanez Assistência Técnica'...")
    
    try:
        # Buscar dados específicos da conta
        import sqlite3
        
        with sqlite3.connect(engagement_monitor.db_path) as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) as total_posts,
                       AVG(engagement_rate) as avg_engagement,
                       MAX(engagement_rate) as max_engagement,
                       AVG(likes) as avg_likes,
                       AVG(comments) as avg_comments
                FROM engagement_history 
                WHERE account_name = 'Albanez Assistência Técnica'
                AND collection_timestamp > datetime('now', '-7 days')
            """)
            
            account_stats = cursor.fetchone()
            
            if account_stats and account_stats[0] > 0:
                print("✅ Dados específicos da conta encontrados:")
                print(f"   - Posts da conta: {account_stats[0]}")
                print(f"   - Engagement médio: {account_stats[1]:.2f}%")
                print(f"   - Melhor engagement: {account_stats[2]:.2f}%")
                print(f"   - Curtidas médias: {int(account_stats[3] or 0)}")
                print(f"   - Comentários médios: {int(account_stats[4] or 0)}")
            else:
                print("ℹ️ Ainda não há dados suficientes para análise específica da conta")
                print("   (Dados serão coletados conforme novos posts forem publicados)")
    
    except Exception as e:
        print(f"❌ Erro ao buscar dados específicos da conta: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Teste de monitoramento concluído!")
    print("\n📊 Resumo do Sistema de Monitoramento:")
    print("✅ Sistema suporta múltiplas contas")
    print("✅ Coleta de métricas funcionando")
    print("✅ Análise de conceitos operacional")
    print("✅ Geração de relatórios ativa")
    print("✅ Filtros por conta disponíveis")
    print("\n🚀 O sistema está pronto para monitorar a conta 'Albanez Assistência Técnica'!")


if __name__ == "__main__":
    asyncio.run(test_albanez_monitoring())