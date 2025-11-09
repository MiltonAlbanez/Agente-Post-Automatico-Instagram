#!/usr/bin/env python3
"""
Script de demonstração e teste do Framework de A/B Testing.
"""
import sys
import os
from pathlib import Path

# Adicionar o diretório src ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from services.ab_testing_framework import ABTestingFramework, get_ab_test_config
from services.performance_tracker import PerformanceTracker
import random
from datetime import datetime


def demo_ab_testing():
    """Demonstra o funcionamento do framework de A/B testing."""
    print("🧪 DEMONSTRAÇÃO DO FRAMEWORK DE A/B TESTING")
    print("=" * 50)
    
    # Inicializar framework
    framework = ABTestingFramework()
    
    # Mostrar testes ativos
    print("\n📊 TESTES A/B ATIVOS:")
    active_tests = framework.get_active_tests()
    for test in active_tests:
        print(f"- {test.name}: {len(test.variants)} variantes")
    
    # Simular atribuições de variantes
    print("\n🎯 SIMULANDO ATRIBUIÇÕES DE VARIANTES:")
    account_name = "Milton_Albanez"
    
    for i in range(5):
        post_id = f"demo_post_{i+1}"
        config = get_ab_test_config(account_name, post_id)
        print(f"Post {i+1}: {config}")
    
    # Simular resultados de performance
    print("\n📈 SIMULANDO RESULTADOS DE PERFORMANCE:")
    performance_tracker = PerformanceTracker()
    
    # Simular dados para diferentes variantes
    test_data = [
        {"variant": "quote_variant", "engagement": 4.2},
        {"variant": "tip_variant", "engagement": 5.8},
        {"variant": "question_variant", "engagement": 3.9},
        {"variant": "trending_hashtags", "engagement": 4.5},
        {"variant": "niche_hashtags", "engagement": 5.2},
        {"variant": "minimalist_style", "engagement": 4.8},
        {"variant": "dynamic_style", "engagement": 5.1},
    ]
    
    for i, data in enumerate(test_data * 3):  # Multiplicar para ter mais amostras
        post_id = f"test_post_{i+1}"
        
        # Registrar post no performance tracker
        post_data = {
            'post_id': post_id,
            'account_name': account_name,
            'content_format': "test_format",
            'hashtags': ["#test"],
            'image_style': "test_style"
        }
        performance_tracker.log_post(post_data)
        
        # Simular engajamento com variação
        engagement_rate = data["engagement"] + random.uniform(-0.5, 0.5)
        performance_tracker.update_metrics(post_id, {
            "likes": int(engagement_rate * 20),
            "comments": int(engagement_rate * 3),
            "shares": int(engagement_rate * 1)
        })
        
        # Registrar resultado no A/B testing
        if "variant" in data["variant"]:
            test_id = "content_format_test"
        elif "hashtags" in data["variant"]:
            test_id = "hashtag_strategy_test"
        else:
            test_id = "image_style_test"
            
        framework.record_result(
            test_id=test_id,
            variant_id=data["variant"],
            post_id=post_id,
            metric_name="engagement_rate",
            metric_value=engagement_rate
        )
    
    # Analisar resultados
    print("\n🏆 RESULTADOS DOS TESTES A/B:")
    for test in active_tests:
        results = framework.get_test_results(test.id)
        print(f"\n📋 {results.get('test_name', test.name)}:")
        
        if results.get('variants'):
            for variant_id, data in results['variants'].items():
                status = "✅ Dados suficientes" if data['has_sufficient_data'] else "⏳ Mais dados necessários"
                print(f"  - {data['variant_name']}: {data['avg_metric']}% ({status})")
        
        if results.get('winner'):
            winner_data = results['variants'][results['winner']]
            print(f"  🥇 Vencedor: {winner_data['variant_name']} ({winner_data['avg_metric']}%)")
    
    # Mostrar recomendações
    print("\n💡 RECOMENDAÇÕES:")
    recommendations = framework.get_recommendations()
    for rec in recommendations:
        print(f"  {rec}")
    
    print("\n✅ Demonstração concluída!")


def test_integration():
    """Testa a integração com o pipeline principal."""
    print("\n🔧 TESTANDO INTEGRAÇÃO COM PIPELINE:")
    print("=" * 40)
    
    account_name = "Milton_Albanez"
    
    # Testar múltiplas configurações
    for i in range(3):
        post_id = f"integration_test_{i+1}"
        config = get_ab_test_config(account_name, post_id)
        
        print(f"\nPost {i+1}:")
        print(f"  Configurações A/B: {config}")
        
        # Simular aplicação das configurações
        if config.get("force_format"):
            print(f"  ✓ Formato aplicado: {config['force_format']}")
        
        if config.get("hashtag_strategy"):
            print(f"  ✓ Estratégia de hashtag: {config['hashtag_strategy']}")
        
        if config.get("image_style"):
            print(f"  ✓ Estilo de imagem: {config['image_style']}")


if __name__ == "__main__":
    try:
        demo_ab_testing()
        test_integration()
        
        print("\n🎉 FRAMEWORK DE A/B TESTING FUNCIONANDO PERFEITAMENTE!")
        print("\nPróximos passos:")
        print("1. Execute posts reais para coletar dados")
        print("2. Monitore os resultados no dashboard")
        print("3. Ajuste estratégias baseado nos vencedores")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()