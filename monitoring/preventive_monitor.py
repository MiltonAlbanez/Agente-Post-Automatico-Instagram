#!/usr/bin/env python3
"""
Sistema de Monitoramento Preventivo
Detecta problemas automaticamente antes que afetem a produção
"""

import os
import json
import requests
import schedule
import time
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, List, Any
import sys

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring/preventive_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PreventiveMonitor:
    def __init__(self):
        self.alerts = []
        self.last_check = {}
        self.thresholds = {
            "api_response_time": 5.0,  # segundos
            "error_rate": 0.1,  # 10%
            "disk_usage": 0.85,  # 85%
            "memory_usage": 0.90  # 90%
        }
        
        # Carregar variáveis de ambiente
        self.load_environment()
        
    def load_environment(self):
        """Carrega variáveis de ambiente do .env"""
        try:
            env_file = Path(".env")
            if env_file.exists():
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '=' in line and not line.strip().startswith('#'):
                            key, value = line.strip().split('=', 1)
                            os.environ[key] = value.strip('"\'')
        except Exception as e:
            logger.error(f"Erro ao carregar .env: {e}")
    
    def check_telegram_health(self) -> Dict[str, Any]:
        """Monitora saúde da API do Telegram"""
        result = {
            "service": "telegram",
            "status": "unknown",
            "response_time": None,
            "error": None,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            token = os.getenv("TELEGRAM_BOT_TOKEN")
            if not token:
                result["status"] = "error"
                result["error"] = "Token não configurado"
                return result
            
            start_time = time.time()
            response = requests.get(
                f"https://api.telegram.org/bot{token}/getMe",
                timeout=10
            )
            response_time = time.time() - start_time
            
            result["response_time"] = response_time
            
            if response.status_code == 200:
                result["status"] = "healthy"
                if response_time > self.thresholds["api_response_time"]:
                    self.add_alert("telegram", "high_response_time", 
                                 f"Tempo de resposta alto: {response_time:.2f}s")
            else:
                result["status"] = "error"
                result["error"] = f"HTTP {response.status_code}"
                self.add_alert("telegram", "api_error", 
                             f"Erro na API: {response.status_code}")
                
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            self.add_alert("telegram", "connection_error", str(e))
        
        return result
    
    def check_instagram_health(self) -> Dict[str, Any]:
        """Monitora saúde da API do Instagram"""
        result = {
            "service": "instagram",
            "status": "unknown",
            "response_time": None,
            "error": None,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            account_id = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
            access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
            
            if not account_id or not access_token:
                result["status"] = "error"
                result["error"] = "Credenciais não configuradas"
                return result
            
            start_time = time.time()
            response = requests.get(
                f"https://graph.facebook.com/v18.0/{account_id}",
                params={"fields": "name", "access_token": access_token},
                timeout=10
            )
            response_time = time.time() - start_time
            
            result["response_time"] = response_time
            
            if response.status_code == 200:
                result["status"] = "healthy"
                if response_time > self.thresholds["api_response_time"]:
                    self.add_alert("instagram", "high_response_time",
                                 f"Tempo de resposta alto: {response_time:.2f}s")
            else:
                result["status"] = "error"
                result["error"] = f"HTTP {response.status_code}"
                self.add_alert("instagram", "api_error",
                             f"Erro na API: {response.status_code}")
                
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            self.add_alert("instagram", "connection_error", str(e))
        
        return result
    
    def check_openai_health(self) -> Dict[str, Any]:
        """Monitora saúde da API do OpenAI"""
        result = {
            "service": "openai",
            "status": "unknown",
            "response_time": None,
            "error": None,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                result["status"] = "error"
                result["error"] = "API key não configurada"
                return result
            
            start_time = time.time()
            response = requests.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10
            )
            response_time = time.time() - start_time
            
            result["response_time"] = response_time
            
            if response.status_code == 200:
                result["status"] = "healthy"
                if response_time > self.thresholds["api_response_time"]:
                    self.add_alert("openai", "high_response_time",
                                 f"Tempo de resposta alto: {response_time:.2f}s")
            else:
                result["status"] = "error"
                result["error"] = f"HTTP {response.status_code}"
                self.add_alert("openai", "api_error",
                             f"Erro na API: {response.status_code}")
                
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            self.add_alert("openai", "connection_error", str(e))
        
        return result
    
    def check_file_integrity(self) -> Dict[str, Any]:
        """Verifica integridade dos arquivos críticos"""
        result = {
            "service": "file_system",
            "status": "healthy",
            "missing_files": [],
            "corrupted_files": [],
            "timestamp": datetime.now().isoformat()
        }
        
        critical_files = [
            "src/config.py",
            "src/pipeline/generate_and_publish.py",
            "automation/scheduler.py",
            "requirements.txt",
            ".env"
        ]
        
        for file_path in critical_files:
            path = Path(file_path)
            if not path.exists():
                result["missing_files"].append(file_path)
                self.add_alert("file_system", "missing_file", f"Arquivo crítico faltando: {file_path}")
            else:
                # Verificar se o arquivo não está vazio
                try:
                    if path.stat().st_size == 0:
                        result["corrupted_files"].append(file_path)
                        self.add_alert("file_system", "empty_file", f"Arquivo vazio: {file_path}")
                except Exception as e:
                    result["corrupted_files"].append(file_path)
                    self.add_alert("file_system", "access_error", f"Erro ao acessar {file_path}: {e}")
        
        if result["missing_files"] or result["corrupted_files"]:
            result["status"] = "error"
        
        return result
    
    def check_scheduler_status(self) -> Dict[str, Any]:
        """Verifica se o agendador está configurado corretamente"""
        result = {
            "service": "scheduler",
            "status": "unknown",
            "scheduled_jobs": 0,
            "next_run": None,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Verificar se o arquivo do scheduler existe
            scheduler_file = Path("automation/scheduler.py")
            config_file = Path("automation/automation_config.json")
            
            if not scheduler_file.exists():
                result["status"] = "error"
                result["error"] = "Arquivo scheduler.py não encontrado"
                self.add_alert("scheduler", "missing_file", "Scheduler não encontrado")
                return result
            
            # Verificar configuração do agendamento
            feed_21h_configured = False
            stories_21h_configured = False
            
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    
                    post_times = config.get("schedule", {}).get("post_times", [])
                    stories_times = config.get("schedule", {}).get("stories_times", [])
                    
                    if "21:00" in post_times:
                        feed_21h_configured = True
                    if "21:00" in stories_times:
                        stories_21h_configured = True
                        
                except Exception as e:
                    logger.warning(f"Erro ao ler configuração: {e}")
            
            # Verificar conteúdo do scheduler como fallback
            with open(scheduler_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if feed_21h_configured or ("21:00" in content and "feed" in content.lower()):
                result["scheduled_jobs"] = 1
                result["status"] = "healthy"
                
                # Calcular próxima execução (21h BRT)
                now = datetime.now()
                next_run = now.replace(hour=21, minute=0, second=0, microsecond=0)
                if now.hour >= 21:
                    next_run += timedelta(days=1)
                result["next_run"] = next_run.isoformat()
                
                if stories_21h_configured:
                    result["note"] = "Feed e Stories configurados para 21h"
                else:
                    result["note"] = "Feed configurado para 21h"
                    
            elif stories_21h_configured:
                result["scheduled_jobs"] = 1
                result["status"] = "warning"
                result["error"] = "Apenas Stories configurado para 21h, Feed não encontrado"
                result["note"] = "Stories configurado para 21h, mas Feed ausente"
                self.add_alert("scheduler", "partial_schedule", "Stories 21h configurado, mas Feed 21h ausente")
            else:
                result["status"] = "error"
                result["error"] = "Agendamento das 21h não encontrado"
                self.add_alert("scheduler", "missing_schedule", "Agendamento das 21h não configurado")
                
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            self.add_alert("scheduler", "check_error", str(e))
        
        return result
    
    def add_alert(self, service: str, alert_type: str, message: str):
        """Adiciona um alerta ao sistema"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "service": service,
            "type": alert_type,
            "message": message,
            "severity": self.get_alert_severity(alert_type)
        }
        
        self.alerts.append(alert)
        logger.warning(f"ALERTA [{service}] {alert_type}: {message}")
    
    def get_alert_severity(self, alert_type: str) -> str:
        """Determina a severidade do alerta"""
        critical_types = ["connection_error", "api_error", "missing_file", "missing_schedule"]
        warning_types = ["high_response_time", "empty_file"]
        
        if alert_type in critical_types:
            return "critical"
        elif alert_type in warning_types:
            return "warning"
        else:
            return "info"
    
    def send_telegram_alert(self, summary: Dict[str, Any]):
        """Envia alerta via Telegram se houver problemas"""
        if not self.alerts:
            return
        
        try:
            token = os.getenv("TELEGRAM_BOT_TOKEN")
            chat_id = os.getenv("TELEGRAM_CHAT_ID")
            
            if not token or not chat_id:
                logger.error("Credenciais do Telegram não configuradas para alertas")
                return
            
            # Contar alertas por severidade
            critical_count = sum(1 for alert in self.alerts if alert["severity"] == "critical")
            warning_count = sum(1 for alert in self.alerts if alert["severity"] == "warning")
            
            if critical_count > 0:
                emoji = "🚨"
                status = "CRÍTICO"
            elif warning_count > 0:
                emoji = "⚠️"
                status = "AVISO"
            else:
                emoji = "ℹ️"
                status = "INFO"
            
            message = f"{emoji} MONITORAMENTO PREVENTIVO - {status}\n\n"
            message += f"📊 Resumo:\n"
            message += f"• Serviços monitorados: {len(summary['services'])}\n"
            message += f"• Alertas críticos: {critical_count}\n"
            message += f"• Avisos: {warning_count}\n\n"
            
            if critical_count > 0:
                message += "🚨 PROBLEMAS CRÍTICOS:\n"
                for alert in self.alerts:
                    if alert["severity"] == "critical":
                        message += f"• [{alert['service']}] {alert['message']}\n"
                message += "\n"
            
            if warning_count > 0:
                message += "⚠️ AVISOS:\n"
                for alert in self.alerts:
                    if alert["severity"] == "warning":
                        message += f"• [{alert['service']}] {alert['message']}\n"
            
            message += f"\n🕐 Verificação: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            
            # Enviar mensagem
            requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": message},
                timeout=10
            )
            
            logger.info("Alerta enviado via Telegram")
            
        except Exception as e:
            logger.error(f"Erro ao enviar alerta via Telegram: {e}")
    
    def run_health_check(self):
        """Executa verificação completa de saúde"""
        logger.info("Iniciando verificação de saúde preventiva...")
        
        # Limpar alertas anteriores
        self.alerts = []
        
        # Executar verificações
        checks = [
            self.check_telegram_health,
            self.check_instagram_health,
            self.check_openai_health,
            self.check_file_integrity,
            self.check_scheduler_status
        ]
        
        results = {}
        for check in checks:
            try:
                result = check()
                service_name = result.get("service", check.__name__)
                results[service_name] = result
            except Exception as e:
                logger.error(f"Erro na verificação {check.__name__}: {e}")
                results[check.__name__] = {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        # Gerar resumo
        summary = {
            "timestamp": datetime.now().isoformat(),
            "services": results,
            "alerts": self.alerts,
            "healthy_services": sum(1 for r in results.values() if r.get("status") == "healthy"),
            "total_services": len(results),
            "critical_alerts": sum(1 for a in self.alerts if a["severity"] == "critical"),
            "warning_alerts": sum(1 for a in self.alerts if a["severity"] == "warning")
        }
        
        # Salvar relatório
        report_file = f"monitoring/health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs("monitoring", exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        # Log do resumo
        logger.info(f"Verificação concluída: {summary['healthy_services']}/{summary['total_services']} serviços saudáveis")
        logger.info(f"Alertas: {summary['critical_alerts']} críticos, {summary['warning_alerts']} avisos")
        
        # Enviar alertas se necessário
        if self.alerts:
            self.send_telegram_alert(summary)
        
        return summary
    
    def start_monitoring(self):
        """Inicia monitoramento contínuo"""
        logger.info("Iniciando monitoramento preventivo...")
        
        # Agendar verificações
        schedule.every(15).minutes.do(self.run_health_check)  # A cada 15 minutos
        schedule.every().hour.at(":00").do(self.run_health_check)  # A cada hora
        schedule.every().day.at("09:00").do(self.run_health_check)  # Diariamente às 9h
        schedule.every().day.at("20:30").do(self.run_health_check)  # Antes do post das 21h
        
        # Executar verificação inicial
        self.run_health_check()
        
        # Loop principal
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Verificar a cada minuto
            except KeyboardInterrupt:
                logger.info("Monitoramento interrompido pelo usuário")
                break
            except Exception as e:
                logger.error(f"Erro no loop de monitoramento: {e}")
                time.sleep(60)

def main():
    """Função principal"""
    monitor = PreventiveMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--check-once":
        # Executar apenas uma verificação
        summary = monitor.run_health_check()
        print(f"\n📊 RESUMO DA VERIFICAÇÃO:")
        print(f"Serviços saudáveis: {summary['healthy_services']}/{summary['total_services']}")
        print(f"Alertas críticos: {summary['critical_alerts']}")
        print(f"Avisos: {summary['warning_alerts']}")
        
        if summary['critical_alerts'] > 0:
            sys.exit(1)
    else:
        # Iniciar monitoramento contínuo
        monitor.start_monitoring()

if __name__ == "__main__":
    main()