#!/usr/bin/env python3
"""
Análise Detalhada da Falha dos Stories das 21h BRT
Investigação completa da causa raiz do problema
"""

import os
import json
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
import sys

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / "src"))

class StoriesFailureAnalyzer:
    def __init__(self):
        self.setup_logging()
        self.analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "21h_stories_failure_investigation",
            "findings": {},
            "timeline": [],
            "evidence": [],
            "recommendations": [],
            "prevention_measures": []
        }
        
    def setup_logging(self):
        """Configurar logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def analyze_railway_status(self):
        """1. Analisar status atual do Railway"""
        self.logger.info("🔍 1. ANALISANDO STATUS DO RAILWAY")
        
        findings = {
            "procfile_analysis": {},
            "scheduler_configuration": {},
            "environment_variables": {},
            "discrepancies": []
        }
        
        # Analisar Procfile
        try:
            procfile_path = Path(__file__).parent / "Procfile"
            if procfile_path.exists():
                with open(procfile_path, 'r', encoding='utf-8') as f:
                    procfile_content = f.read()
                
                findings["procfile_analysis"] = {
                    "exists": True,
                    "main_command": "python railway_scheduler.py" if "railway_scheduler.py" in procfile_content else "UNKNOWN",
                    "content_preview": procfile_content[:200]
                }
                
                # DISCREPÂNCIA CRÍTICA IDENTIFICADA
                if "railway_automation.py" in procfile_content:
                    findings["discrepancies"].append({
                        "type": "CRITICAL_DISCREPANCY",
                        "description": "Procfile pode estar executando railway_automation.py (simulação) em vez de railway_scheduler.py (real)",
                        "impact": "HIGH",
                        "evidence": "railway_automation.py contém apenas simulate_post_creation()"
                    })
                    
        except Exception as e:
            findings["procfile_analysis"] = {"error": str(e)}
        
        # Analisar configuração do scheduler
        try:
            scheduler_path = Path(__file__).parent / "railway_scheduler.py"
            if scheduler_path.exists():
                with open(scheduler_path, 'r', encoding='utf-8') as f:
                    scheduler_content = f.read()
                
                # Verificar agendamentos de stories
                stories_schedules = []
                if "00:00" in scheduler_content and "create_scheduled_stories" in scheduler_content:
                    stories_schedules.append("00:00 UTC (21:00 BRT)")
                if "18:00" in scheduler_content and "create_scheduled_stories" in scheduler_content:
                    stories_schedules.append("18:00 UTC (15:00 BRT)")
                if "12:00" in scheduler_content and "create_scheduled_stories" in scheduler_content:
                    stories_schedules.append("12:00 UTC (09:00 BRT)")
                
                findings["scheduler_configuration"] = {
                    "stories_schedules_found": stories_schedules,
                    "has_21h_brt_schedule": "00:00 UTC (21:00 BRT)" in stories_schedules,
                    "uses_real_generate_and_publish": "generate_and_publish" in scheduler_content,
                    "mode_parameter": "mode='stories'" in scheduler_content
                }
                
        except Exception as e:
            findings["scheduler_configuration"] = {"error": str(e)}
        
        # Verificar variáveis de ambiente críticas
        env_vars_to_check = [
            'OPENAI_API_KEY', 'RAPIDAPI_KEY', 'INSTAGRAM_ACCESS_TOKEN',
            'INSTAGRAM_BUSINESS_ACCOUNT_ID', 'TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID',
            'DRY_RUN', 'SIMULATION_MODE', 'PRODUCTION_MODE', 'REAL_POSTING'
        ]
        
        for var in env_vars_to_check:
            value = os.getenv(var)
            findings["environment_variables"][var] = {
                "exists": value is not None,
                "value_preview": value[:10] + "..." if value and len(value) > 10 else value
            }
        
        # Verificar se há variáveis que forçam simulação
        simulation_vars = ['DRY_RUN', 'SIMULATION_MODE', 'TEST_MODE']
        for var in simulation_vars:
            if os.getenv(var):
                findings["discrepancies"].append({
                    "type": "SIMULATION_MODE_DETECTED",
                    "description": f"Variável {var} está definida, pode estar forçando modo simulação",
                    "impact": "HIGH",
                    "evidence": f"{var}={os.getenv(var)}"
                })
        
        self.analysis_results["findings"]["railway_status"] = findings
        
        # Adicionar à timeline
        self.analysis_results["timeline"].append({
            "timestamp": datetime.now().isoformat(),
            "event": "Railway Status Analysis",
            "status": "COMPLETED",
            "critical_issues": len([d for d in findings["discrepancies"] if d.get("impact") == "HIGH"])
        })
        
    def analyze_telegram_integration(self):
        """2. Analisar integração com Telegram"""
        self.logger.info("📱 2. ANALISANDO INTEGRAÇÃO COM TELEGRAM")
        
        findings = {
            "configuration": {},
            "connectivity": {},
            "silent_failures": []
        }
        
        # Verificar configuração
        telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        telegram_chat = os.getenv('TELEGRAM_CHAT_ID')
        
        findings["configuration"] = {
            "bot_token_configured": telegram_token is not None,
            "chat_id_configured": telegram_chat is not None,
            "token_format_valid": telegram_token and ":" in telegram_token if telegram_token else False
        }
        
        # Testar conectividade (se configurado)
        if telegram_token and telegram_chat:
            try:
                sys.path.append(str(Path(__file__).parent / "src"))
                from services.telegram_client import TelegramClient
                
                telegram_client = TelegramClient(telegram_token, telegram_chat)
                
                # Tentar enviar mensagem de teste
                test_message = f"🔍 Teste de conectividade - {datetime.now().strftime('%H:%M:%S')}"
                result = telegram_client.send_message(test_message)
                
                findings["connectivity"] = {
                    "test_successful": True,
                    "test_timestamp": datetime.now().isoformat(),
                    "response": str(result)[:100]
                }
                
            except Exception as e:
                findings["connectivity"] = {
                    "test_successful": False,
                    "error": str(e),
                    "test_timestamp": datetime.now().isoformat()
                }
                
                findings["silent_failures"].append({
                    "type": "TELEGRAM_CONNECTION_FAILURE",
                    "description": "Falha na conectividade com Telegram",
                    "error": str(e),
                    "impact": "MEDIUM"
                })
        
        self.analysis_results["findings"]["telegram_integration"] = findings
        
    def analyze_instagram_publishing(self):
        """3. Analisar processo de publicação no Instagram"""
        self.logger.info("📸 3. ANALISANDO PROCESSO DE PUBLICAÇÃO NO INSTAGRAM")
        
        findings = {
            "credentials": {},
            "quotas": {},
            "restrictions": {},
            "api_health": {}
        }
        
        # Verificar credenciais
        instagram_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
        instagram_business_id = os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID')
        
        findings["credentials"] = {
            "access_token_configured": instagram_token is not None,
            "business_id_configured": instagram_business_id is not None,
            "token_length": len(instagram_token) if instagram_token else 0,
            "business_id_format": instagram_business_id.isdigit() if instagram_business_id else False
        }
        
        # Verificar accounts.json
        try:
            accounts_path = Path(__file__).parent / "accounts.json"
            if accounts_path.exists():
                with open(accounts_path, 'r', encoding='utf-8') as f:
                    accounts = json.load(f)
                
                findings["credentials"]["accounts_file"] = {
                    "exists": True,
                    "account_count": len(accounts),
                    "accounts": [acc.get('nome', 'UNNAMED') for acc in accounts]
                }
                
                # Verificar se as credenciais do ambiente batem com accounts.json
                for acc in accounts:
                    if acc.get('instagram_access_token') == instagram_token:
                        findings["credentials"]["token_match_found"] = True
                        break
                else:
                    findings["credentials"]["token_match_found"] = False
                    
        except Exception as e:
            findings["credentials"]["accounts_file"] = {"error": str(e)}
        
        # Testar API do Instagram (se credenciais disponíveis)
        if instagram_token and instagram_business_id:
            try:
                sys.path.append(str(Path(__file__).parent / "src"))
                from services.instagram_client_robust import InstagramClientRobust
                
                instagram_client = InstagramClientRobust(instagram_business_id, instagram_token)
                
                # Testar conectividade básica
                # Nota: Não vamos fazer chamadas reais para evitar consumir quota
                findings["api_health"] = {
                    "client_initialized": True,
                    "credentials_format_valid": True,
                    "test_timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                findings["api_health"] = {
                    "client_initialized": False,
                    "error": str(e),
                    "test_timestamp": datetime.now().isoformat()
                }
        
        self.analysis_results["findings"]["instagram_publishing"] = findings
        
    def analyze_ltm_logs(self):
        """4. Consultar LTM (Logs, Traces e Métricas)"""
        self.logger.info("📊 4. CONSULTANDO LTM - LOGS, TRACES E MÉTRICAS")
        
        findings = {
            "log_files": {},
            "anomalous_events": [],
            "performance_metrics": {},
            "api_failures": [],
            "critical_timeframe_analysis": {}
        }
        
        # Analisar arquivos de log e relatórios existentes
        log_files_to_check = [
            "simulation_issue_diagnosis_*.json",
            "comprehensive_performance_documentation_*.json",
            "final_system_verification_report_*.json",
            "connection_auth_report_*.json"
        ]
        
        project_root = Path(__file__).parent
        
        for pattern in log_files_to_check:
            matching_files = list(project_root.glob(pattern))
            if matching_files:
                latest_file = max(matching_files, key=lambda f: f.stat().st_mtime)
                try:
                    with open(latest_file, 'r', encoding='utf-8') as f:
                        content = json.load(f)
                    
                    findings["log_files"][pattern] = {
                        "file": latest_file.name,
                        "timestamp": datetime.fromtimestamp(latest_file.stat().st_mtime).isoformat(),
                        "content_summary": self._summarize_log_content(content)
                    }
                    
                    # Procurar por eventos anômalos
                    anomalies = self._detect_anomalies_in_log(content, latest_file.name)
                    findings["anomalous_events"].extend(anomalies)
                    
                except Exception as e:
                    findings["log_files"][pattern] = {"error": str(e)}
        
        # Análise específica do timeframe crítico (21h BRT = 00h UTC)
        findings["critical_timeframe_analysis"] = {
            "target_time": "00:00 UTC (21:00 BRT)",
            "analysis_window": "23:30 UTC - 00:30 UTC",
            "events_found": [],
            "gaps_detected": []
        }
        
        # Verificar se há evidências de execução no horário crítico
        current_hour = datetime.now().hour
        if current_hour == 0 or current_hour == 23:  # Próximo ao horário crítico
            findings["critical_timeframe_analysis"]["current_status"] = "WITHIN_CRITICAL_WINDOW"
        else:
            findings["critical_timeframe_analysis"]["current_status"] = "OUTSIDE_CRITICAL_WINDOW"
        
        self.analysis_results["findings"]["ltm_analysis"] = findings
        
    def _summarize_log_content(self, content):
        """Resumir conteúdo de log"""
        summary = {}
        
        if isinstance(content, dict):
            # Contar chaves principais
            summary["main_keys"] = list(content.keys())[:10]  # Primeiras 10 chaves
            
            # Procurar por indicadores importantes
            if "simulation" in str(content).lower():
                summary["contains_simulation_data"] = True
            if "error" in str(content).lower():
                summary["contains_errors"] = True
            if "success" in str(content).lower():
                summary["contains_success_data"] = True
                
        return summary
        
    def _detect_anomalies_in_log(self, content, filename):
        """Detectar anomalias em logs"""
        anomalies = []
        
        content_str = str(content).lower()
        
        # Detectar simulações quando deveria ser real
        if "simulation" in content_str and "real" not in content_str:
            anomalies.append({
                "type": "SIMULATION_MODE_DETECTED",
                "source": filename,
                "description": "Log indica modo simulação ativo",
                "severity": "HIGH"
            })
        
        # Detectar falhas de API
        if "api" in content_str and ("error" in content_str or "fail" in content_str):
            anomalies.append({
                "type": "API_FAILURE_DETECTED",
                "source": filename,
                "description": "Possível falha de API detectada nos logs",
                "severity": "MEDIUM"
            })
        
        # Detectar problemas de autenticação
        if "auth" in content_str and ("invalid" in content_str or "expired" in content_str):
            anomalies.append({
                "type": "AUTHENTICATION_ISSUE",
                "source": filename,
                "description": "Possível problema de autenticação",
                "severity": "HIGH"
            })
        
        return anomalies
        
    def generate_recommendations(self):
        """Gerar recomendações baseadas na análise"""
        self.logger.info("💡 GERANDO RECOMENDAÇÕES")
        
        # Recomendações imediatas
        immediate_actions = []
        
        # Verificar se há discrepâncias críticas
        railway_findings = self.analysis_results["findings"].get("railway_status", {})
        discrepancies = railway_findings.get("discrepancies", [])
        
        for discrepancy in discrepancies:
            if discrepancy.get("impact") == "HIGH":
                if discrepancy.get("type") == "CRITICAL_DISCREPANCY":
                    immediate_actions.append({
                        "priority": "CRITICAL",
                        "action": "Verificar e corrigir Procfile para usar railway_scheduler.py",
                        "description": "Procfile pode estar executando arquivo de simulação",
                        "estimated_time": "5 minutos"
                    })
                elif discrepancy.get("type") == "SIMULATION_MODE_DETECTED":
                    immediate_actions.append({
                        "priority": "HIGH",
                        "action": "Remover ou corrigir variáveis de ambiente que forçam simulação",
                        "description": f"Variável detectada: {discrepancy.get('evidence')}",
                        "estimated_time": "2 minutos"
                    })
        
        # Recomendações de prevenção
        prevention_measures = [
            {
                "measure": "Implementar monitoramento de modo de operação",
                "description": "Adicionar verificação automática se o sistema está em modo real ou simulação",
                "implementation": "Criar script de verificação que roda a cada hora"
            },
            {
                "measure": "Adicionar logs detalhados para stories",
                "description": "Incluir logs específicos para publicação de stories com timestamps",
                "implementation": "Modificar railway_scheduler.py para incluir logs detalhados"
            },
            {
                "measure": "Criar sistema de alertas para falhas silenciosas",
                "description": "Notificar via Telegram quando stories não são publicados no horário esperado",
                "implementation": "Implementar verificação pós-execução com timeout"
            }
        ]
        
        self.analysis_results["recommendations"] = immediate_actions
        self.analysis_results["prevention_measures"] = prevention_measures
        
    def generate_technical_report(self):
        """Gerar relatório técnico detalhado"""
        self.logger.info("📋 GERANDO RELATÓRIO TÉCNICO")
        
        # Calcular score de criticidade
        critical_issues = 0
        high_issues = 0
        medium_issues = 0
        
        for finding_category in self.analysis_results["findings"].values():
            if isinstance(finding_category, dict):
                discrepancies = finding_category.get("discrepancies", [])
                for disc in discrepancies:
                    impact = disc.get("impact", "LOW")
                    if impact == "CRITICAL":
                        critical_issues += 1
                    elif impact == "HIGH":
                        high_issues += 1
                    elif impact == "MEDIUM":
                        medium_issues += 1
        
        # Determinar status geral
        if critical_issues > 0:
            overall_status = "CRITICAL_ISSUES_FOUND"
        elif high_issues > 0:
            overall_status = "HIGH_PRIORITY_ISSUES_FOUND"
        elif medium_issues > 0:
            overall_status = "MEDIUM_PRIORITY_ISSUES_FOUND"
        else:
            overall_status = "NO_MAJOR_ISSUES_DETECTED"
        
        # Adicionar resumo executivo
        self.analysis_results["executive_summary"] = {
            "overall_status": overall_status,
            "critical_issues_count": critical_issues,
            "high_priority_issues_count": high_issues,
            "medium_priority_issues_count": medium_issues,
            "analysis_completion_time": datetime.now().isoformat(),
            "primary_cause_hypothesis": self._determine_primary_cause()
        }
        
    def _determine_primary_cause(self):
        """Determinar causa primária baseada na análise"""
        railway_findings = self.analysis_results["findings"].get("railway_status", {})
        discrepancies = railway_findings.get("discrepancies", [])
        
        # Verificar se há discrepância crítica no Procfile
        for disc in discrepancies:
            if disc.get("type") == "CRITICAL_DISCREPANCY":
                return "PROCFILE_EXECUTING_SIMULATION_INSTEAD_OF_REAL_SCHEDULER"
        
        # Verificar se há variáveis de simulação
        for disc in discrepancies:
            if disc.get("type") == "SIMULATION_MODE_DETECTED":
                return "ENVIRONMENT_VARIABLES_FORCING_SIMULATION_MODE"
        
        # Se não há discrepâncias críticas, pode ser problema de configuração
        scheduler_config = railway_findings.get("scheduler_configuration", {})
        if not scheduler_config.get("has_21h_brt_schedule", False):
            return "MISSING_21H_BRT_SCHEDULE_CONFIGURATION"
        
        return "UNKNOWN_REQUIRES_DEEPER_INVESTIGATION"
        
    def save_report(self):
        """Salvar relatório"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stories_21h_failure_analysis_{timestamp}.json"
        filepath = Path(__file__).parent / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"📄 Relatório salvo: {filename}")
        
        # Criar resumo em markdown
        self._create_markdown_summary(timestamp)
        
        return filename
        
    def _create_markdown_summary(self, timestamp):
        """Criar resumo em markdown"""
        filename = f"stories_21h_failure_analysis_summary_{timestamp}.md"
        filepath = Path(__file__).parent / filename
        
        summary = self.analysis_results["executive_summary"]
        
        markdown_content = f"""# Análise de Falha - Stories 21h BRT

## Resumo Executivo

**Status Geral:** {summary["overall_status"]}
**Timestamp:** {summary["analysis_completion_time"]}
**Hipótese da Causa Primária:** {summary["primary_cause_hypothesis"]}

### Contadores de Problemas
- 🔴 Críticos: {summary["critical_issues_count"]}
- 🟡 Alta Prioridade: {summary["high_priority_issues_count"]}
- 🟠 Média Prioridade: {summary["medium_priority_issues_count"]}

## Recomendações Imediatas

"""
        
        for rec in self.analysis_results["recommendations"]:
            markdown_content += f"""### {rec['priority']} - {rec['action']}
**Descrição:** {rec['description']}
**Tempo Estimado:** {rec['estimated_time']}

"""
        
        markdown_content += """## Medidas de Prevenção

"""
        
        for measure in self.analysis_results["prevention_measures"]:
            markdown_content += f"""### {measure['measure']}
**Descrição:** {measure['description']}
**Implementação:** {measure['implementation']}

"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        self.logger.info(f"📄 Resumo em markdown salvo: {filename}")
        
    def run_complete_analysis(self):
        """Executar análise completa"""
        self.logger.info("🔍 INICIANDO ANÁLISE COMPLETA DA FALHA DOS STORIES 21H")
        
        try:
            # 1. Analisar Railway
            self.analyze_railway_status()
            
            # 2. Analisar Telegram
            self.analyze_telegram_integration()
            
            # 3. Analisar Instagram
            self.analyze_instagram_publishing()
            
            # 4. Analisar LTM
            self.analyze_ltm_logs()
            
            # 5. Gerar recomendações
            self.generate_recommendations()
            
            # 6. Gerar relatório técnico
            self.generate_technical_report()
            
            # 7. Salvar relatório
            report_filename = self.save_report()
            
            self.logger.info("✅ ANÁLISE COMPLETA FINALIZADA")
            self.logger.info(f"📄 Relatório: {report_filename}")
            
            # Mostrar resumo no console
            summary = self.analysis_results["executive_summary"]
            self.logger.info(f"🎯 CAUSA PRIMÁRIA IDENTIFICADA: {summary['primary_cause_hypothesis']}")
            self.logger.info(f"🔴 Problemas críticos: {summary['critical_issues_count']}")
            self.logger.info(f"🟡 Problemas alta prioridade: {summary['high_priority_issues_count']}")
            
            return report_filename
            
        except Exception as e:
            self.logger.error(f"❌ Erro durante análise: {e}")
            raise

def main():
    """Função principal"""
    analyzer = StoriesFailureAnalyzer()
    return analyzer.run_complete_analysis()

if __name__ == "__main__":
    main()