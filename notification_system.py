#!/usr/bin/env python3
"""
Sistema de Notificações para LTM
Envia alertas críticos via Telegram e logs
"""

import os
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class NotificationSystem:
    def __init__(self):
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.setup_logging()
        
        # Cache para evitar spam de notificações
        self.notification_cache = {}
        self.cache_duration = 3600  # 1 hora
        
        # Configurações de alertas
        self.alert_thresholds = {
            "cpu_critical": 90,
            "memory_critical": 90,
            "disk_critical": 95,
            "consecutive_failures": 3,
            "inactive_hours": 2
        }
        
    def setup_logging(self):
        """Configurar logging para notificações"""
        self.logger = logging.getLogger(__name__)
        
    def is_telegram_configured(self) -> bool:
        """Verificar se o Telegram está configurado"""
        return bool(self.telegram_bot_token and self.telegram_chat_id)
    
    def send_telegram_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """Enviar mensagem via Telegram"""
        if not self.is_telegram_configured():
            self.logger.warning("Telegram não configurado - mensagem não enviada")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            payload = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": parse_mode,
                "disable_web_page_preview": True
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            self.logger.info("✅ Mensagem Telegram enviada com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao enviar mensagem Telegram: {e}")
            return False
    
    def should_send_notification(self, alert_type: str) -> bool:
        """Verificar se deve enviar notificação (evitar spam)"""
        now = datetime.now()
        cache_key = f"{alert_type}_{now.strftime('%Y%m%d_%H')}"  # Cache por hora
        
        if cache_key in self.notification_cache:
            last_sent = self.notification_cache[cache_key]
            if (now - last_sent).total_seconds() < self.cache_duration:
                return False
        
        self.notification_cache[cache_key] = now
        
        # Limpar cache antigo
        cutoff_time = now - timedelta(hours=24)
        self.notification_cache = {
            k: v for k, v in self.notification_cache.items() 
            if v > cutoff_time
        }
        
        return True
    
    def send_system_alert(self, alert_type: str, message: str, details: Dict = None):
        """Enviar alerta do sistema"""
        if not self.should_send_notification(alert_type):
            self.logger.debug(f"Alerta {alert_type} suprimido (cache)")
            return
        
        # Log local
        self.logger.warning(f"🚨 ALERTA {alert_type.upper()}: {message}")
        
        # Preparar mensagem para Telegram
        telegram_message = f"""
🚨 <b>ALERTA LTM - {alert_type.upper()}</b>

📅 <b>Data/Hora:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
⚠️ <b>Mensagem:</b> {message}
"""
        
        if details:
            telegram_message += "\n📊 <b>Detalhes:</b>\n"
            for key, value in details.items():
                telegram_message += f"• {key}: {value}\n"
        
        telegram_message += f"\n🔗 <b>Sistema:</b> LTM Instagram Automation"
        
        # Enviar via Telegram
        self.send_telegram_message(telegram_message)
    
    def check_system_health(self, system_metrics: Dict) -> List[str]:
        """Verificar saúde do sistema e retornar alertas"""
        alerts = []
        
        try:
            # Verificar CPU
            cpu_percent = system_metrics.get("cpu", {}).get("percent", 0)
            if cpu_percent > self.alert_thresholds["cpu_critical"]:
                alerts.append(f"CPU crítica: {cpu_percent:.1f}%")
            
            # Verificar Memória
            memory_percent = system_metrics.get("memory", {}).get("percent", 0)
            if memory_percent > self.alert_thresholds["memory_critical"]:
                alerts.append(f"Memória crítica: {memory_percent:.1f}%")
            
            # Verificar Disco
            disk_percent = system_metrics.get("disk", {}).get("percent", 0)
            if disk_percent > self.alert_thresholds["disk_critical"]:
                alerts.append(f"Disco crítico: {disk_percent:.1f}%")
            
        except Exception as e:
            alerts.append(f"Erro ao verificar métricas: {e}")
        
        return alerts
    
    def check_execution_health(self, performance_summary: Dict) -> List[str]:
        """Verificar saúde das execuções"""
        alerts = []
        
        try:
            # Verificar taxa de sucesso
            success_rate = performance_summary.get("success_rate", 100)
            total_executions = performance_summary.get("total_executions", 0)
            
            # Só alertar se houver execuções suficientes e taxa muito baixa
            if total_executions >= 5 and success_rate < 20:
                alerts.append(f"Taxa de sucesso crítica: {success_rate:.1f}% ({total_executions} execuções)")
            elif total_executions >= 10 and success_rate < 40:
                alerts.append(f"Taxa de sucesso baixa: {success_rate:.1f}% ({total_executions} execuções)")
            
            # Verificar falhas consecutivas por operação
            operations_stats = performance_summary.get("operations_stats", {})
            for operation, stats in operations_stats.items():
                consecutive_failures = stats.get("count", 0) - stats.get("success", 0)
                if consecutive_failures >= self.alert_thresholds["consecutive_failures"] and stats.get("success", 0) == 0:
                    alerts.append(f"Operação {operation} falhando: {consecutive_failures} falhas consecutivas")
            
        except Exception as e:
            alerts.append(f"Erro ao verificar execuções: {e}")
        
        return alerts
    
    def send_startup_notification(self):
        """Enviar notificação de inicialização"""
        message = """
🚀 <b>LTM INICIADO</b>

📅 <b>Data/Hora:</b> {timestamp}
✅ <b>Status:</b> Sistema iniciado com sucesso
🔄 <b>Modo:</b> Agendamento automático 24/7
⚙️ <b>Ambiente:</b> {environment}

O sistema está operacional e pronto para executar as tarefas agendadas.
""".format(
            timestamp=datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            environment=os.environ.get("RAILWAY_ENVIRONMENT", "local")
        )
        
        self.send_telegram_message(message)
        self.logger.info("📱 Notificação de inicialização enviada")
    
    def send_daily_report(self, performance_summary: Dict):
        """Enviar relatório diário"""
        try:
            total_exec = performance_summary.get("total_executions", 0)
            success_rate = performance_summary.get("success_rate", 0)
            successful = performance_summary.get("successful_executions", 0)
            failed = performance_summary.get("failed_executions", 0)
            
            message = f"""
📊 <b>RELATÓRIO DIÁRIO LTM</b>

📅 <b>Data:</b> {datetime.now().strftime('%d/%m/%Y')}

📈 <b>Execuções (24h):</b>
• Total: {total_exec}
• Sucessos: {successful}
• Falhas: {failed}
• Taxa de sucesso: {success_rate:.1f}%

"""
            
            # Adicionar estatísticas por operação
            operations_stats = performance_summary.get("operations_stats", {})
            if operations_stats:
                message += "🔧 <b>Por Operação:</b>\n"
                for operation, stats in operations_stats.items():
                    message += f"• {operation}: {stats['success']}/{stats['count']} ({stats['success_rate']:.1f}%)\n"
            
            message += f"\n✅ Sistema operacional há {performance_summary.get('uptime_seconds', 0) / 3600:.1f} horas"
            
            self.send_telegram_message(message)
            self.logger.info("📊 Relatório diário enviado")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao enviar relatório diário: {e}")
    
    def monitor_and_alert(self, system_metrics: Dict, performance_summary: Dict):
        """Monitorar sistema e enviar alertas se necessário"""
        all_alerts = []
        
        # Verificar saúde do sistema
        system_alerts = self.check_system_health(system_metrics)
        all_alerts.extend(system_alerts)
        
        # Verificar saúde das execuções
        execution_alerts = self.check_execution_health(performance_summary)
        all_alerts.extend(execution_alerts)
        
        # Enviar alertas se houver
        if all_alerts:
            alert_message = "Problemas detectados no sistema"
            details = {f"Alerta {i+1}": alert for i, alert in enumerate(all_alerts)}
            self.send_system_alert("system_health", alert_message, details)

# Instância global do sistema de notificações
notification_system = NotificationSystem()

if __name__ == "__main__":
    # Teste do sistema de notificações
    notif = NotificationSystem()
    
    # Teste de alerta
    notif.send_system_alert(
        "test", 
        "Teste do sistema de notificações",
        {"cpu": "85%", "memory": "70%"}
    )
    
    # Teste de relatório
    test_summary = {
        "total_executions": 10,
        "successful_executions": 8,
        "failed_executions": 2,
        "success_rate": 80.0,
        "operations_stats": {
            "create_post": {"count": 5, "success": 4, "success_rate": 80.0},
            "create_stories": {"count": 5, "success": 4, "success_rate": 80.0}
        }
    }
    
    notif.send_daily_report(test_summary)