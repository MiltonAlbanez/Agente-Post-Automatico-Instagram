#!/usr/bin/env python3
"""
Diagnóstico Específico do Ambiente Railway
Verificação detalhada das diferenças entre ambiente local e Railway
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
import sys

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / "src"))

class RailwayEnvironmentDiagnostic:
    def __init__(self):
        self.setup_logging()
        self.diagnosis_results = {
            "timestamp": datetime.now().isoformat(),
            "diagnosis_type": "RAILWAY_ENVIRONMENT_ANALYSIS",
            "critical_findings": [],
            "environment_comparison": {},
            "root_cause_analysis": {},
            "immediate_fixes": []
        }
        
    def setup_logging(self):
        """Configurar logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def analyze_environment_variables(self):
        """Analisar variáveis de ambiente críticas"""
        self.logger.info("🔍 ANALISANDO VARIÁVEIS DE AMBIENTE")
        
        # Variáveis críticas que devem estar presentes no Railway
        critical_vars = {
            'OPENAI_API_KEY': 'Chave da API OpenAI para geração de conteúdo',
            'RAPIDAPI_KEY': 'Chave da RapidAPI para serviços externos',
            'INSTAGRAM_ACCESS_TOKEN': 'Token de acesso do Instagram',
            'INSTAGRAM_BUSINESS_ACCOUNT_ID': 'ID da conta business do Instagram',
            'TELEGRAM_BOT_TOKEN': 'Token do bot do Telegram',
            'TELEGRAM_CHAT_ID': 'ID do chat do Telegram'
        }
        
        # Variáveis que podem causar simulação
        simulation_vars = {
            'DRY_RUN': 'Modo dry run ativo',
            'SIMULATION_MODE': 'Modo simulação ativo',
            'TEST_MODE': 'Modo teste ativo',
            'DEBUG_MODE': 'Modo debug ativo',
            'PRODUCTION_MODE': 'Modo produção (deve ser true)',
            'REAL_POSTING': 'Postagem real (deve ser true)'
        }
        
        env_analysis = {
            "critical_variables": {},
            "simulation_variables": {},
            "missing_critical": [],
            "problematic_simulation": []
        }
        
        # Verificar variáveis críticas
        for var, description in critical_vars.items():
            value = os.getenv(var)
            env_analysis["critical_variables"][var] = {
                "exists": value is not None,
                "description": description,
                "value_length": len(value) if value else 0
            }
            
            if not value:
                env_analysis["missing_critical"].append({
                    "variable": var,
                    "description": description,
                    "impact": "CRITICAL"
                })
        
        # Verificar variáveis de simulação
        for var, description in simulation_vars.items():
            value = os.getenv(var)
            env_analysis["simulation_variables"][var] = {
                "exists": value is not None,
                "value": value,
                "description": description
            }
            
            # Verificar se está forçando simulação
            if value and var in ['DRY_RUN', 'SIMULATION_MODE', 'TEST_MODE', 'DEBUG_MODE']:
                if value.lower() in ['true', '1', 'yes', 'on']:
                    env_analysis["problematic_simulation"].append({
                        "variable": var,
                        "value": value,
                        "description": f"{description} - FORÇANDO SIMULAÇÃO",
                        "impact": "HIGH"
                    })
            
            # Verificar se produção está desabilitada
            if var in ['PRODUCTION_MODE', 'REAL_POSTING'] and value:
                if value.lower() in ['false', '0', 'no', 'off']:
                    env_analysis["problematic_simulation"].append({
                        "variable": var,
                        "value": value,
                        "description": f"{description} - DESABILITANDO PRODUÇÃO",
                        "impact": "HIGH"
                    })
        
        self.diagnosis_results["environment_comparison"] = env_analysis
        
        # Adicionar findings críticos
        if env_analysis["missing_critical"]:
            self.diagnosis_results["critical_findings"].append({
                "type": "MISSING_CRITICAL_ENVIRONMENT_VARIABLES",
                "count": len(env_analysis["missing_critical"]),
                "variables": [item["variable"] for item in env_analysis["missing_critical"]],
                "impact": "CRITICAL",
                "description": "Variáveis de ambiente críticas não configuradas no Railway"
            })
        
        if env_analysis["problematic_simulation"]:
            self.diagnosis_results["critical_findings"].append({
                "type": "SIMULATION_MODE_FORCED_BY_ENVIRONMENT",
                "count": len(env_analysis["problematic_simulation"]),
                "variables": [item["variable"] for item in env_analysis["problematic_simulation"]],
                "impact": "HIGH",
                "description": "Variáveis de ambiente forçando modo simulação"
            })
    
    def analyze_accounts_configuration(self):
        """Analisar configuração das contas"""
        self.logger.info("📱 ANALISANDO CONFIGURAÇÃO DAS CONTAS")
        
        try:
            accounts_path = Path(__file__).parent / "accounts.json"
            with open(accounts_path, 'r', encoding='utf-8') as f:
                accounts = json.load(f)
            
            accounts_analysis = {
                "file_exists": True,
                "account_count": len(accounts),
                "accounts_details": [],
                "configuration_issues": []
            }
            
            for i, account in enumerate(accounts):
                account_detail = {
                    "index": i,
                    "name": account.get('nome', 'UNNAMED'),
                    "has_instagram_id": bool(account.get('instagram_id')),
                    "has_instagram_token": bool(account.get('instagram_access_token')),
                    "has_telegram_config": bool(account.get('telegram_bot_token') and account.get('telegram_chat_id')),
                    "token_length": len(account.get('instagram_access_token', ''))
                }
                
                accounts_analysis["accounts_details"].append(account_detail)
                
                # Verificar problemas de configuração
                if not account.get('instagram_id'):
                    accounts_analysis["configuration_issues"].append({
                        "account": account.get('nome', f'Account_{i}'),
                        "issue": "Missing instagram_id",
                        "impact": "HIGH"
                    })
                
                if not account.get('instagram_access_token'):
                    accounts_analysis["configuration_issues"].append({
                        "account": account.get('nome', f'Account_{i}'),
                        "issue": "Missing instagram_access_token",
                        "impact": "CRITICAL"
                    })
            
            self.diagnosis_results["accounts_configuration"] = accounts_analysis
            
            if accounts_analysis["configuration_issues"]:
                self.diagnosis_results["critical_findings"].append({
                    "type": "ACCOUNTS_CONFIGURATION_ISSUES",
                    "count": len(accounts_analysis["configuration_issues"]),
                    "issues": accounts_analysis["configuration_issues"],
                    "impact": "HIGH",
                    "description": "Problemas na configuração das contas"
                })
                
        except Exception as e:
            self.diagnosis_results["accounts_configuration"] = {
                "file_exists": False,
                "error": str(e)
            }
            
            self.diagnosis_results["critical_findings"].append({
                "type": "ACCOUNTS_FILE_ERROR",
                "error": str(e),
                "impact": "CRITICAL",
                "description": "Erro ao ler arquivo accounts.json"
            })
    
    def analyze_scheduler_vs_automation(self):
        """Analisar diferença entre scheduler e automation"""
        self.logger.info("⚙️ ANALISANDO SCHEDULER VS AUTOMATION")
        
        analysis = {
            "railway_scheduler": {},
            "railway_automation": {},
            "procfile_configuration": {},
            "execution_difference": {}
        }
        
        # Analisar railway_scheduler.py
        try:
            scheduler_path = Path(__file__).parent / "railway_scheduler.py"
            with open(scheduler_path, 'r', encoding='utf-8') as f:
                scheduler_content = f.read()
            
            analysis["railway_scheduler"] = {
                "exists": True,
                "size": len(scheduler_content),
                "uses_generate_and_publish": "generate_and_publish" in scheduler_content,
                "has_stories_schedule": "create_scheduled_stories" in scheduler_content,
                "has_21h_schedule": "00:00" in scheduler_content and "create_scheduled_stories" in scheduler_content,
                "mode_stories": "mode='stories'" in scheduler_content,
                "mode_feed": "mode='feed'" in scheduler_content
            }
            
        except Exception as e:
            analysis["railway_scheduler"] = {"error": str(e)}
        
        # Analisar railway_automation.py
        try:
            automation_path = Path(__file__).parent / "railway_automation.py"
            with open(automation_path, 'r', encoding='utf-8') as f:
                automation_content = f.read()
            
            analysis["railway_automation"] = {
                "exists": True,
                "size": len(automation_content),
                "uses_simulate_post_creation": "simulate_post_creation" in automation_content,
                "uses_generate_and_publish": "generate_and_publish" in automation_content,
                "is_simulation_only": "simulate_post_creation" in automation_content and "generate_and_publish" not in automation_content
            }
            
        except Exception as e:
            analysis["railway_automation"] = {"error": str(e)}
        
        # Analisar Procfile
        try:
            procfile_path = Path(__file__).parent / "Procfile"
            with open(procfile_path, 'r', encoding='utf-8') as f:
                procfile_content = f.read()
            
            analysis["procfile_configuration"] = {
                "exists": True,
                "content": procfile_content,
                "main_command": "railway_scheduler.py" if "railway_scheduler.py" in procfile_content else "OTHER",
                "uses_scheduler": "railway_scheduler.py" in procfile_content,
                "uses_automation": "railway_automation.py" in procfile_content
            }
            
        except Exception as e:
            analysis["procfile_configuration"] = {"error": str(e)}
        
        # Determinar diferença de execução
        scheduler_real = analysis["railway_scheduler"].get("uses_generate_and_publish", False)
        automation_simulation = analysis["railway_automation"].get("is_simulation_only", False)
        procfile_uses_scheduler = analysis["procfile_configuration"].get("uses_scheduler", False)
        
        analysis["execution_difference"] = {
            "scheduler_does_real_posting": scheduler_real,
            "automation_does_simulation": automation_simulation,
            "procfile_uses_correct_file": procfile_uses_scheduler,
            "potential_issue": not procfile_uses_scheduler and automation_simulation
        }
        
        self.diagnosis_results["scheduler_vs_automation"] = analysis
        
        # Adicionar finding se há problema
        if analysis["execution_difference"].get("potential_issue"):
            self.diagnosis_results["critical_findings"].append({
                "type": "WRONG_FILE_EXECUTION",
                "description": "Procfile pode estar executando arquivo de simulação em vez do scheduler real",
                "impact": "CRITICAL",
                "evidence": {
                    "procfile_uses_scheduler": procfile_uses_scheduler,
                    "automation_is_simulation": automation_simulation
                }
            })
    
    def determine_root_cause(self):
        """Determinar causa raiz"""
        self.logger.info("🎯 DETERMINANDO CAUSA RAIZ")
        
        root_causes = []
        
        # Analisar findings críticos
        for finding in self.diagnosis_results["critical_findings"]:
            if finding["type"] == "MISSING_CRITICAL_ENVIRONMENT_VARIABLES":
                root_causes.append({
                    "cause": "ENVIRONMENT_VARIABLES_NOT_SET_IN_RAILWAY",
                    "priority": "CRITICAL",
                    "description": "Variáveis de ambiente críticas não estão configuradas no Railway",
                    "evidence": finding["variables"],
                    "fix": "Configurar todas as variáveis de ambiente no painel do Railway"
                })
            
            elif finding["type"] == "SIMULATION_MODE_FORCED_BY_ENVIRONMENT":
                root_causes.append({
                    "cause": "ENVIRONMENT_FORCING_SIMULATION_MODE",
                    "priority": "HIGH",
                    "description": "Variáveis de ambiente estão forçando modo simulação",
                    "evidence": finding["variables"],
                    "fix": "Remover ou corrigir variáveis que forçam simulação"
                })
            
            elif finding["type"] == "WRONG_FILE_EXECUTION":
                root_causes.append({
                    "cause": "PROCFILE_EXECUTING_WRONG_FILE",
                    "priority": "CRITICAL",
                    "description": "Procfile executando arquivo de simulação",
                    "evidence": finding["evidence"],
                    "fix": "Corrigir Procfile para usar railway_scheduler.py"
                })
        
        # Se não há variáveis de ambiente, essa é provavelmente a causa principal
        env_vars = self.diagnosis_results.get("environment_comparison", {})
        missing_critical = env_vars.get("missing_critical", [])
        
        if len(missing_critical) >= 4:  # Se faltam muitas variáveis críticas
            primary_cause = "RAILWAY_ENVIRONMENT_NOT_CONFIGURED"
        elif any(rc["cause"] == "PROCFILE_EXECUTING_WRONG_FILE" for rc in root_causes):
            primary_cause = "WRONG_EXECUTION_FILE"
        elif any(rc["cause"] == "ENVIRONMENT_FORCING_SIMULATION_MODE" for rc in root_causes):
            primary_cause = "FORCED_SIMULATION_MODE"
        else:
            primary_cause = "CONFIGURATION_MISMATCH"
        
        self.diagnosis_results["root_cause_analysis"] = {
            "primary_cause": primary_cause,
            "contributing_factors": root_causes,
            "confidence_level": "HIGH" if root_causes else "MEDIUM"
        }
    
    def generate_immediate_fixes(self):
        """Gerar correções imediatas"""
        self.logger.info("🔧 GERANDO CORREÇÕES IMEDIATAS")
        
        fixes = []
        
        # Baseado na causa raiz
        primary_cause = self.diagnosis_results["root_cause_analysis"]["primary_cause"]
        
        if primary_cause == "RAILWAY_ENVIRONMENT_NOT_CONFIGURED":
            fixes.append({
                "priority": "CRITICAL",
                "title": "Configurar Variáveis de Ambiente no Railway",
                "description": "Acessar painel do Railway e configurar todas as variáveis críticas",
                "steps": [
                    "1. Acessar dashboard do Railway",
                    "2. Ir em Settings > Environment Variables",
                    "3. Adicionar OPENAI_API_KEY com valor da chave OpenAI",
                    "4. Adicionar RAPIDAPI_KEY com valor da chave RapidAPI",
                    "5. Adicionar INSTAGRAM_ACCESS_TOKEN com token do Instagram",
                    "6. Adicionar INSTAGRAM_BUSINESS_ACCOUNT_ID com ID da conta",
                    "7. Adicionar TELEGRAM_BOT_TOKEN com token do bot",
                    "8. Adicionar TELEGRAM_CHAT_ID com ID do chat",
                    "9. Fazer redeploy da aplicação"
                ],
                "estimated_time": "10 minutos"
            })
        
        if primary_cause == "WRONG_EXECUTION_FILE":
            fixes.append({
                "priority": "HIGH",
                "title": "Corrigir Procfile",
                "description": "Garantir que Procfile execute railway_scheduler.py",
                "steps": [
                    "1. Verificar conteúdo do Procfile",
                    "2. Confirmar que linha principal é: scheduler: python railway_scheduler.py",
                    "3. Fazer commit e push das alterações",
                    "4. Verificar redeploy automático"
                ],
                "estimated_time": "5 minutos"
            })
        
        # Sempre adicionar verificação de logs
        fixes.append({
            "priority": "MEDIUM",
            "title": "Verificar Logs do Railway",
            "description": "Monitorar logs em tempo real para confirmar correções",
            "steps": [
                "1. Acessar dashboard do Railway",
                "2. Ir na aba Logs",
                "3. Verificar se sistema inicia corretamente",
                "4. Confirmar que não há erros de variáveis de ambiente",
                "5. Aguardar próximo horário de stories (00:00 UTC)"
            ],
            "estimated_time": "15 minutos"
        })
        
        self.diagnosis_results["immediate_fixes"] = fixes
    
    def save_diagnosis(self):
        """Salvar diagnóstico"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"railway_environment_diagnosis_{timestamp}.json"
        filepath = Path(__file__).parent / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.diagnosis_results, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"📄 Diagnóstico salvo: {filename}")
        
        # Criar resumo executivo
        self._create_executive_summary(timestamp)
        
        return filename
    
    def _create_executive_summary(self, timestamp):
        """Criar resumo executivo"""
        filename = f"railway_diagnosis_summary_{timestamp}.md"
        filepath = Path(__file__).parent / filename
        
        root_cause = self.diagnosis_results["root_cause_analysis"]
        
        summary = f"""# Diagnóstico Railway - Stories 21h BRT

## 🎯 CAUSA RAIZ IDENTIFICADA
**{root_cause["primary_cause"]}**

## 📊 Resumo dos Problemas
"""
        
        for finding in self.diagnosis_results["critical_findings"]:
            impact_emoji = "🔴" if finding["impact"] == "CRITICAL" else "🟡" if finding["impact"] == "HIGH" else "🟠"
            summary += f"{impact_emoji} **{finding['type']}**: {finding['description']}\n"
        
        summary += "\n## 🔧 Correções Imediatas\n\n"
        
        for fix in self.diagnosis_results["immediate_fixes"]:
            priority_emoji = "🔴" if fix["priority"] == "CRITICAL" else "🟡" if fix["priority"] == "HIGH" else "🟠"
            summary += f"### {priority_emoji} {fix['title']}\n"
            summary += f"**Tempo Estimado:** {fix['estimated_time']}\n\n"
            summary += f"{fix['description']}\n\n"
            
            for step in fix["steps"]:
                summary += f"- {step}\n"
            summary += "\n"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        self.logger.info(f"📄 Resumo executivo salvo: {filename}")
    
    def run_complete_diagnosis(self):
        """Executar diagnóstico completo"""
        self.logger.info("🔍 INICIANDO DIAGNÓSTICO COMPLETO DO RAILWAY")
        
        try:
            # 1. Analisar variáveis de ambiente
            self.analyze_environment_variables()
            
            # 2. Analisar configuração das contas
            self.analyze_accounts_configuration()
            
            # 3. Analisar scheduler vs automation
            self.analyze_scheduler_vs_automation()
            
            # 4. Determinar causa raiz
            self.determine_root_cause()
            
            # 5. Gerar correções imediatas
            self.generate_immediate_fixes()
            
            # 6. Salvar diagnóstico
            report_filename = self.save_diagnosis()
            
            # Mostrar resumo
            root_cause = self.diagnosis_results["root_cause_analysis"]["primary_cause"]
            critical_count = len([f for f in self.diagnosis_results["critical_findings"] if f["impact"] == "CRITICAL"])
            
            self.logger.info("✅ DIAGNÓSTICO COMPLETO FINALIZADO")
            self.logger.info(f"🎯 CAUSA RAIZ: {root_cause}")
            self.logger.info(f"🔴 Problemas críticos: {critical_count}")
            self.logger.info(f"📄 Relatório: {report_filename}")
            
            return report_filename
            
        except Exception as e:
            self.logger.error(f"❌ Erro durante diagnóstico: {e}")
            raise

def main():
    """Função principal"""
    diagnostic = RailwayEnvironmentDiagnostic()
    return diagnostic.run_complete_diagnosis()

if __name__ == "__main__":
    main()