#!/usr/bin/env python3
"""
Análise Detalhada da Discrepância Railway
Investigação das diferenças entre configuração e execução
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

class RailwayDiscrepancyAnalyzer:
    def __init__(self):
        self.setup_logging()
        self.analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "RAILWAY_DISCREPANCY_INVESTIGATION",
            "image_analysis": {},
            "ltm_records_analysis": {},
            "telegram_silence_analysis": {},
            "execution_patterns": {},
            "root_cause_hypothesis": [],
            "verification_points": []
        }
        
    def setup_logging(self):
        """Configurar logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def analyze_railway_images_data(self):
        """Analisar dados das imagens do Railway"""
        self.logger.info("🖼️ ANALISANDO DADOS DAS IMAGENS DO RAILWAY")
        
        # Análise baseada nas imagens fornecidas
        image_analysis = {
            "variables_tab_analysis": {
                "variables_present": [
                    "AUTOCMD",
                    "TOKEN_DE_ACESSO_DO_INSTAGRAM", 
                    "ID_DA_CONTA_COMERCIAL_DO_INSTAGRAM",
                    "VERIFICAÇÕES_DE_ENQUETE_MÁXIMO",
                    "INSTAGRAM_MAX_RETENTATIVAS",
                    "INTERVALO_DE_ENQUETE_DO_INSTAGRAM",
                    "TEMPO_LIMITE_DO_INSTAGRAM"
                ],
                "variables_masked": True,
                "total_variables_visible": 7,
                "critical_missing_variables": [
                    "OPENAI_API_KEY",
                    "RAPIDAPI_KEY", 
                    "TELEGRAM_BOT_TOKEN",
                    "TELEGRAM_CHAT_ID"
                ],
                "naming_discrepancy": {
                    "expected": "INSTAGRAM_ACCESS_TOKEN",
                    "found": "TOKEN_DE_ACESSO_DO_INSTAGRAM",
                    "impact": "CRITICAL - Código pode não reconhecer nomes em português"
                }
            },
            "cron_runs_analysis": {
                "recent_executions": [
                    {
                        "date": "23/10/25",
                        "time": "21h26",
                        "status": "Correndo...",
                        "duration": "4m 13s",
                        "description": "Correção: Fallback automático"
                    },
                    {
                        "date": "23/10/25", 
                        "time": "21h03",
                        "status": "Completed",
                        "duration": "23m 13s",
                        "description": "Correção: Fallback automático"
                    },
                    {
                        "date": "22/10/25",
                        "time": "21h04", 
                        "status": "Completed",
                        "duration": "23h 59m",
                        "description": "Correção: Fallback automático"
                    },
                    {
                        "date": "21/10/25",
                        "time": "21h16",
                        "status": "Completed", 
                        "duration": "23h 47m",
                        "description": "Correção: Fallback automático"
                    }
                ],
                "pattern_analysis": {
                    "all_executions_fallback": True,
                    "consistent_21h_timing": True,
                    "long_durations": True,
                    "no_normal_executions": True
                }
            }
        }
        
        self.analysis_results["image_analysis"] = image_analysis
        
        # Identificar problemas críticos
        critical_issues = []
        
        # 1. Nomenclatura das variáveis
        if image_analysis["variables_tab_analysis"]["naming_discrepancy"]:
            critical_issues.append({
                "type": "VARIABLE_NAMING_MISMATCH",
                "severity": "CRITICAL",
                "description": "Variáveis configuradas em português, código espera em inglês",
                "evidence": image_analysis["variables_tab_analysis"]["naming_discrepancy"],
                "impact": "Sistema não consegue ler variáveis devido à diferença de nomenclatura"
            })
        
        # 2. Variáveis críticas ausentes
        missing_vars = image_analysis["variables_tab_analysis"]["critical_missing_variables"]
        if missing_vars:
            critical_issues.append({
                "type": "CRITICAL_VARIABLES_MISSING",
                "severity": "CRITICAL", 
                "description": "Variáveis essenciais não configuradas",
                "evidence": missing_vars,
                "impact": "Sistema não pode funcionar sem essas variáveis"
            })
        
        # 3. Padrão de execução anômalo
        if image_analysis["cron_runs_analysis"]["pattern_analysis"]["all_executions_fallback"]:
            critical_issues.append({
                "type": "FALLBACK_EXECUTION_PATTERN",
                "severity": "HIGH",
                "description": "Todas as execuções são fallbacks, nunca execução normal",
                "evidence": image_analysis["cron_runs_analysis"]["recent_executions"],
                "impact": "Sistema está constantemente em modo de recuperação"
            })
        
        self.analysis_results["critical_issues_from_images"] = critical_issues
        
    def analyze_ltm_records(self):
        """Analisar registros do LTM"""
        self.logger.info("📋 ANALISANDO REGISTROS DO LTM")
        
        # Buscar arquivos de relatórios e configurações
        ltm_files = []
        base_path = Path(__file__).parent
        
        # Buscar arquivos de relatórios recentes
        for pattern in ["*report*.json", "*diagnosis*.json", "*analysis*.json", "*ltm*.json"]:
            ltm_files.extend(list(base_path.glob(pattern)))
        
        ltm_analysis = {
            "files_found": len(ltm_files),
            "recent_records": [],
            "configuration_claims": [],
            "discrepancies_found": []
        }
        
        # Analisar arquivos encontrados
        for file_path in sorted(ltm_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                record = {
                    "filename": file_path.name,
                    "timestamp": data.get("timestamp", "unknown"),
                    "type": data.get("diagnosis_type", data.get("analysis_type", "unknown")),
                    "claims_variables_configured": False,
                    "environment_status": {}
                }
                
                # Verificar se há claims sobre variáveis configuradas
                if "environment_comparison" in data:
                    env_data = data["environment_comparison"]
                    record["environment_status"] = env_data
                    
                    # Verificar se há variáveis reportadas como existentes
                    if "critical_variables" in env_data:
                        for var, status in env_data["critical_variables"].items():
                            if status.get("exists", False):
                                record["claims_variables_configured"] = True
                                break
                
                ltm_analysis["recent_records"].append(record)
                
            except Exception as e:
                self.logger.warning(f"Erro ao ler {file_path}: {e}")
        
        # Analisar discrepâncias
        for record in ltm_analysis["recent_records"]:
            if record["claims_variables_configured"]:
                ltm_analysis["discrepancies_found"].append({
                    "file": record["filename"],
                    "claim": "Variáveis reportadas como configuradas",
                    "reality": "Imagens mostram variáveis ausentes ou com nomes incorretos",
                    "discrepancy_type": "LTM_VS_REALITY"
                })
        
        self.analysis_results["ltm_records_analysis"] = ltm_analysis
        
    def analyze_telegram_silence(self):
        """Analisar por que Telegram não está notificando"""
        self.logger.info("📱 ANALISANDO SILÊNCIO DO TELEGRAM")
        
        telegram_analysis = {
            "potential_causes": [],
            "verification_points": [],
            "hypothesis": []
        }
        
        # Verificar configuração do Telegram
        try:
            accounts_path = Path(__file__).parent / "accounts.json"
            with open(accounts_path, 'r', encoding='utf-8') as f:
                accounts = json.load(f)
            
            telegram_config = {
                "accounts_with_telegram": 0,
                "accounts_without_telegram": 0,
                "telegram_tokens_present": [],
                "telegram_chat_ids_present": []
            }
            
            for account in accounts:
                if account.get('telegram_bot_token') and account.get('telegram_chat_id'):
                    telegram_config["accounts_with_telegram"] += 1
                    telegram_config["telegram_tokens_present"].append(bool(account.get('telegram_bot_token')))
                    telegram_config["telegram_chat_ids_present"].append(bool(account.get('telegram_chat_id')))
                else:
                    telegram_config["accounts_without_telegram"] += 1
            
            telegram_analysis["local_config"] = telegram_config
            
            # Analisar possíveis causas do silêncio
            if telegram_config["accounts_without_telegram"] > 0:
                telegram_analysis["potential_causes"].append({
                    "cause": "TELEGRAM_NOT_CONFIGURED_IN_ACCOUNTS",
                    "description": "Algumas contas não têm configuração Telegram",
                    "impact": "Notificações não serão enviadas para essas contas"
                })
            
        except Exception as e:
            telegram_analysis["local_config_error"] = str(e)
        
        # Hipóteses sobre o silêncio
        telegram_analysis["hypothesis"] = [
            {
                "hypothesis": "VARIABLE_NAME_MISMATCH",
                "description": "Código busca TELEGRAM_BOT_TOKEN, mas Railway tem nomes em português",
                "probability": "HIGH",
                "evidence": "Padrão similar ao Instagram token"
            },
            {
                "hypothesis": "TELEGRAM_VARIABLES_MISSING_IN_RAILWAY", 
                "description": "Variáveis Telegram não configuradas no Railway",
                "probability": "HIGH",
                "evidence": "Não visíveis nas imagens das variáveis"
            },
            {
                "hypothesis": "SILENT_FAILURE_IN_TELEGRAM_CLIENT",
                "description": "Cliente Telegram falha silenciosamente sem variáveis",
                "probability": "MEDIUM",
                "evidence": "Padrão de fallback sem notificações"
            }
        ]
        
        self.analysis_results["telegram_silence_analysis"] = telegram_analysis
        
    def analyze_execution_patterns(self):
        """Analisar padrões de execução"""
        self.logger.info("🔄 ANALISANDO PADRÕES DE EXECUÇÃO")
        
        execution_analysis = {
            "fallback_pattern": {
                "description": "Todas as execuções são 'Correção: Fallback automático'",
                "implications": [
                    "Sistema nunca executa normalmente",
                    "Sempre ativa mecanismo de recuperação",
                    "Indica falha sistemática na execução principal"
                ],
                "root_cause_indicators": [
                    "Variáveis de ambiente não carregadas",
                    "Falha na inicialização do sistema",
                    "Erro de configuração fundamental"
                ]
            },
            "timing_analysis": {
                "consistent_21h_execution": True,
                "description": "Execuções sempre às 21h (horário das stories)",
                "implication": "Scheduler está funcionando, mas execução falha"
            },
            "duration_analysis": {
                "long_durations": True,
                "typical_duration": "23+ horas",
                "description": "Durações anormalmente longas",
                "implication": "Sistema fica em loop ou estado de espera prolongado"
            }
        }
        
        self.analysis_results["execution_patterns"] = execution_analysis
        
    def generate_root_cause_hypothesis(self):
        """Gerar hipóteses sobre a causa raiz"""
        self.logger.info("🎯 GERANDO HIPÓTESES SOBRE CAUSA RAIZ")
        
        hypotheses = [
            {
                "hypothesis": "VARIABLE_NAMING_LANGUAGE_MISMATCH",
                "probability": "VERY_HIGH",
                "description": "Código em inglês, variáveis configuradas em português",
                "evidence": [
                    "TOKEN_DE_ACESSO_DO_INSTAGRAM vs INSTAGRAM_ACCESS_TOKEN",
                    "Padrão consistente de nomenclatura em português",
                    "Sistema não reconhece variáveis existentes"
                ],
                "verification": "Verificar se código busca nomes em inglês",
                "fix": "Reconfigurar variáveis com nomes em inglês ou adaptar código"
            },
            {
                "hypothesis": "CRITICAL_VARIABLES_COMPLETELY_MISSING",
                "probability": "HIGH", 
                "description": "Variáveis essenciais não configuradas no Railway",
                "evidence": [
                    "OPENAI_API_KEY não visível",
                    "RAPIDAPI_KEY não visível", 
                    "TELEGRAM_* variáveis ausentes"
                ],
                "verification": "Verificar painel completo de variáveis",
                "fix": "Configurar todas as variáveis críticas"
            },
            {
                "hypothesis": "RAILWAY_ENVIRONMENT_LOADING_ISSUE",
                "probability": "MEDIUM",
                "description": "Railway não carrega variáveis corretamente para a aplicação",
                "evidence": [
                    "Variáveis visíveis no painel mas não no código",
                    "Padrão de fallback constante"
                ],
                "verification": "Testar carregamento de variáveis em runtime",
                "fix": "Investigar configuração de deployment"
            },
            {
                "hypothesis": "LTM_RECORDS_OUTDATED_OR_INCORRECT",
                "probability": "HIGH",
                "description": "Registros LTM não refletem estado atual",
                "evidence": [
                    "Discrepância entre LTM e realidade",
                    "Claims de configuração vs evidência visual"
                ],
                "verification": "Comparar timestamps dos registros",
                "fix": "Atualizar registros LTM com estado real"
            }
        ]
        
        self.analysis_results["root_cause_hypothesis"] = hypotheses
        
    def create_verification_checklist(self):
        """Criar checklist de verificação"""
        self.logger.info("✅ CRIANDO CHECKLIST DE VERIFICAÇÃO")
        
        verification_points = [
            {
                "category": "RAILWAY_VARIABLES",
                "checks": [
                    {
                        "item": "Verificar nomes exatos das variáveis no Railway",
                        "method": "Screenshot completo da aba Variáveis",
                        "expected": "Nomes em inglês conforme código",
                        "priority": "CRITICAL"
                    },
                    {
                        "item": "Confirmar presença de TODAS as variáveis críticas",
                        "method": "Checklist manual no painel Railway",
                        "expected": "6 variáveis críticas presentes",
                        "priority": "CRITICAL"
                    },
                    {
                        "item": "Testar carregamento de variáveis em runtime",
                        "method": "Script de verificação no Railway",
                        "expected": "Todas as variáveis acessíveis",
                        "priority": "HIGH"
                    }
                ]
            },
            {
                "category": "CODE_VERIFICATION", 
                "checks": [
                    {
                        "item": "Verificar nomes de variáveis no código",
                        "method": "Busca por os.getenv() no código",
                        "expected": "Nomes em inglês",
                        "priority": "HIGH"
                    },
                    {
                        "item": "Verificar tratamento de variáveis ausentes",
                        "method": "Análise do código de inicialização",
                        "expected": "Validação e logs de erro",
                        "priority": "MEDIUM"
                    }
                ]
            },
            {
                "category": "TELEGRAM_VERIFICATION",
                "checks": [
                    {
                        "item": "Verificar configuração Telegram no Railway",
                        "method": "Buscar TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID",
                        "expected": "Variáveis presentes e válidas",
                        "priority": "HIGH"
                    },
                    {
                        "item": "Testar envio de notificação manual",
                        "method": "Script de teste Telegram",
                        "expected": "Notificação recebida",
                        "priority": "MEDIUM"
                    }
                ]
            }
        ]
        
        self.analysis_results["verification_points"] = verification_points
        
    def save_analysis(self):
        """Salvar análise"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"railway_discrepancy_analysis_{timestamp}.json"
        filepath = Path(__file__).parent / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"📄 Análise salva: {filename}")
        
        # Criar resumo executivo
        self._create_executive_summary(timestamp)
        
        return filename
        
    def _create_executive_summary(self, timestamp):
        """Criar resumo executivo"""
        filename = f"railway_discrepancy_summary_{timestamp}.md"
        filepath = Path(__file__).parent / filename
        
        summary = f"""# Análise de Discrepância Railway - {datetime.now().strftime('%d/%m/%Y %H:%M')}

## 🎯 DESCOBERTAS CRÍTICAS

### 1. NOMENCLATURA DAS VARIÁVEIS (CRÍTICO)
- **Problema**: Variáveis configuradas em PORTUGUÊS no Railway
- **Código espera**: Nomes em INGLÊS
- **Exemplo**: `TOKEN_DE_ACESSO_DO_INSTAGRAM` vs `INSTAGRAM_ACCESS_TOKEN`
- **Impacto**: Sistema não consegue ler as variáveis

### 2. VARIÁVEIS CRÍTICAS AUSENTES
- ❌ `OPENAI_API_KEY` - Não visível nas imagens
- ❌ `RAPIDAPI_KEY` - Não visível nas imagens  
- ❌ `TELEGRAM_BOT_TOKEN` - Não visível nas imagens
- ❌ `TELEGRAM_CHAT_ID` - Não visível nas imagens

### 3. PADRÃO DE EXECUÇÃO ANÔMALO
- **Todas as execuções**: "Correção: Fallback automático"
- **Nunca**: Execução normal
- **Duração**: 23+ horas (anormal)
- **Implicação**: Sistema sempre em modo de recuperação

## 🔍 ANÁLISE DAS IMAGENS

### Variáveis Visíveis no Railway:
1. `AUTOCMD`
2. `TOKEN_DE_ACESSO_DO_INSTAGRAM` ⚠️ (nome em português)
3. `ID_DA_CONTA_COMERCIAL_DO_INSTAGRAM` ⚠️ (nome em português)
4. `VERIFICAÇÕES_DE_ENQUETE_MÁXIMO` ⚠️ (nome em português)
5. `INSTAGRAM_MAX_RETENTATIVAS`
6. `INTERVALO_DE_ENQUETE_DO_INSTAGRAM` ⚠️ (nome em português)
7. `TEMPO_LIMITE_DO_INSTAGRAM` ⚠️ (nome em português)

### Execuções Recentes:
- **23/10/25 21h26**: Correndo... (4m 13s) - Fallback
- **23/10/25 21h03**: Completo (23m 13s) - Fallback  
- **22/10/25 21h04**: Completo (23h 59m) - Fallback
- **21/10/25 21h16**: Completo (23h 47m) - Fallback

## 🚨 HIPÓTESES SOBRE CAUSA RAIZ

### HIPÓTESE PRINCIPAL (Probabilidade: MUITO ALTA)
**INCOMPATIBILIDADE DE NOMENCLATURA**
- Código busca variáveis em inglês
- Railway tem variáveis em português
- Sistema não consegue fazer a correspondência

### HIPÓTESE SECUNDÁRIA (Probabilidade: ALTA)  
**VARIÁVEIS CRÍTICAS AUSENTES**
- OpenAI, RapidAPI e Telegram não configurados
- Sistema falha silenciosamente
- Ativa modo fallback automaticamente

## 🔧 AÇÕES CORRETIVAS IMEDIATAS

### 1. RECONFIGURAR VARIÁVEIS (CRÍTICO)
```
Renomear no Railway:
TOKEN_DE_ACESSO_DO_INSTAGRAM → INSTAGRAM_ACCESS_TOKEN
ID_DA_CONTA_COMERCIAL_DO_INSTAGRAM → INSTAGRAM_BUSINESS_ACCOUNT_ID

Adicionar ausentes:
+ OPENAI_API_KEY
+ RAPIDAPI_KEY  
+ TELEGRAM_BOT_TOKEN
+ TELEGRAM_CHAT_ID
```

### 2. VERIFICAR CARREGAMENTO
- Criar script de teste de variáveis
- Executar no Railway para confirmar carregamento
- Monitorar logs de inicialização

### 3. TESTAR NOTIFICAÇÕES
- Verificar se Telegram funciona após correção
- Confirmar recebimento de notificações de teste

## 📋 CHECKLIST DE VERIFICAÇÃO

### Imediato (próximos 30 min):
- [ ] Renomear variáveis para inglês no Railway
- [ ] Adicionar variáveis ausentes
- [ ] Fazer redeploy da aplicação

### Validação (próximas 2 horas):
- [ ] Verificar logs de inicialização
- [ ] Testar carregamento de variáveis
- [ ] Confirmar execução normal (não fallback)
- [ ] Testar notificações Telegram

### Monitoramento (próximos dias):
- [ ] Acompanhar execuções às 21h
- [ ] Verificar se stories são publicadas
- [ ] Confirmar fim do padrão de fallback

## 🎯 CONCLUSÃO

A discrepância entre LTM e realidade é explicada por:
1. **Nomenclatura incorreta** das variáveis (português vs inglês)
2. **Variáveis críticas ausentes** no Railway
3. **Falhas silenciosas** que ativam modo fallback
4. **Registros LTM desatualizados** ou baseados em configuração local

A correção é **simples mas crítica**: reconfigurar variáveis com nomes corretos em inglês.
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        self.logger.info(f"📄 Resumo executivo salvo: {filename}")
        
    def run_complete_analysis(self):
        """Executar análise completa"""
        self.logger.info("🔍 INICIANDO ANÁLISE COMPLETA DE DISCREPÂNCIA")
        
        try:
            # 1. Analisar dados das imagens
            self.analyze_railway_images_data()
            
            # 2. Analisar registros LTM
            self.analyze_ltm_records()
            
            # 3. Analisar silêncio do Telegram
            self.analyze_telegram_silence()
            
            # 4. Analisar padrões de execução
            self.analyze_execution_patterns()
            
            # 5. Gerar hipóteses sobre causa raiz
            self.generate_root_cause_hypothesis()
            
            # 6. Criar checklist de verificação
            self.create_verification_checklist()
            
            # 7. Salvar análise
            report_filename = self.save_analysis()
            
            # Mostrar resumo
            critical_issues = len(self.analysis_results.get("critical_issues_from_images", []))
            hypotheses = len(self.analysis_results.get("root_cause_hypothesis", []))
            
            self.logger.info("✅ ANÁLISE COMPLETA FINALIZADA")
            self.logger.info(f"🔴 Problemas críticos identificados: {critical_issues}")
            self.logger.info(f"🎯 Hipóteses geradas: {hypotheses}")
            self.logger.info(f"📄 Relatório: {report_filename}")
            
            return report_filename
            
        except Exception as e:
            self.logger.error(f"❌ Erro durante análise: {e}")
            raise

def main():
    """Função principal"""
    analyzer = RailwayDiscrepancyAnalyzer()
    return analyzer.run_complete_analysis()

if __name__ == "__main__":
    main()