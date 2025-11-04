#!/usr/bin/env python3
"""
Sistema de Notificações para Alertas de Performance
Envia notificações via Telegram e email sobre métricas importantes
"""

import json
import smtplib
import requests
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Any
from pathlib import Path

from .engagement_monitor import EngagementMonitor
from .performance_tracker import PerformanceTracker

class NotificationManager:
    """
    Gerencia notificações automáticas sobre performance dos posts
    """
    
    def __init__(self, config_path: str = "config/notification_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.engagement_monitor = EngagementMonitor()
        self.performance_tracker = PerformanceTracker()
    
    def _load_config(self) -> Dict:
        """Carrega configurações de notificação"""
        default_config = {
            "telegram": {
                "enabled": True,
                "bot_token": "",
                "chat_id": "",
                "alerts": {
                    "low_engagement": True,
                    "high_performance": True,
                    "daily_summary": True,
                    "error_alerts": True
                }
            },
            "email": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "recipients": [],
                "alerts": {
                    "weekly_report": True,
                    "critical_alerts": True
                }
            },
            "thresholds": {
                "low_engagement_rate": 2.0,  # %
                "high_engagement_rate": 8.0,  # %
                "min_likes_threshold": 50,
                "error_count_threshold": 3
            },
            "schedule": {
                "daily_summary_time": "20:00",
                "weekly_report_day": "sunday",
                "check_interval_minutes": 30
            }
        }
        
        config_file = Path(self.config_path)
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                # Merge com configurações padrão
                default_config.update(loaded_config)
        else:
            # Criar arquivo de configuração padrão
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
        
        return default_config
    
    def send_telegram_message(self, message: str, account_name: str = None) -> bool:
        """Envia mensagem via Telegram"""
        if not self.config["telegram"]["enabled"]:
            return False
        
        bot_token = self.config["telegram"]["bot_token"]
        chat_id = self.config["telegram"]["chat_id"]
        
        if not bot_token or not chat_id:
            print("⚠️ Telegram não configurado - bot_token ou chat_id ausentes")
            return False
        
        try:
            # Adicionar emoji e formatação
            if account_name:
                formatted_message = f"📊 **{account_name}**\n\n{message}"
            else:
                formatted_message = f"🤖 **Sistema de Automação**\n\n{message}"
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": formatted_message,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao enviar mensagem Telegram: {e}")
            return False
    
    def send_email(self, subject: str, body: str, recipients: List[str] = None) -> bool:
        """Envia email"""
        if not self.config["email"]["enabled"]:
            return False
        
        email_config = self.config["email"]
        recipients = recipients or email_config["recipients"]
        
        if not recipients:
            print("⚠️ Email não configurado - nenhum destinatário")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = email_config["username"]
            msg['To'] = ", ".join(recipients)
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"])
            server.starttls()
            server.login(email_config["username"], email_config["password"])
            
            text = msg.as_string()
            server.sendmail(email_config["username"], recipients, text)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao enviar email: {e}")
            return False
    
    def check_low_engagement_alert(self, account_name: str) -> None:
        """Verifica e alerta sobre baixo engagement"""
        if not self.config["telegram"]["alerts"]["low_engagement"]:
            return
        
        try:
            # Buscar posts das últimas 24 horas
            report = self.engagement_monitor.generate_engagement_report(
                account_name=account_name,
                days_back=1
            )
            
            if not report or not hasattr(report, 'avg_engagement_rate'):
                return
            
            threshold = self.config["thresholds"]["low_engagement_rate"]
            
            if report.avg_engagement_rate < threshold:
                message = f"""
⚠️ **ALERTA: Baixo Engagement**

📉 Taxa de engagement: {report.avg_engagement_rate:.2f}%
🎯 Meta mínima: {threshold}%
📅 Período: Últimas 24 horas
📊 Posts analisados: {report.total_posts}

💡 **Sugestões:**
• Revisar horários de publicação
• Testar novos conceitos de conteúdo
• Verificar qualidade das hashtags
• Analisar performance dos concorrentes
"""
                
                self.send_telegram_message(message, account_name)
                
        except Exception as e:
            print(f"❌ Erro ao verificar baixo engagement: {e}")
    
    def check_high_performance_alert(self, account_name: str) -> None:
        """Verifica e alerta sobre alta performance"""
        if not self.config["telegram"]["alerts"]["high_performance"]:
            return
        
        try:
            # Buscar posts das últimas 24 horas
            report = self.engagement_monitor.generate_engagement_report(
                account_name=account_name,
                days_back=1
            )
            
            if not report or not hasattr(report, 'avg_engagement_rate'):
                return
            
            threshold = self.config["thresholds"]["high_engagement_rate"]
            
            if report.avg_engagement_rate > threshold:
                message = f"""
🎉 **SUCESSO: Alta Performance!**

📈 Taxa de engagement: {report.avg_engagement_rate:.2f}%
🏆 Acima da meta: {threshold}%
📅 Período: Últimas 24 horas
📊 Posts analisados: {report.total_posts}

✨ **Continue assim:**
• Replique o formato dos posts de sucesso
• Mantenha os horários que funcionaram
• Use conceitos similares aos que performaram bem
"""
                
                self.send_telegram_message(message, account_name)
                
        except Exception as e:
            print(f"❌ Erro ao verificar alta performance: {e}")
    
    def send_daily_summary(self, account_name: str) -> None:
        """Envia resumo diário"""
        if not self.config["telegram"]["alerts"]["daily_summary"]:
            return
        
        try:
            report = self.engagement_monitor.generate_engagement_report(
                account_name=account_name,
                days_back=1
            )
            
            if not report:
                return
            
            # Calcular comparação com dia anterior
            yesterday_report = self.engagement_monitor.generate_engagement_report(
                account_name=account_name,
                days_back=2
            )
            
            engagement_trend = ""
            if yesterday_report and hasattr(yesterday_report, 'avg_engagement_rate'):
                diff = report.avg_engagement_rate - yesterday_report.avg_engagement_rate
                if diff > 0:
                    engagement_trend = f"📈 +{diff:.1f}% vs ontem"
                elif diff < 0:
                    engagement_trend = f"📉 {diff:.1f}% vs ontem"
                else:
                    engagement_trend = "➡️ Estável vs ontem"
            
            message = f"""
📊 **Resumo Diário - {datetime.now().strftime('%d/%m/%Y')}**

📈 **Métricas do Dia:**
• Engagement: {report.avg_engagement_rate:.2f}% {engagement_trend}
• Curtidas médias: {report.avg_likes:.0f}
• Comentários médios: {report.avg_comments:.0f}
• Posts publicados: {report.total_posts}

🎯 **Próximas Ações:**
• Continuar monitoramento
• Otimizar baseado nos resultados
• Preparar conteúdo para amanhã
"""
            
            self.send_telegram_message(message, account_name)
            
        except Exception as e:
            print(f"❌ Erro ao enviar resumo diário: {e}")
    
    def send_error_alert(self, error_message: str, account_name: str = None) -> None:
        """Envia alerta de erro"""
        if not self.config["telegram"]["alerts"]["error_alerts"]:
            return
        
        message = f"""
🚨 **ERRO NO SISTEMA**

⚠️ **Detalhes:**
{error_message}

🕐 **Horário:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

🔧 **Ação Necessária:**
Verificar logs e corrigir o problema
"""
        
        self.send_telegram_message(message, account_name)
    
    def check_all_alerts(self, account_name: str) -> None:
        """Executa todas as verificações de alerta para uma conta"""
        try:
            self.check_low_engagement_alert(account_name)
            self.check_high_performance_alert(account_name)
            
        except Exception as e:
            self.send_error_alert(f"Erro ao verificar alertas: {str(e)}", account_name)
    
    def send_weekly_report(self, account_name: str) -> None:
        """Envia relatório semanal por email"""
        if not self.config["email"]["alerts"]["weekly_report"]:
            return
        
        try:
            report = self.engagement_monitor.generate_engagement_report(
                account_name=account_name,
                days_back=7
            )
            
            if not report:
                return
            
            html_body = f"""
            <html>
            <body>
                <h2>📊 Relatório Semanal - {account_name}</h2>
                <p><strong>Período:</strong> {(datetime.now() - timedelta(days=7)).strftime('%d/%m/%Y')} - {datetime.now().strftime('%d/%m/%Y')}</p>
                
                <h3>📈 Métricas Gerais</h3>
                <ul>
                    <li><strong>Taxa de Engagement:</strong> {report.avg_engagement_rate:.2f}%</li>
                    <li><strong>Curtidas Médias:</strong> {report.avg_likes:.0f}</li>
                    <li><strong>Comentários Médios:</strong> {report.avg_comments:.0f}</li>
                    <li><strong>Total de Posts:</strong> {report.total_posts}</li>
                </ul>
                
                <h3>🎯 Conceitos de Melhor Performance</h3>
                <p>Análise detalhada dos conceitos que mais engajaram na semana.</p>
                
                <p><em>Relatório gerado automaticamente em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</em></p>
            </body>
            </html>
            """
            
            subject = f"📊 Relatório Semanal - {account_name} - {datetime.now().strftime('%d/%m/%Y')}"
            self.send_email(subject, html_body)
            
        except Exception as e:
            print(f"❌ Erro ao enviar relatório semanal: {e}")

if __name__ == "__main__":
    # Teste do sistema de notificações
    notification_manager = NotificationManager()
    
    # Teste para Albanez Assistência Técnica
    account_name = "Albanez Assistência Técnica"
    
    print("🔔 Testando sistema de notificações...")
    
    # Teste de resumo diário
    notification_manager.send_daily_summary(account_name)
    
    # Teste de verificação de alertas
    notification_manager.check_all_alerts(account_name)
    
    print("✅ Teste de notificações concluído!")