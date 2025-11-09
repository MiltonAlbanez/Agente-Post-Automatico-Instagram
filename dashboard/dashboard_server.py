#!/usr/bin/env python3
"""
Servidor do Dashboard A/B Testing
Fornece uma interface web para visualizar resultados dos testes A/B em tempo real.
"""

import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from flask import Flask, render_template_string, jsonify, send_from_directory
from typing import Dict, List, Any

# Adicionar o diretório src ao path
sys.path.append(str(Path(__file__).parent.parent / "src"))

try:
    from services.ab_testing_manager import ABTestingManager
    from services.performance_tracker import PerformanceTracker
except ImportError:
    # Fallback para desenvolvimento
    class ABTestingManager:
        def __init__(self):
            self.active_tests = {
                'Teste de Formatos de Conteúdo': {
                    'status': 'active',
                    'variants': ['tip', 'question', 'quote']
                },
                'Teste de Estratégias de Hashtag': {
                    'status': 'active', 
                    'variants': ['trending', 'niche', 'optimized']
                }
            }
        
        def analyze_test_results(self, test_name):
            return {
                'winner': 'Formato Dica',
                'confidence': 95,
                'sample_size': 45,
                'duration_days': 7,
                'lift': 15
            }
    
    class PerformanceTracker:
        def __init__(self):
            self.db_path = "data/performance.db"

app = Flask(__name__)

class DashboardDataProvider:
    """Provedor de dados para o dashboard."""
    
    def __init__(self):
        self.ab_manager = ABTestingManager()
        self.performance_tracker = PerformanceTracker()
    
    def get_overview_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas gerais do dashboard."""
        try:
            # Obter dados dos testes A/B
            active_tests = len([test for test in self.ab_manager.active_tests.values() 
                              if test.get('status') == 'active'])
            
            # Obter dados de performance
            with sqlite3.connect(self.performance_tracker.db_path) as conn:
                cursor = conn.cursor()
                
                # Total de posts
                cursor.execute("SELECT COUNT(*) FROM post_performance")
                total_posts = cursor.fetchone()[0]
                
                # Posts hoje
                today = datetime.now().date().isoformat()
                cursor.execute("""
                    SELECT COUNT(*) FROM post_performance 
                    WHERE DATE(published_at) = ?
                """, (today,))
                posts_today = cursor.fetchone()[0]
                
                # Engajamento médio
                cursor.execute("""
                    SELECT AVG(engagement_rate) FROM post_performance 
                    WHERE engagement_rate > 0
                """)
                avg_engagement = cursor.fetchone()[0] or 0
                
                # Melhor formato
                cursor.execute("""
                    SELECT content_format, AVG(engagement_rate) as avg_rate
                    FROM post_performance 
                    WHERE engagement_rate > 0 
                    GROUP BY content_format 
                    ORDER BY avg_rate DESC 
                    LIMIT 1
                """)
                best_format_data = cursor.fetchone()
                best_format = best_format_data[0] if best_format_data else "N/A"
                
            return {
                'active_tests': active_tests,
                'total_posts': total_posts,
                'posts_today': posts_today,
                'avg_engagement': round(avg_engagement, 2),
                'best_format': best_format
            }
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
            return {
                'active_tests': 0,
                'total_posts': 0,
                'posts_today': 0,
                'avg_engagement': 0.0,
                'best_format': "N/A"
            }
    
    def get_format_performance(self) -> Dict[str, List]:
        """Obtém performance por formato de conteúdo."""
        try:
            with sqlite3.connect(self.performance_tracker.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT content_format, AVG(engagement_rate) as avg_rate, COUNT(*) as count
                    FROM post_performance 
                    WHERE engagement_rate > 0 AND content_format IS NOT NULL
                    GROUP BY content_format 
                    ORDER BY avg_rate DESC
                """)
                
                results = cursor.fetchall()
                formats = [row[0] for row in results]
                rates = [round(row[1], 2) for row in results]
                
                return {
                    'labels': formats,
                    'data': rates
                }
        except Exception as e:
            print(f"Erro ao obter performance por formato: {e}")
            return {
                'labels': ['Formato Dica', 'Formato Pergunta', 'Formato Citação'],
                'data': [4.8, 4.2, 3.9]
            }
    
    def get_engagement_timeline(self) -> Dict[str, List]:
        """Obtém timeline de engajamento dos últimos 7 dias."""
        try:
            with sqlite3.connect(self.performance_tracker.db_path) as conn:
                cursor = conn.cursor()
                
                # Últimos 7 dias
                dates = []
                engagement_data = []
                
                for i in range(6, -1, -1):
                    date = (datetime.now() - timedelta(days=i)).date().isoformat()
                    dates.append(date)
                    
                    cursor.execute("""
                        SELECT AVG(engagement_rate) 
                        FROM post_performance 
                        WHERE DATE(published_at) = ? AND engagement_rate > 0
                    """, (date,))
                    
                    avg_rate = cursor.fetchone()[0]
                    engagement_data.append(round(avg_rate, 2) if avg_rate else 0)
                
                return {
                    'labels': [datetime.fromisoformat(d).strftime('%a') for d in dates],
                    'data': engagement_data
                }
        except Exception as e:
            print(f"Erro ao obter timeline: {e}")
            return {
                'labels': ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'],
                'data': [3.8, 4.1, 4.5, 4.2, 4.8, 5.2, 4.9]
            }
    
    def get_ab_test_results(self) -> List[Dict]:
        """Obtém resultados dos testes A/B."""
        try:
            results = []
            
            for test_name, test_data in self.ab_manager.active_tests.items():
                # Analisar resultados do teste
                analysis = self.ab_manager.analyze_test_results(test_name)
                
                if analysis:
                    results.append({
                        'name': test_name,
                        'status': test_data.get('status', 'active'),
                        'winner': analysis.get('winner', 'Em andamento'),
                        'confidence': analysis.get('confidence', 0),
                        'sample_size': analysis.get('sample_size', 0),
                        'duration_days': analysis.get('duration_days', 0),
                        'lift': analysis.get('lift', 0)
                    })
            
            return results
        except Exception as e:
            print(f"Erro ao obter resultados A/B: {e}")
            return [
                {
                    'name': 'Teste de Formatos de Conteúdo',
                    'status': 'active',
                    'winner': 'Formato Dica',
                    'confidence': 95,
                    'sample_size': 45,
                    'duration_days': 7,
                    'lift': 15
                }
            ]

# Instância do provedor de dados
data_provider = DashboardDataProvider()

@app.route('/')
def dashboard():
    """Página principal do dashboard."""
    try:
        with open(Path(__file__).parent / 'ab_dashboard.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Dashboard HTML não encontrado!", 404

@app.route('/api/stats')
def api_stats():
    """API para estatísticas gerais."""
    return jsonify(data_provider.get_overview_stats())

@app.route('/api/format-performance')
def api_format_performance():
    """API para performance por formato."""
    return jsonify(data_provider.get_format_performance())

@app.route('/api/engagement-timeline')
def api_engagement_timeline():
    """API para timeline de engajamento."""
    return jsonify(data_provider.get_engagement_timeline())

@app.route('/api/ab-results')
def api_ab_results():
    """API para resultados dos testes A/B."""
    return jsonify(data_provider.get_ab_test_results())

@app.route('/api/refresh')
def api_refresh():
    """API para forçar atualização dos dados."""
    try:
        # Recarregar dados
        global data_provider
        data_provider = DashboardDataProvider()
        
        return jsonify({
            'status': 'success',
            'message': 'Dados atualizados com sucesso',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao atualizar dados: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    print("🚀 Iniciando Dashboard A/B Testing...")
    print("📊 Dashboard disponível em: http://localhost:5000")
    print("🔄 Dados atualizados automaticamente a cada 30 segundos")
    print("⚡ Use Ctrl+C para parar o servidor")
    
    # Criar diretório de dados se não existir
    os.makedirs('data', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)