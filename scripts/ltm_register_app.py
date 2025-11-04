#!/usr/bin/env python3
"""
Script de registro da aplicação no LTM (simulado)
- Valida endpoints de health check
- Gera um reporte de registro para auditoria
"""

import json
import time
import requests
from pathlib import Path
from datetime import datetime

CONFIG_PATH = Path("config/ltm_config.json")
OUTPUT_DIR = Path("backups")
OUTPUT_DIR.mkdir(exist_ok=True)

def validate_health(config: dict) -> dict:
    hc = config.get("health_check", {})
    url = hc.get("url")
    method = hc.get("method", "GET").upper()
    expected = int(hc.get("expected_status", 200))
    interval = int(hc.get("interval_seconds", 30))
    timeout = int(hc.get("timeout_seconds", 5))
    retries = int(hc.get("retries", 3))

    results = {"checks": []}
    for i in range(retries):
        try:
            resp = requests.request(method, url, timeout=timeout)
            ok = resp.status_code == expected
            results["checks"].append({
                "attempt": i + 1,
                "status_code": resp.status_code,
                "ok": ok
            })
            if ok:
                results["status"] = "HEALTHY"
                break
            time.sleep(interval)
        except Exception as e:
            results["checks"].append({
                "attempt": i + 1,
                "error": str(e),
                "ok": False
            })
            time.sleep(max(1, interval))
    if "status" not in results:
        results["status"] = "UNHEALTHY"
    return results

def main():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {CONFIG_PATH}")
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    health = validate_health(config)

    report = {
        "timestamp": datetime.now().isoformat(),
        "service_name": config.get("service_name"),
        "environment": config.get("environment"),
        "balancer": config.get("balancer"),
        "nodes": config.get("nodes"),
        "health_check": health
    }

    out = OUTPUT_DIR / f"ltm_register_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"📋 Relatório de registro LTM salvo em: {out}")
    print(f"Status de health: {health.get('status')}")

if __name__ == "__main__":
    main()