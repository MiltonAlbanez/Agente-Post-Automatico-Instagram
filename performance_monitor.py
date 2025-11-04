#!/usr/bin/env python3
"""
Sistema de Monitoramento de Performance para LTM
Monitora métricas de sistema, execuções e performance geral
"""

import os
import json
import time
import psutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

class PerformanceMonitor:
    def __init__(self, log_file: str = "performance_monitor.log"):
        self.log_file = Path(log_file)
        self.metrics_file = Path("performance_metrics.json")
        self.setup_logging()
        self.start_time = datetime.now()
        self.execution_history = []
        
    def setup_logging(self):
        """Configurar logging específico para performance"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - [PERF] - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def get_system_metrics(self) -> Dict[str, Any]:
        """Coletar métricas do sistema"""
        try:
            # Métricas de CPU e Memória
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Métricas de rede (se disponível)
            try:
                network = psutil.net_io_counters()
                network_stats = {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                }
            except:
                network_stats = {"error": "Network stats not available"}
            
            return {
                "timestamp": datetime.now().isoformat(),
                "cpu": {
                    "percent": cpu_percent,
                    "count": psutil.cpu_count()
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100
                },
                "network": network_stats,
                "uptime_seconds": (datetime.now() - self.start_time).total_seconds()
            }
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas do sistema: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    def record_execution(self, operation: str, account: str, status: str, 
                        duration: float, details: Dict = None):
        """Registrar execução de operação"""
        execution_record = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "account": account,
            "status": status,
            "duration_seconds": duration,
            "details": details or {}
        }
        
        self.execution_history.append(execution_record)
        
        # Manter apenas os últimos 1000 registros
        if len(self.execution_history) > 1000:
            self.execution_history = self.execution_history[-1000:]
        
        self.logger.info(f"Execução registrada: {operation} - {account} - {status} ({duration:.2f}s)")
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Gerar resumo de performance das últimas N horas"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Filtrar execuções recentes
        recent_executions = [
            exec for exec in self.execution_history
            if datetime.fromisoformat(exec["timestamp"]) > cutoff_time
        ]
        
        if not recent_executions:
            return {"message": f"Nenhuma execução nas últimas {hours} horas"}
        
        # Calcular estatísticas
        total_executions = len(recent_executions)
        successful = len([e for e in recent_executions if e["status"] == "success"])
        failed = total_executions - successful
        
        # Estatísticas por operação
        operations_stats = {}
        for exec in recent_executions:
            op = exec["operation"]
            if op not in operations_stats:
                operations_stats[op] = {"count": 0, "success": 0, "total_duration": 0}
            
            operations_stats[op]["count"] += 1
            operations_stats[op]["total_duration"] += exec["duration_seconds"]
            if exec["status"] == "success":
                operations_stats[op]["success"] += 1
        
        # Calcular médias
        for op_stats in operations_stats.values():
            op_stats["success_rate"] = (op_stats["success"] / op_stats["count"]) * 100
            op_stats["avg_duration"] = op_stats["total_duration"] / op_stats["count"]
        
        return {
            "period_hours": hours,
            "total_executions": total_executions,
            "successful_executions": successful,
            "failed_executions": failed,
            "success_rate": (successful / total_executions) * 100 if total_executions > 0 else 0,
            "operations_stats": operations_stats,
            "system_metrics": self.get_system_metrics()
        }
    
    def save_metrics(self):
        """Salvar métricas em arquivo"""
        try:
            metrics_data = {
                "last_updated": datetime.now().isoformat(),
                "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
                "execution_history": self.execution_history[-100:],  # Últimas 100 execuções
                "performance_summary": self.get_performance_summary(24),
                "system_metrics": self.get_system_metrics()
            }
            
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(metrics_data, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Métricas salvas em {self.metrics_file}")
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar métricas: {e}")
    
    def load_metrics(self) -> Dict[str, Any]:
        """Carregar métricas salvas"""
        try:
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            self.logger.error(f"Erro ao carregar métricas: {e}")
            return {}
    
    def check_health_thresholds(self) -> Dict[str, Any]:
        """Verificar se as métricas estão dentro dos limites saudáveis"""
        metrics = self.get_system_metrics()
        health_status = {"status": "healthy", "warnings": [], "errors": []}
        
        # Verificar CPU
        if metrics.get("cpu", {}).get("percent", 0) > 80:
            health_status["warnings"].append(f"CPU usage high: {metrics['cpu']['percent']:.1f}%")
        
        # Verificar Memória
        memory_percent = metrics.get("memory", {}).get("percent", 0)
        if memory_percent > 85:
            health_status["errors"].append(f"Memory usage critical: {memory_percent:.1f}%")
        elif memory_percent > 70:
            health_status["warnings"].append(f"Memory usage high: {memory_percent:.1f}%")
        
        # Verificar Disco
        disk_percent = metrics.get("disk", {}).get("percent", 0)
        if disk_percent > 90:
            health_status["errors"].append(f"Disk usage critical: {disk_percent:.1f}%")
        elif disk_percent > 80:
            health_status["warnings"].append(f"Disk usage high: {disk_percent:.1f}%")
        
        # Determinar status geral
        if health_status["errors"]:
            health_status["status"] = "critical"
        elif health_status["warnings"]:
            health_status["status"] = "warning"
        
        return health_status

# Instância global do monitor
performance_monitor = PerformanceMonitor()

def monitor_execution(operation: str, account: str = "system"):
    """Decorator para monitorar execuções"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                performance_monitor.record_execution(
                    operation, account, "success", duration, 
                    {"result_type": type(result).__name__}
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                performance_monitor.record_execution(
                    operation, account, "error", duration,
                    {"error": str(e)}
                )
                raise
        return wrapper
    return decorator

if __name__ == "__main__":
    # Teste do sistema de monitoramento
    monitor = PerformanceMonitor()
    
    # Simular algumas execuções
    monitor.record_execution("test_post", "test_account", "success", 2.5)
    monitor.record_execution("test_story", "test_account", "error", 1.2, {"error": "API timeout"})
    
    # Mostrar resumo
    summary = monitor.get_performance_summary(1)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    
    # Salvar métricas
    monitor.save_metrics()