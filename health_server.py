#!/usr/bin/env python3
"""
Health Check Server para Railway
Fornece endpoints de saúde e monitoramento do sistema
"""

import os
import json
import threading
import time
from datetime import datetime, timedelta
from flask import Flask, jsonify
import logging
from pathlib import Path

# Configurar logging para o health server
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthServer:
    def __init__(self, port=8000):
        self.app = Flask(__name__)
        self.port = port
        self.start_time = datetime.now()
        self.last_activity = datetime.now()
        self.scheduler_status = "starting"
        self.server_thread = None
        self.health_log_file = Path("data/health_checks.jsonl")
        try:
            self.health_log_file.parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        # Configurações de health via bot_config.json
        self._settings = self._load_health_settings()
        self._last_alert_at: datetime | None = None
        
        # Importar performance monitor se disponível
        try:
            from performance_monitor import performance_monitor
            self.performance_monitor = performance_monitor
        except ImportError:
            self.performance_monitor = None
            logger.warning("Performance monitor não disponível")

        # Cliente Telegram opcional para alertas
        try:
            from src.services.telegram_client import TelegramClient
            self._TelegramClient = TelegramClient
        except Exception:
            self._TelegramClient = None
            logger.warning("TelegramClient não disponível (src.services.telegram_client)")

        self.setup_routes()

    def _load_health_settings(self) -> dict:
        """Carrega configurações de health checks do bot_config.json"""
        default = {
            "timeouts": {"supabase": 5, "telegram": 5, "storage": 5, "network": 5},
            "retries": 2,
            "retry_delay_seconds": 2,
            "alerts": {
                "enabled": False,
                "on_critical": True,
                "on_dependency_error": True,
                "throttle_minutes": 30,
            },
        }
        try:
            cfg_path = Path("config/bot_config.json")
            if cfg_path.exists():
                with open(cfg_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                hc = data.get("health_checks", {})
                # merge simples
                for k, v in default.items():
                    if k not in hc:
                        hc[k] = v
                # assegurar subchaves
                tdefs = default["timeouts"]
                hc["timeouts"] = {**tdefs, **hc.get("timeouts", {})}
                adefs = default["alerts"]
                hc["alerts"] = {**adefs, **hc.get("alerts", {})}
                return hc
        except Exception as e:
            logger.warning(f"Falha ao carregar bot_config.json para health: {e}")
        return default

    def _get_timeout(self, key: str) -> int:
        return int(self._settings.get("timeouts", {}).get(key, 5))

    def _should_throttle_alert(self) -> bool:
        try:
            throttle_min = int(self._settings.get("alerts", {}).get("throttle_minutes", 30))
        except Exception:
            throttle_min = 30
        if not self._last_alert_at:
            return False
        return (datetime.now() - self._last_alert_at) < timedelta(minutes=throttle_min)

    def _send_alert(self, text: str) -> bool:
        """Envia alerta via Telegram se habilitado e não throttled"""
        alerts_cfg = self._settings.get("alerts", {})
        if not alerts_cfg.get("enabled", False):
            return False
        if self._should_throttle_alert():
            logger.info("Alerta Telegram suprimido por throttle")
            return False
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID")
        if not (token and chat_id and self._TelegramClient):
            logger.warning("Telegram não configurado para alertas (token/chat_id/cliente ausentes)")
            return False
        try:
            client = self._TelegramClient(token, chat_id)
            ok = client.send_message(text)
            if ok:
                self._last_alert_at = datetime.now()
            else:
                logger.warning("Falha ao enviar alerta Telegram")
            return ok
        except Exception as e:
            logger.warning(f"Erro ao enviar alerta Telegram: {e}")
            return False

    def _check_supabase(self) -> dict:
        """Checar conectividade com Supabase REST"""
        import os, requests
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_ANON_KEY")
        if not url or not key:
            return {"status": "missing", "message": "SUPABASE_URL/ANON_KEY ausentes"}
        timeout = self._get_timeout("supabase")
        retries = int(self._settings.get("retries", 1))
        delay = int(self._settings.get("retry_delay_seconds", 1))
        last_err = None
        for _ in range(max(1, retries)):
            try:
                resp = requests.get(f"{url}/rest/v1/", headers={
                    "apikey": key,
                    "Authorization": f"Bearer {key}"
                }, timeout=timeout)
                return {"status": "ok" if resp.status_code == 200 else "error", "code": resp.status_code}
            except Exception as e:
                last_err = e
                time.sleep(delay)
        return {"status": "error", "error": str(last_err) if last_err else "unknown"}

    def _check_telegram(self) -> dict:
        """Checar token do Telegram e chamada básica getMe"""
        import os, requests
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        if not token:
            return {"status": "missing", "message": "TELEGRAM_BOT_TOKEN ausente"}
        timeout = self._get_timeout("telegram")
        retries = int(self._settings.get("retries", 1))
        delay = int(self._settings.get("retry_delay_seconds", 1))
        last_err = None
        for _ in range(max(1, retries)):
            try:
                resp = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=timeout)
                data = {}
                try:
                    data = resp.json()
                except Exception:
                    pass
                ok = resp.status_code == 200 and bool(data.get("ok", False))
                return {"status": "ok" if ok else "error", "code": resp.status_code, "ok": data.get("ok")}
            except Exception as e:
                last_err = e
                time.sleep(delay)
        return {"status": "error", "error": str(last_err) if last_err else "unknown"}

    def _check_storage(self) -> dict:
        """Checar conectividade com storage público (Catbox)"""
        import requests
        timeout = self._get_timeout("storage")
        retries = int(self._settings.get("retries", 1))
        delay = int(self._settings.get("retry_delay_seconds", 1))
        last_err = None
        for _ in range(max(1, retries)):
            try:
                resp = requests.head("https://files.catbox.moe/", timeout=timeout)
                return {"status": "ok" if resp.status_code in (200, 301, 302, 403) else "error", "code": resp.status_code}
            except Exception as e:
                last_err = e
                time.sleep(delay)
        return {"status": "error", "error": str(last_err) if last_err else "unknown"}

    def _check_network(self) -> dict:
        """Checagem simples de rede externa"""
        import requests
        timeout = self._get_timeout("network")
        retries = int(self._settings.get("retries", 1))
        delay = int(self._settings.get("retry_delay_seconds", 1))
        last_err = None
        for _ in range(max(1, retries)):
            try:
                resp = requests.get("https://httpbin.org/get", timeout=timeout)
                return {"status": "ok", "latency_ms": resp.elapsed.total_seconds() * 1000}
            except Exception as e:
                last_err = e
                time.sleep(delay)
        return {"status": "error", "error": str(last_err) if last_err else "unknown"}
        
    def setup_routes(self):
        """Configurar rotas do Flask"""
        
        @self.app.route('/')
        def root():
            return jsonify({
                "service": "LTM Instagram Automation",
                "status": "running",
                "message": "Health check server is operational",
                "timestamp": datetime.now().isoformat()
            })
        
        @self.app.route('/health')
        def health_check():
            uptime_seconds = (datetime.now() - self.start_time).total_seconds()
            last_activity_seconds = (datetime.now() - self.last_activity).total_seconds()
            route_start = datetime.now()
            
            # Status básico
            health_data = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": uptime_seconds,
                "uptime_human": str(timedelta(seconds=int(uptime_seconds))),
                "scheduler_status": self.scheduler_status,
                "last_activity": self.last_activity.isoformat(),
                "last_activity_seconds_ago": last_activity_seconds,
                "system_info": {
                    "python_version": os.sys.version,
                    "platform": os.name,
                    "environment": os.environ.get("RAILWAY_ENVIRONMENT", "local")
                }
            }
            
            # Adicionar métricas de performance se disponível
            if self.performance_monitor:
                try:
                    system_metrics = self.performance_monitor.get_system_metrics()
                    performance_summary = self.performance_monitor.get_performance_summary(24)
                    health_thresholds = self.performance_monitor.check_health_thresholds()
                    
                    health_data.update({
                        "system_metrics": system_metrics,
                        "performance_24h": performance_summary,
                        "health_check": health_thresholds
                    })
                    
                    # Ajustar status baseado nos thresholds
                    if health_thresholds.get("status") == "critical":
                        health_data["status"] = "critical"
                    elif health_thresholds.get("status") == "warning":
                        health_data["status"] = "warning"
                        
                except Exception as e:
                    health_data["performance_error"] = str(e)

            # Checagens de dependências externas
            external = {
                "supabase": self._check_supabase(),
                "telegram": self._check_telegram(),
                "storage": self._check_storage(),
                "network": self._check_network()
            }
            health_data["external_checks"] = external

            # Ajustar status por dependências críticas
            criticals = [k for k, v in external.items() if v.get("status") == "error"]
            if criticals:
                health_data["status"] = "warning" if health_data.get("status") == "healthy" else health_data.get("status")
                health_data["dependency_warnings"] = criticals

            # Enviar alerta opcional
            try:
                alerts_cfg = self._settings.get("alerts", {})
                dep_fail = any(v.get("status") in ("error", "missing") for v in external.values())
                should_alert = (
                    alerts_cfg.get("enabled", False)
                    and ((alerts_cfg.get("on_critical", True) and health_data.get("status") == "critical")
                         or (alerts_cfg.get("on_dependency_error", True) and dep_fail))
                )
                if should_alert:
                    env_name = os.environ.get("RAILWAY_ENVIRONMENT", "local")
                    msg = (
                        f"[ALERTA HEALTH] status={health_data.get('status')} env={env_name}\n"
                        f"Falhas: {', '.join([k for k,v in external.items() if v.get('status') in ('error','missing')]) or 'nenhuma'}\n"
                        f"Uptime: {health_data.get('uptime_human')}"
                    )
                    self._send_alert(msg)
            except Exception as e:
                logger.warning(f"Falha ao processar alerta health: {e}")

            # Verificar se o scheduler está ativo
            if last_activity_seconds > 3600:  # 1 hora sem atividade
                health_data["status"] = "warning"
                health_data["warning"] = "Scheduler inactive for over 1 hour"
            
            # Registrar no monitor e em arquivo de log
            try:
                if self.performance_monitor:
                    duration = (datetime.now() - route_start).total_seconds()
                    self.performance_monitor.record_execution("health_check", "system", "success", duration, {"status": health_data.get("status")})
                    # Salvar métricas periodicamente
                    self.performance_monitor.save_metrics()
                # Append JSONL
                with open(self.health_log_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(health_data, ensure_ascii=False) + "\n")
            except Exception as e:
                logger.warning(f"Falha ao registrar health: {e}")

            return jsonify(health_data)
        
        @self.app.route('/metrics')
        def metrics():
            """Endpoint específico para métricas detalhadas"""
            if not self.performance_monitor:
                return jsonify({"error": "Performance monitor not available"}), 503
            
            try:
                return jsonify({
                    "system_metrics": self.performance_monitor.get_system_metrics(),
                    "performance_summary_1h": self.performance_monitor.get_performance_summary(1),
                    "performance_summary_24h": self.performance_monitor.get_performance_summary(24),
                    "health_thresholds": self.performance_monitor.check_health_thresholds()
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route('/health/dependencies')
        def health_dependencies():
            """Endpoint específico para dependências externas"""
            deps = {
                "supabase": self._check_supabase(),
                "telegram": self._check_telegram(),
                "storage": self._check_storage(),
                "network": self._check_network()
            }
            return jsonify({"timestamp": datetime.now().isoformat(), "dependencies": deps})
        
        @self.app.route('/status')
        def status():
            """Status simplificado para checks rápidos"""
            return jsonify({
                "status": self.scheduler_status,
                "uptime": (datetime.now() - self.start_time).total_seconds(),
                "last_activity": (datetime.now() - self.last_activity).total_seconds()
            })
    
    def update_activity(self):
        """Atualizar timestamp da última atividade"""
        self.last_activity = datetime.now()
    
    def update_scheduler_status(self, status: str):
        """Atualizar status do scheduler"""
        self.scheduler_status = status
        self.update_activity()
    
    def start(self):
        """Iniciar o servidor em thread separada"""
        def run_server():
            try:
                logger.info(f"🏥 Health server iniciando na porta {self.port}")
                self.app.run(
                    host='0.0.0.0',
                    port=self.port,
                    debug=False,
                    use_reloader=False,
                    threaded=True
                )
            except Exception as e:
                logger.error(f"❌ Erro no health server: {e}")
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        logger.info(f"✅ Health server thread iniciada na porta {self.port}")

if __name__ == "__main__":
    # Teste do health server
    server = HealthServer(port=8000)
    server.start()
    
    import time
    print("Health server rodando... Pressione Ctrl+C para parar")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Parando health server...")