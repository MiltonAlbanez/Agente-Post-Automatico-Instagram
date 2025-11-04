#!/usr/bin/env python3
"""
Diagnóstico Específico para Problema Telegram 404
Identifica e corrige problemas de conectividade com o Telegram Bot API
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TelegramDiagnostic:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "diagnostic_version": "1.0",
            "status": "RUNNING",
            "issues_found": [],
            "fixes_applied": [],
            "recommendations": []
        }
        
    def check_environment_variables(self):
        """Verificar variáveis de ambiente do Telegram"""
        logger.info("🔍 Verificando variáveis de ambiente do Telegram...")
        
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        env_status = {
            "bot_token": {
                "exists": bot_token is not None,
                "format_valid": False,
                "length": len(bot_token) if bot_token else 0
            },
            "chat_id": {
                "exists": chat_id is not None,
                "format_valid": False,
                "value": chat_id if chat_id else None
            }
        }
        
        # Validar formato do bot token
        if bot_token:
            if ":" in bot_token and len(bot_token.split(":")) == 2:
                bot_id, bot_hash = bot_token.split(":", 1)
                if bot_id.isdigit() and len(bot_hash) >= 35:
                    env_status["bot_token"]["format_valid"] = True
                else:
                    self.results["issues_found"].append({
                        "type": "INVALID_BOT_TOKEN_FORMAT",
                        "description": "Bot token não tem formato válido (deve ser: 123456789:ABC-DEF...)",
                        "severity": "HIGH"
                    })
            else:
                self.results["issues_found"].append({
                    "type": "MALFORMED_BOT_TOKEN",
                    "description": "Bot token malformado - deve conter ':'",
                    "severity": "HIGH"
                })
        else:
            self.results["issues_found"].append({
                "type": "MISSING_BOT_TOKEN",
                "description": "TELEGRAM_BOT_TOKEN não está definido",
                "severity": "CRITICAL"
            })
            
        # Validar formato do chat ID
        if chat_id:
            if chat_id.startswith("-") and chat_id[1:].isdigit():
                env_status["chat_id"]["format_valid"] = True
            elif chat_id.isdigit():
                env_status["chat_id"]["format_valid"] = True
            else:
                self.results["issues_found"].append({
                    "type": "INVALID_CHAT_ID_FORMAT",
                    "description": f"Chat ID '{chat_id}' não tem formato válido",
                    "severity": "HIGH"
                })
        else:
            self.results["issues_found"].append({
                "type": "MISSING_CHAT_ID",
                "description": "TELEGRAM_CHAT_ID não está definido",
                "severity": "CRITICAL"
            })
            
        self.results["environment_check"] = env_status
        return env_status
        
    def test_bot_api_connectivity(self):
        """Testar conectividade com a API do Telegram"""
        logger.info("🌐 Testando conectividade com API do Telegram...")
        
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            return {"error": "Bot token não disponível"}
            
        api_tests = {
            "getMe": {"status": "PENDING", "response": None, "error": None},
            "getChat": {"status": "PENDING", "response": None, "error": None},
            "sendMessage": {"status": "PENDING", "response": None, "error": None}
        }
        
        # Teste 1: getMe (verificar se o bot existe)
        try:
            url = f"https://api.telegram.org/bot{bot_token}/getMe"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    api_tests["getMe"]["status"] = "SUCCESS"
                    api_tests["getMe"]["response"] = {
                        "bot_id": data["result"]["id"],
                        "bot_username": data["result"]["username"],
                        "bot_name": data["result"]["first_name"]
                    }
                    logger.info(f"✅ Bot encontrado: @{data['result']['username']}")
                else:
                    api_tests["getMe"]["status"] = "FAILED"
                    api_tests["getMe"]["error"] = data.get("description", "Erro desconhecido")
            elif response.status_code == 404:
                api_tests["getMe"]["status"] = "FAILED"
                api_tests["getMe"]["error"] = "Bot não encontrado (404) - Token inválido"
                self.results["issues_found"].append({
                    "type": "BOT_NOT_FOUND_404",
                    "description": "Bot token inválido - API retornou 404",
                    "severity": "CRITICAL"
                })
            elif response.status_code == 401:
                api_tests["getMe"]["status"] = "FAILED"
                api_tests["getMe"]["error"] = "Não autorizado (401) - Token inválido"
                self.results["issues_found"].append({
                    "type": "UNAUTHORIZED_401",
                    "description": "Token não autorizado - verifique se está correto",
                    "severity": "CRITICAL"
                })
            else:
                api_tests["getMe"]["status"] = "FAILED"
                api_tests["getMe"]["error"] = f"HTTP {response.status_code}: {response.text}"
                
        except requests.exceptions.RequestException as e:
            api_tests["getMe"]["status"] = "ERROR"
            api_tests["getMe"]["error"] = f"Erro de conexão: {str(e)}"
            self.results["issues_found"].append({
                "type": "NETWORK_ERROR",
                "description": f"Erro de rede ao conectar com Telegram API: {str(e)}",
                "severity": "HIGH"
            })
            
        # Teste 2: getChat (verificar se o chat existe e o bot tem acesso)
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if chat_id and api_tests["getMe"]["status"] == "SUCCESS":
            try:
                url = f"https://api.telegram.org/bot{bot_token}/getChat"
                params = {"chat_id": chat_id}
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("ok"):
                        api_tests["getChat"]["status"] = "SUCCESS"
                        api_tests["getChat"]["response"] = {
                            "chat_type": data["result"]["type"],
                            "chat_title": data["result"].get("title", "N/A")
                        }
                        logger.info(f"✅ Chat acessível: {data['result'].get('title', chat_id)}")
                    else:
                        api_tests["getChat"]["status"] = "FAILED"
                        api_tests["getChat"]["error"] = data.get("description", "Erro desconhecido")
                elif response.status_code == 400:
                    api_tests["getChat"]["status"] = "FAILED"
                    api_tests["getChat"]["error"] = "Chat não encontrado ou bot não tem acesso"
                    self.results["issues_found"].append({
                        "type": "CHAT_ACCESS_DENIED",
                        "description": f"Bot não tem acesso ao chat {chat_id}",
                        "severity": "HIGH"
                    })
                else:
                    api_tests["getChat"]["status"] = "FAILED"
                    api_tests["getChat"]["error"] = f"HTTP {response.status_code}: {response.text}"
                    
            except requests.exceptions.RequestException as e:
                api_tests["getChat"]["status"] = "ERROR"
                api_tests["getChat"]["error"] = f"Erro de conexão: {str(e)}"
                
        # Teste 3: sendMessage (teste de envio real)
        if (chat_id and 
            api_tests["getMe"]["status"] == "SUCCESS" and 
            api_tests["getChat"]["status"] == "SUCCESS"):
            
            try:
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                payload = {
                    "chat_id": chat_id,
                    "text": f"🔧 Teste de diagnóstico Telegram - {datetime.now().strftime('%H:%M:%S')}"
                }
                response = requests.post(url, data=payload, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("ok"):
                        api_tests["sendMessage"]["status"] = "SUCCESS"
                        api_tests["sendMessage"]["response"] = {
                            "message_id": data["result"]["message_id"],
                            "sent_at": data["result"]["date"]
                        }
                        logger.info("✅ Mensagem de teste enviada com sucesso")
                    else:
                        api_tests["sendMessage"]["status"] = "FAILED"
                        api_tests["sendMessage"]["error"] = data.get("description", "Erro desconhecido")
                else:
                    api_tests["sendMessage"]["status"] = "FAILED"
                    api_tests["sendMessage"]["error"] = f"HTTP {response.status_code}: {response.text}"
                    
            except requests.exceptions.RequestException as e:
                api_tests["sendMessage"]["status"] = "ERROR"
                api_tests["sendMessage"]["error"] = f"Erro de conexão: {str(e)}"
                
        self.results["api_connectivity"] = api_tests
        return api_tests
        
    def check_configuration_files(self):
        """Verificar arquivos de configuração"""
        logger.info("📁 Verificando arquivos de configuração...")
        
        config_files = {
            "accounts.json": {"exists": False, "telegram_config": None},
            "config/notification_config.json": {"exists": False, "telegram_config": None},
            "railway_env_commands.txt": {"exists": False, "telegram_vars": None},
            "CREDENCIAIS_PERMANENTES.json": {"exists": False, "telegram_config": None}
        }
        
        project_root = Path(__file__).parent
        
        # Verificar accounts.json
        accounts_path = project_root / "accounts.json"
        if accounts_path.exists():
            try:
                with open(accounts_path, 'r', encoding='utf-8') as f:
                    accounts = json.load(f)
                
                config_files["accounts.json"]["exists"] = True
                telegram_accounts = []
                
                for acc in accounts:
                    if acc.get("telegram_bot_token") or acc.get("telegram_chat_id"):
                        telegram_accounts.append({
                            "name": acc.get("nome", "UNNAMED"),
                            "has_bot_token": bool(acc.get("telegram_bot_token")),
                            "has_chat_id": bool(acc.get("telegram_chat_id"))
                        })
                        
                config_files["accounts.json"]["telegram_config"] = telegram_accounts
                
            except Exception as e:
                config_files["accounts.json"]["error"] = str(e)
                
        # Verificar notification_config.json
        notification_config_path = project_root / "config" / "notification_config.json"
        if notification_config_path.exists():
            try:
                with open(notification_config_path, 'r', encoding='utf-8') as f:
                    notification_config = json.load(f)
                
                config_files["config/notification_config.json"]["exists"] = True
                telegram_config = notification_config.get("telegram", {})
                config_files["config/notification_config.json"]["telegram_config"] = {
                    "has_bot_token": bool(telegram_config.get("bot_token")),
                    "has_chat_id": bool(telegram_config.get("chat_id")),
                    "enabled": telegram_config.get("enabled", False)
                }
                
            except Exception as e:
                config_files["config/notification_config.json"]["error"] = str(e)
                
        # Verificar railway_env_commands.txt
        railway_env_path = project_root / "railway_env_commands.txt"
        if railway_env_path.exists():
            try:
                with open(railway_env_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                config_files["railway_env_commands.txt"]["exists"] = True
                
                # Procurar por variáveis do Telegram
                import re
                bot_token_match = re.search(r'TELEGRAM_BOT_TOKEN[=\s]+"([^"]+)"', content)
                chat_id_match = re.search(r'TELEGRAM_CHAT_ID[=\s]+"([^"]+)"', content)
                
                config_files["railway_env_commands.txt"]["telegram_vars"] = {
                    "has_bot_token": bool(bot_token_match),
                    "has_chat_id": bool(chat_id_match),
                    "bot_token_value": bot_token_match.group(1) if bot_token_match else None,
                    "chat_id_value": chat_id_match.group(1) if chat_id_match else None
                }
                
            except Exception as e:
                config_files["railway_env_commands.txt"]["error"] = str(e)
                
        # Verificar CREDENCIAIS_PERMANENTES.json
        credentials_path = project_root / "CREDENCIAIS_PERMANENTES.json"
        if credentials_path.exists():
            try:
                with open(credentials_path, 'r', encoding='utf-8') as f:
                    credentials = json.load(f)
                
                config_files["CREDENCIAIS_PERMANENTES.json"]["exists"] = True
                config_files["CREDENCIAIS_PERMANENTES.json"]["telegram_config"] = {
                    "has_bot_token": bool(credentials.get("TELEGRAM_BOT_TOKEN")),
                    "has_chat_id": bool(credentials.get("TELEGRAM_CHAT_ID"))
                }
                
            except Exception as e:
                config_files["CREDENCIAIS_PERMANENTES.json"]["error"] = str(e)
                
        self.results["configuration_files"] = config_files
        return config_files
        
    def generate_fix_recommendations(self):
        """Gerar recomendações de correção baseadas nos problemas encontrados"""
        logger.info("💡 Gerando recomendações de correção...")
        
        recommendations = []
        
        # Analisar problemas encontrados
        for issue in self.results["issues_found"]:
            if issue["type"] == "BOT_NOT_FOUND_404":
                recommendations.append({
                    "priority": "CRITICAL",
                    "action": "REPLACE_BOT_TOKEN",
                    "description": "Substituir TELEGRAM_BOT_TOKEN por um token válido",
                    "steps": [
                        "1. Acesse @BotFather no Telegram",
                        "2. Use /newbot para criar um novo bot ou /token para regenerar token existente",
                        "3. Copie o token fornecido (formato: 123456789:ABC-DEF...)",
                        "4. Atualize a variável TELEGRAM_BOT_TOKEN no Railway",
                        "5. Reinicie o serviço"
                    ]
                })
                
            elif issue["type"] == "CHAT_ACCESS_DENIED":
                recommendations.append({
                    "priority": "HIGH",
                    "action": "FIX_CHAT_ACCESS",
                    "description": "Corrigir acesso do bot ao chat",
                    "steps": [
                        "1. Adicione o bot ao grupo/canal desejado",
                        "2. Conceda permissões de administrador se necessário",
                        "3. Use @userinfobot para obter o chat_id correto",
                        "4. Atualize TELEGRAM_CHAT_ID no Railway",
                        "5. Teste o envio de mensagem"
                    ]
                })
                
            elif issue["type"] in ["MISSING_BOT_TOKEN", "MISSING_CHAT_ID"]:
                recommendations.append({
                    "priority": "CRITICAL",
                    "action": "SET_ENVIRONMENT_VARIABLES",
                    "description": "Configurar variáveis de ambiente do Telegram",
                    "steps": [
                        "1. railway variables set TELEGRAM_BOT_TOKEN=\"seu_token_aqui\"",
                        "2. railway variables set TELEGRAM_CHAT_ID=\"seu_chat_id_aqui\"",
                        "3. Verificar com: railway variables",
                        "4. Reiniciar o serviço: railway up"
                    ]
                })
                
        # Recomendações gerais
        if not any(issue["type"].startswith("BOT_") for issue in self.results["issues_found"]):
            recommendations.append({
                "priority": "LOW",
                "action": "PREVENTIVE_MONITORING",
                "description": "Implementar monitoramento preventivo",
                "steps": [
                    "1. Configurar health check para Telegram API",
                    "2. Implementar retry automático para falhas temporárias",
                    "3. Adicionar alertas para problemas de conectividade",
                    "4. Criar backup de configurações"
                ]
            })
            
        self.results["recommendations"] = recommendations
        return recommendations
        
    def apply_automatic_fixes(self):
        """Aplicar correções automáticas quando possível"""
        logger.info("🔧 Aplicando correções automáticas...")
        
        fixes_applied = []
        
        # Verificar se existem credenciais válidas em arquivos de configuração
        config_files = self.results.get("configuration_files", {})
        
        # Tentar carregar credenciais do railway_env_commands.txt
        railway_config = config_files.get("railway_env_commands.txt", {})
        if (railway_config.get("exists") and 
            railway_config.get("telegram_vars", {}).get("has_bot_token") and
            railway_config.get("telegram_vars", {}).get("has_chat_id")):
            
            bot_token = railway_config["telegram_vars"]["bot_token_value"]
            chat_id = railway_config["telegram_vars"]["chat_id_value"]
            
            if bot_token and chat_id:
                os.environ["TELEGRAM_BOT_TOKEN"] = bot_token
                os.environ["TELEGRAM_CHAT_ID"] = chat_id
                
                fixes_applied.append({
                    "type": "ENVIRONMENT_VARIABLES_LOADED",
                    "description": "Credenciais carregadas do railway_env_commands.txt",
                    "success": True
                })
                
        # Tentar carregar credenciais do CREDENCIAIS_PERMANENTES.json
        credentials_config = config_files.get("CREDENCIAIS_PERMANENTES.json", {})
        if (credentials_config.get("exists") and 
            credentials_config.get("telegram_config", {}).get("has_bot_token") and
            credentials_config.get("telegram_config", {}).get("has_chat_id")):
            
            try:
                credentials_path = Path(__file__).parent / "CREDENCIAIS_PERMANENTES.json"
                with open(credentials_path, 'r', encoding='utf-8') as f:
                    credentials = json.load(f)
                
                if not os.getenv("TELEGRAM_BOT_TOKEN"):
                    os.environ["TELEGRAM_BOT_TOKEN"] = credentials["TELEGRAM_BOT_TOKEN"]
                if not os.getenv("TELEGRAM_CHAT_ID"):
                    os.environ["TELEGRAM_CHAT_ID"] = credentials["TELEGRAM_CHAT_ID"]
                    
                fixes_applied.append({
                    "type": "CREDENTIALS_LOADED_FROM_FILE",
                    "description": "Credenciais carregadas do CREDENCIAIS_PERMANENTES.json",
                    "success": True
                })
                
            except Exception as e:
                fixes_applied.append({
                    "type": "CREDENTIALS_LOAD_FAILED",
                    "description": f"Falha ao carregar credenciais: {str(e)}",
                    "success": False
                })
                
        self.results["fixes_applied"] = fixes_applied
        return fixes_applied
        
    def run_full_diagnostic(self):
        """Executar diagnóstico completo"""
        logger.info("🚀 Iniciando diagnóstico completo do Telegram...")
        
        try:
            # 1. Verificar variáveis de ambiente
            self.check_environment_variables()
            
            # 2. Verificar arquivos de configuração
            self.check_configuration_files()
            
            # 3. Aplicar correções automáticas
            self.apply_automatic_fixes()
            
            # 4. Testar conectividade API
            self.test_bot_api_connectivity()
            
            # 5. Gerar recomendações
            self.generate_fix_recommendations()
            
            # Determinar status final
            critical_issues = [i for i in self.results["issues_found"] if i["severity"] == "CRITICAL"]
            high_issues = [i for i in self.results["issues_found"] if i["severity"] == "HIGH"]
            
            if critical_issues:
                self.results["status"] = "CRITICAL_ISSUES_FOUND"
            elif high_issues:
                self.results["status"] = "ISSUES_FOUND"
            else:
                self.results["status"] = "HEALTHY"
                
            logger.info(f"✅ Diagnóstico concluído - Status: {self.results['status']}")
            
        except Exception as e:
            self.results["status"] = "DIAGNOSTIC_ERROR"
            self.results["error"] = str(e)
            logger.error(f"❌ Erro durante diagnóstico: {str(e)}")
            
        return self.results
        
    def save_report(self):
        """Salvar relatório de diagnóstico"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = Path(__file__).parent / f"telegram_diagnostic_report_{timestamp}.json"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📄 Relatório salvo em: {report_path}")
            return report_path
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar relatório: {str(e)}")
            return None

def main():
    """Função principal"""
    print("🔧 DIAGNÓSTICO TELEGRAM 404 - AGENTE POST INSTAGRAM")
    print("=" * 60)
    
    diagnostic = TelegramDiagnostic()
    
    # Executar diagnóstico completo
    results = diagnostic.run_full_diagnostic()
    
    # Salvar relatório
    report_path = diagnostic.save_report()
    
    # Exibir resumo
    print("\n📊 RESUMO DO DIAGNÓSTICO:")
    print(f"Status: {results['status']}")
    print(f"Problemas encontrados: {len(results['issues_found'])}")
    print(f"Correções aplicadas: {len(results['fixes_applied'])}")
    print(f"Recomendações: {len(results['recommendations'])}")
    
    if results["issues_found"]:
        print("\n⚠️ PROBLEMAS ENCONTRADOS:")
        for issue in results["issues_found"]:
            print(f"  • {issue['type']}: {issue['description']} ({issue['severity']})")
            
    if results["recommendations"]:
        print("\n💡 PRÓXIMAS AÇÕES RECOMENDADAS:")
        for rec in results["recommendations"]:
            print(f"  • {rec['action']} ({rec['priority']})")
            print(f"    {rec['description']}")
            
    if report_path:
        print(f"\n📄 Relatório detalhado: {report_path}")
        
    return results

if __name__ == "__main__":
    main()