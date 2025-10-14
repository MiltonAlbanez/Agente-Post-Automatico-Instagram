"""
Dashboard de Automação para Sistema de Posts do Instagram
Interface para controlar e monitorar a automação
"""

import streamlit as st
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys
import plotly.express as px
import plotly.graph_objects as go

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from automation.scheduler import AutomationScheduler
from automation.consistency_manager import ConsistencyManager
from src.services.engagement_monitor import EngagementMonitor

class AutomationDashboard:
    def __init__(self):
        self.scheduler = AutomationScheduler()
        self.consistency_manager = ConsistencyManager()
        self.engagement_monitor = EngagementMonitor()
        
    def run_dashboard(self):
        """Executar dashboard principal"""
        st.set_page_config(
            page_title="Dashboard de Automação - Instagram Posts",
            page_icon="🤖",
            layout="wide"
        )
        
        st.title("🤖 Dashboard de Automação - Instagram Posts")
        st.markdown("---")
        
        # Sidebar para controles
        self.render_sidebar()
        
        # Conteúdo principal
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Visão Geral", 
            "⚙️ Configurações", 
            "📈 Performance", 
            "🔄 Consistência"
        ])
        
        with tab1:
            self.render_overview_tab()
            
        with tab2:
            self.render_settings_tab()
            
        with tab3:
            self.render_performance_tab()
            
        with tab4:
            self.render_consistency_tab()
            
    def render_sidebar(self):
        """Renderizar sidebar com controles"""
        st.sidebar.header("🎛️ Controles de Automação")
        
        # Status do sistema
        st.sidebar.subheader("Status do Sistema")
        
        if st.sidebar.button("▶️ Iniciar Automação"):
            st.sidebar.success("Automação iniciada!")
            
        if st.sidebar.button("⏸️ Pausar Automação"):
            st.sidebar.warning("Automação pausada!")
            
        if st.sidebar.button("🔄 Executar Ciclo Manual"):
            with st.spinner("Executando ciclo manual..."):
                self.scheduler.run_manual_cycle()
            st.sidebar.success("Ciclo manual concluído!")
            
        st.sidebar.markdown("---")
        
        # Ações rápidas
        st.sidebar.subheader("Ações Rápidas")
        
        if st.sidebar.button("📝 Criar Post Agora"):
            with st.spinner("Criando post..."):
                self.scheduler.create_scheduled_post()
            st.sidebar.success("Post criado!")
            
        if st.sidebar.button("🔍 Monitorar Engagement"):
            with st.spinner("Coletando dados..."):
                self.scheduler.monitor_engagement()
            st.sidebar.success("Monitoramento concluído!")
            
        if st.sidebar.button("⚡ Otimizar Conceitos"):
            with st.spinner("Otimizando..."):
                self.scheduler.run_optimization()
            st.sidebar.success("Otimização concluída!")
            
    def render_overview_tab(self):
        """Renderizar aba de visão geral"""
        st.header("📊 Visão Geral do Sistema")
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Posts Hoje",
                value="3",
                delta="0"
            )
            
        with col2:
            st.metric(
                label="Engagement Médio",
                value="4.2%",
                delta="0.3%"
            )
            
        with col3:
            st.metric(
                label="Qualidade Média",
                value="8.7/10",
                delta="0.2"
            )
            
        with col4:
            # Calcular próximo post baseado na configuração atual
            config = self.scheduler.config
            post_times = config["schedule"]["post_times"]
            current_time = datetime.now().time()
            
            # Encontrar próximo horário
            next_post = "20:00"  # Default para teste hoje
            for post_time in post_times:
                post_time_obj = datetime.strptime(post_time, "%H:%M").time()
                if post_time_obj > current_time:
                    next_post = post_time
                    break
            
            # Se passou de todos os horários de hoje, mostrar primeiro de amanhã
            if next_post == "20:00" and current_time > datetime.strptime("20:00", "%H:%M").time():
                next_post = post_times[0] + " (amanhã)"
            
            st.metric(
                label="Próximo Post",
                value=next_post,
                delta=None
            )
            
        st.markdown("---")
        
        # Gráfico de atividade
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📅 Atividade dos Últimos 7 Dias")
            
            # Dados simulados
            dates = pd.date_range(end=datetime.now(), periods=7)
            posts_data = pd.DataFrame({
                'Data': dates,
                'Posts': [3, 2, 3, 3, 1, 3, 2],
                'Engagement': [4.1, 3.8, 4.5, 4.2, 3.2, 4.7, 4.0]
            })
            
            fig = px.bar(posts_data, x='Data', y='Posts', 
                        title="Posts por Dia")
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.subheader("📈 Tendência de Engagement")
            
            fig = px.line(posts_data, x='Data', y='Engagement',
                         title="Engagement Rate (%)")
            st.plotly_chart(fig, use_container_width=True)
            
        # Status dos agendamentos
        st.subheader("⏰ Próximos Agendamentos")
        
        # Usar configuração atual do scheduler
        config = self.scheduler.config
        post_times = config["schedule"]["post_times"]
        optimization_time = config["schedule"]["optimization_time"]
        
        # Criar lista de agendamentos
        schedule_times = []
        schedule_actions = []
        schedule_status = []
        
        # Adicionar posts agendados
        for post_time in post_times:
            schedule_times.append(post_time)
            schedule_actions.append('Criar Post')
            schedule_status.append('Agendado')
        
        # Adicionar agendamento de teste às 20:00 (apenas para hoje)
        current_hour = datetime.now().hour
        if current_hour < 20:  # Só mostrar se ainda não passou das 20h
            schedule_times.append('20:00')
            schedule_actions.append('Post de Teste')
            schedule_status.append('Agendado')
        
        # Adicionar otimização
        schedule_times.append(optimization_time)
        schedule_actions.append('Otimização')
        schedule_status.append('Agendado')
        
        schedule_data = pd.DataFrame({
            'Horário': schedule_times,
            'Ação': schedule_actions,
            'Status': schedule_status
        })
        
        st.dataframe(schedule_data, use_container_width=True)
        
    def render_settings_tab(self):
        """Renderizar aba de configurações"""
        st.header("⚙️ Configurações de Automação")
        
        # Carregar configurações atuais
        config = self.scheduler.config
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📅 Agendamento")
            
            daily_posts = st.number_input(
                "Posts por dia",
                min_value=1,
                max_value=5,
                value=config["schedule"]["daily_posts"]
            )
            
            post_times = st.text_area(
                "Horários dos posts (um por linha)",
                value="\n".join(config["schedule"]["post_times"])
            )
            
            optimization_time = st.time_input(
                "Horário da otimização",
                value=datetime.strptime(config["schedule"]["optimization_time"], "%H:%M").time()
            )
            
            monitoring_interval = st.number_input(
                "Intervalo de monitoramento (minutos)",
                min_value=15,
                max_value=240,
                value=config["schedule"]["monitoring_interval"]
            )
            
        with col2:
            st.subheader("🎯 Conteúdo")
            
            auto_optimize = st.checkbox(
                "Otimização automática",
                value=config["content_settings"]["auto_optimize"]
            )
            
            use_trending = st.checkbox(
                "Usar conceitos em tendência",
                value=config["content_settings"]["use_trending_concepts"]
            )
            
            quality_threshold = st.slider(
                "Limite mínimo de qualidade",
                min_value=0.5,
                max_value=1.0,
                value=config["content_settings"]["maintain_quality_threshold"],
                step=0.1
            )
            
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🛡️ Segurança")
            
            max_daily = st.number_input(
                "Máximo de posts por dia",
                min_value=1,
                max_value=10,
                value=config["safety_settings"]["max_daily_posts"]
            )
            
            min_interval = st.number_input(
                "Intervalo mínimo entre posts (minutos)",
                min_value=30,
                max_value=480,
                value=config["safety_settings"]["min_interval_between_posts"]
            )
            
        with col2:
            st.subheader("🔔 Notificações")
            
            daily_summary = st.checkbox("Resumo diário", value=True)
            error_alerts = st.checkbox("Alertas de erro", value=True)
            performance_alerts = st.checkbox("Alertas de performance", value=True)
            
        # Botão para salvar configurações
        if st.button("💾 Salvar Configurações"):
            # Atualizar configurações
            new_config = config.copy()
            new_config["schedule"]["daily_posts"] = daily_posts
            new_config["schedule"]["post_times"] = post_times.split("\n")
            new_config["schedule"]["optimization_time"] = optimization_time.strftime("%H:%M")
            new_config["schedule"]["monitoring_interval"] = monitoring_interval
            new_config["content_settings"]["auto_optimize"] = auto_optimize
            new_config["content_settings"]["use_trending_concepts"] = use_trending
            new_config["content_settings"]["maintain_quality_threshold"] = quality_threshold
            new_config["safety_settings"]["max_daily_posts"] = max_daily
            new_config["safety_settings"]["min_interval_between_posts"] = min_interval
            
            # Salvar
            self.scheduler.config = new_config
            self.scheduler.save_config()
            
            st.success("Configurações salvas com sucesso!")
            
    def render_performance_tab(self):
        """Renderizar aba de performance"""
        st.header("📈 Análise de Performance")
        
        # Filtro por conta
        st.subheader("🎯 Filtros")
        col1, col2 = st.columns(2)
        
        with col1:
            # Carregar contas disponíveis
            try:
                with open('accounts.json', 'r', encoding='utf-8') as f:
                    accounts_data = json.load(f)
                account_names = list(accounts_data.keys())
                account_names.insert(0, "Todas as Contas")
            except:
                account_names = ["Todas as Contas", "Milton_Albanez", "Albanez Assistência Técnica"]
            
            selected_account = st.selectbox(
                "Selecionar Conta:",
                account_names,
                index=0
            )
        
        with col2:
            days_filter = st.selectbox(
                "Período:",
                [7, 14, 30],
                index=0,
                format_func=lambda x: f"Últimos {x} dias"
            )
        
        # Obter dados reais do engagement monitor
        try:
            if selected_account == "Todas as Contas":
                report = self.engagement_monitor.generate_engagement_report(days_filter)
            else:
                # Gerar relatório específico para a conta selecionada
                report = self._generate_account_specific_report(selected_account, days_filter)
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")
            report = {"general_stats": {"avg_engagement_rate": 0, "avg_likes": 0, "avg_comments": 0}}
        
        st.markdown("---")
        
        # Métricas de engagement
        col1, col2, col3 = st.columns(3)
        
        with col1:
            engagement_rate = report.get("general_stats", {}).get("avg_engagement_rate", 0)
            st.metric("Taxa de Engagement", f"{engagement_rate:.1f}%")
            
        with col2:
            avg_likes = report.get("general_stats", {}).get("avg_likes", 0)
            st.metric("Curtidas Médias", f"{avg_likes:.0f}")
            
        with col3:
            avg_comments = report.get("general_stats", {}).get("avg_comments", 0)
            st.metric("Comentários Médios", f"{avg_comments:.0f}")
            
        st.markdown("---")
        
        # Gráficos de performance
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Performance por Conceito")
            
            # Usar dados reais do relatório
            concept_performance = report.get("concept_performance", [])
            
            if concept_performance:
                concept_data = pd.DataFrame({
                    'Conceito': [cp['concept'] for cp in concept_performance],
                    'Engagement': [cp['engagement_rate'] for cp in concept_performance],
                    'Posts': [cp['posts'] for cp in concept_performance]
                })
                
                fig = px.scatter(concept_data, x='Posts', y='Engagement', 
                               size='Engagement', color='Conceito',
                               title=f"Engagement vs Quantidade de Posts{' - ' + selected_account if selected_account != 'Todas as Contas' else ''}")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Dados insuficientes para análise de conceitos no período selecionado.")
            
        with col2:
            st.subheader("⏰ Performance por Horário")
            
            time_data = pd.DataFrame({
                'Horário': ['09:00', '12:00', '14:00', '17:00', '19:00', '21:00'],
                'Engagement': [3.8, 3.2, 4.5, 4.8, 5.2, 4.1]
            })
            
            fig = px.bar(time_data, x='Horário', y='Engagement',
                        title="Engagement por Horário de Postagem")
            st.plotly_chart(fig, use_container_width=True)
            
        # Tabela de melhores posts
        st.subheader(f"🏆 Melhores Posts Recentes{' - ' + selected_account if selected_account != 'Todas as Contas' else ''}")
        
        # Buscar posts reais do banco de dados
        try:
            import sqlite3
            
            with sqlite3.connect(self.engagement_monitor.db_path) as conn:
                if selected_account == "Todas as Contas":
                    query = """
                        SELECT 
                            DATE(collection_timestamp) as data,
                            concept_used as conceito,
                            likes,
                            comments,
                            saves,
                            engagement_rate
                        FROM engagement_history 
                        WHERE collection_timestamp > datetime('now', '-{} days')
                        ORDER BY engagement_rate DESC
                        LIMIT 10
                    """.format(days_filter)
                    cursor = conn.execute(query)
                else:
                    query = """
                        SELECT 
                            DATE(collection_timestamp) as data,
                            concept_used as conceito,
                            likes,
                            comments,
                            saves,
                            engagement_rate
                        FROM engagement_history 
                        WHERE account_name = ?
                        AND collection_timestamp > datetime('now', '-{} days')
                        ORDER BY engagement_rate DESC
                        LIMIT 10
                    """.format(days_filter)
                    cursor = conn.execute(query, (selected_account,))
                
                posts_data = cursor.fetchall()
                
                if posts_data:
                    best_posts = pd.DataFrame(posts_data, columns=[
                        'Data', 'Conceito', 'Curtidas', 'Comentários', 'Salvamentos', 'Engagement'
                    ])
                    
                    # Formatar engagement como porcentagem
                    best_posts['Engagement'] = best_posts['Engagement'].apply(lambda x: f"{x:.1f}%")
                    
                    st.dataframe(best_posts, use_container_width=True)
                else:
                    st.info("Nenhum post encontrado no período selecionado.")
                    
        except Exception as e:
            st.error(f"Erro ao carregar dados dos posts: {e}")
            # Fallback para dados simulados
            best_posts = pd.DataFrame({
                'Data': ['Sem dados'],
                'Conceito': ['N/A'],
                'Curtidas': [0],
                'Comentários': [0],
                'Salvamentos': [0],
                'Engagement': ['0.0%']
            })
            st.dataframe(best_posts, use_container_width=True)
    
    def _generate_account_specific_report(self, account_name: str, days_back: int = 7):
        """Gera relatório específico para uma conta."""
        try:
            import sqlite3
            
            with sqlite3.connect(self.engagement_monitor.db_path) as conn:
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_posts,
                        AVG(engagement_rate) as avg_engagement,
                        MAX(engagement_rate) as max_engagement,
                        MIN(engagement_rate) as min_engagement,
                        AVG(likes) as avg_likes,
                        AVG(comments) as avg_comments
                    FROM engagement_history 
                    WHERE account_name = ?
                    AND collection_timestamp > datetime('now', '-{} days')
                """.format(days_back), (account_name,))
                
                account_stats = cursor.fetchone()
                
                # Buscar performance de conceitos para esta conta
                cursor = conn.execute("""
                    SELECT 
                        concept_used,
                        COUNT(*) as total_posts,
                        AVG(engagement_rate) as avg_engagement,
                        AVG(likes) as avg_likes,
                        AVG(comments) as avg_comments
                    FROM engagement_history 
                    WHERE account_name = ?
                    AND collection_timestamp > datetime('now', '-{} days')
                    AND concept_used IS NOT NULL
                    GROUP BY concept_used
                    ORDER BY avg_engagement DESC
                """.format(days_back), (account_name,))
                
                concept_data = cursor.fetchall()
                
                return {
                    "period_days": days_back,
                    "account_name": account_name,
                    "generated_at": datetime.now().isoformat(),
                    "general_stats": {
                        "total_posts": account_stats[0] or 0,
                        "avg_engagement_rate": round(account_stats[1] or 0, 2),
                        "max_engagement_rate": round(account_stats[2] or 0, 2),
                        "min_engagement_rate": round(account_stats[3] or 0, 2),
                        "avg_likes": int(account_stats[4] or 0),
                        "avg_comments": int(account_stats[5] or 0)
                    },
                    "concept_performance": [
                        {
                            "concept": concept[0],
                            "posts": concept[1],
                            "engagement_rate": round(concept[2], 2),
                            "likes": int(concept[3]),
                            "comments": int(concept[4])
                        }
                        for concept in concept_data
                    ]
                }
        except Exception as e:
            print(f"Erro ao gerar relatório específico da conta: {e}")
            return {
                "general_stats": {
                    "total_posts": 0,
                    "avg_engagement_rate": 0,
                    "avg_likes": 0,
                    "avg_comments": 0
                },
                "concept_performance": []
            }
        
    def render_consistency_tab(self):
        """Renderizar aba de consistência"""
        st.header("🔄 Análise de Consistência")
        
        # Obter relatório de consistência
        try:
            report = self.consistency_manager.get_consistency_report()
            
            if "error" not in report:
                # Métricas de consistência
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Qualidade Média",
                        f"{report['average_quality_score']}/10"
                    )
                    
                with col2:
                    st.metric(
                        "Diversidade de Conceitos",
                        f"{int(report['concept_diversity'] * 100)}%"
                    )
                    
                with col3:
                    st.metric(
                        "Total de Posts",
                        report['total_posts']
                    )
                    
                with col4:
                    st.metric(
                        "Tendência",
                        report['quality_trend'].title()
                    )
                    
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📊 Conceitos Mais Utilizados")
                    
                    if report['most_used_concepts']:
                        concepts_df = pd.DataFrame(report['most_used_concepts'])
                        fig = px.pie(concepts_df, values='count', names='concept',
                                   title="Distribuição de Conceitos")
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Dados insuficientes")
                        
                with col2:
                    st.subheader("💡 Recomendações")
                    
                    if report['recommendations']:
                        for rec in report['recommendations']:
                            st.write(f"• {rec}")
                    else:
                        st.success("Nenhuma recomendação no momento!")
                        
            else:
                st.warning(report['error'])
                
        except Exception as e:
            st.error(f"Erro ao carregar dados de consistência: {str(e)}")
            
        # Configurações de qualidade
        st.markdown("---")
        st.subheader("⚙️ Padrões de Qualidade")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Conteúdo:**")
            st.write("• Legenda: 50-2200 caracteres")
            st.write("• Hashtags: 5-30 tags")
            st.write("• Call-to-action obrigatório")
            
        with col2:
            st.write("**Visual:**")
            st.write("• Resolução mínima: 1080x1080")
            st.write("• Proporções: 1:1, 4:5, 9:16")
            st.write("• Harmonia de cores")

def main():
    dashboard = AutomationDashboard()
    dashboard.run_dashboard()

if __name__ == "__main__":
    main()