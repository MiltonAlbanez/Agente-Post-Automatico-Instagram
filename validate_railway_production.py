#!/usr/bin/env python3
"""
Script para validar configuração de produção no Railway
Verifica variáveis de ambiente, conectividade e configurações críticas
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
import sys

class RailwayProductionValidator:
    def __init__(self):
        self.report = {
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "validation_results": {},
            "critical_issues": [],
            "warnings": [],
            "recommendations": [],
            "status": "UNKNOWN"
        }
        
    def load_environment_variables(self):
        """Carrega variáveis de ambiente do arquivo .env"""
        try:
            env_file = Path(".env")
            if env_file.exists():
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '=' in line and not line.strip().startswith('#'):
                            key, value = line.strip().split('=', 1)
                            os.environ[key] = value.strip('"\'')
                return True
        except Exception as e:
            self.report["critical_issues"].append(f"Erro ao carregar .env: {str(e)}")
            return False
        return False
    
    def validate_required_variables(self):
        """Valida se todas as variáveis necessárias estão definidas"""
        print("🔍 Validando variáveis de ambiente obrigatórias...")
        
        required_vars = {
            "TELEGRAM_BOT_TOKEN": "Token do bot do Telegram",
            "TELEGRAM_CHAT_ID": "ID do chat do Telegram",
            "OPENAI_API_KEY": "Chave da API OpenAI",
            "RAPIDAPI_KEY": "Chave da RapidAPI",
            "REPLICATE_TOKEN": "Token do Replicate",
            "INSTAGRAM_BUSINESS_ACCOUNT_ID": "ID da conta business Instagram",
            "INSTAGRAM_ACCESS_TOKEN": "Token de acesso Instagram"
        }
        
        missing_vars = []
        configured_vars = []
        
        for var, description in required_vars.items():
            value = os.getenv(var)
            if not value:
                missing_vars.append(f"{var} ({description})")
            else:
                configured_vars.append(var)
                # Mascarar valores sensíveis no log
                masked_value = value[:8] + "..." if len(value) > 8 else "***"
                print(f"  ✅ {var}: {masked_value}")
        
        if missing_vars:
            self.report["critical_issues"].extend([f"Variável não definida: {var}" for var in missing_vars])
            print(f"  ❌ Variáveis faltando: {len(missing_vars)}")
            for var in missing_vars:
                print(f"    - {var}")
        
        self.report["validation_results"]["environment_variables"] = {
            "configured": len(configured_vars),
            "missing": len(missing_vars),
            "configured_vars": configured_vars,
            "missing_vars": missing_vars,
            "status": "PASS" if not missing_vars else "FAIL"
        }
        
        return len(missing_vars) == 0
    
    def validate_telegram_connectivity(self):
        """Testa conectividade com API do Telegram"""
        print("📱 Testando conectividade com Telegram...")
        
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        if not token or not chat_id:
            self.report["critical_issues"].append("Credenciais do Telegram não configuradas")
            self.report["validation_results"]["telegram"] = {"status": "FAIL", "error": "Credenciais não configuradas"}
            return False
        
        try:
            # Teste getMe
            response = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
            if response.status_code == 200:
                bot_info = response.json()
                bot_name = bot_info.get("result", {}).get("username", "Unknown")
                print(f"  ✅ Bot conectado: @{bot_name}")
                
                # Teste getChat
                chat_response = requests.get(f"https://api.telegram.org/bot{token}/getChat", 
                                           params={"chat_id": chat_id}, timeout=10)
                if chat_response.status_code == 200:
                    print(f"  ✅ Chat acessível: {chat_id}")
                    
                    self.report["validation_results"]["telegram"] = {
                        "status": "PASS",
                        "bot_username": bot_name,
                        "chat_accessible": True
                    }
                    return True
                else:
                    error_msg = f"Chat inacessível: {chat_response.status_code}"
                    self.report["critical_issues"].append(error_msg)
                    print(f"  ❌ {error_msg}")
            else:
                error_msg = f"Bot inacessível: {response.status_code}"
                self.report["critical_issues"].append(error_msg)
                print(f"  ❌ {error_msg}")
                
        except Exception as e:
            error_msg = f"Erro de conectividade Telegram: {str(e)}"
            self.report["critical_issues"].append(error_msg)
            print(f"  ❌ {error_msg}")
        
        self.report["validation_results"]["telegram"] = {"status": "FAIL", "error": "Conectividade falhou"}
        return False
    
    def validate_instagram_credentials(self):
        """Valida credenciais do Instagram"""
        print("📸 Validando credenciais do Instagram...")
        
        account_id = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
        access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        
        if not account_id or not access_token:
            self.report["critical_issues"].append("Credenciais do Instagram não configuradas")
            self.report["validation_results"]["instagram"] = {"status": "FAIL", "error": "Credenciais não configuradas"}
            return False
        
        try:
            # Teste básico da API do Instagram
            url = f"https://graph.facebook.com/v18.0/{account_id}"
            params = {
                "fields": "name,username",
                "access_token": access_token
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                username = data.get("username", "Unknown")
                print(f"  ✅ Conta Instagram conectada: @{username}")
                
                self.report["validation_results"]["instagram"] = {
                    "status": "PASS",
                    "username": username,
                    "account_id": account_id
                }
                return True
            else:
                error_msg = f"Credenciais Instagram inválidas: {response.status_code}"
                self.report["critical_issues"].append(error_msg)
                print(f"  ❌ {error_msg}")
                
        except Exception as e:
            error_msg = f"Erro ao validar Instagram: {str(e)}"
            self.report["critical_issues"].append(error_msg)
            print(f"  ❌ {error_msg}")
        
        self.report["validation_results"]["instagram"] = {"status": "FAIL", "error": "Validação falhou"}
        return False
    
    def validate_production_settings(self):
        """Valida configurações específicas de produção"""
        print("⚙️ Validando configurações de produção...")
        
        production_vars = {
            "DRY_RUN": "false",
            "SIMULATION_MODE": "false", 
            "PRODUCTION_MODE": "true",
            "REAL_POSTING": "true"
        }
        
        issues = []
        warnings = []
        
        for var, expected in production_vars.items():
            current = os.getenv(var, "").lower()
            if current != expected:
                if var in ["PRODUCTION_MODE", "REAL_POSTING"]:
                    issues.append(f"{var} deve ser '{expected}' em produção (atual: '{current}')")
                else:
                    warnings.append(f"{var} recomendado '{expected}' em produção (atual: '{current}')")
        
        if issues:
            self.report["critical_issues"].extend(issues)
            print(f"  ❌ Problemas críticos: {len(issues)}")
            for issue in issues:
                print(f"    - {issue}")
        
        if warnings:
            self.report["warnings"].extend(warnings)
            print(f"  ⚠️ Avisos: {len(warnings)}")
            for warning in warnings:
                print(f"    - {warning}")
        
        if not issues and not warnings:
            print("  ✅ Configurações de produção corretas")
        
        self.report["validation_results"]["production_settings"] = {
            "status": "PASS" if not issues else "FAIL",
            "critical_issues": len(issues),
            "warnings": len(warnings)
        }
        
        return len(issues) == 0
    
    def check_railway_files(self):
        """Verifica arquivos específicos do Railway"""
        print("🚂 Verificando arquivos do Railway...")
        
        railway_files = [
            "railway_env_commands.txt",
            "src/config.py",
            "automation/scheduler.py",
            "requirements.txt"
        ]
        
        missing_files = []
        found_files = []
        
        for file_path in railway_files:
            if Path(file_path).exists():
                found_files.append(file_path)
                print(f"  ✅ {file_path}")
            else:
                missing_files.append(file_path)
                print(f"  ❌ {file_path} não encontrado")
        
        if missing_files:
            self.report["critical_issues"].extend([f"Arquivo faltando: {f}" for f in missing_files])
        
        self.report["validation_results"]["railway_files"] = {
            "status": "PASS" if not missing_files else "FAIL",
            "found": found_files,
            "missing": missing_files
        }
        
        return len(missing_files) == 0
    
    def generate_railway_commands(self):
        """Gera comandos do Railway para configurar variáveis"""
        print("📝 Gerando comandos do Railway...")
        
        commands = []
        env_vars = {}
        
        # Carregar variáveis do .env
        env_file = Path(".env")
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        env_vars[key] = value.strip('"\'')
        
        # Gerar comandos railway variables set
        for key, value in env_vars.items():
            commands.append(f'railway variables set {key}="{value}"')
        
        # Salvar comandos
        commands_file = "railway_production_setup.txt"
        with open(commands_file, 'w', encoding='utf-8') as f:
            f.write("# Comandos para configurar variáveis de ambiente no Railway\n")
            f.write(f"# Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            for cmd in commands:
                f.write(cmd + "\n")
        
        print(f"  ✅ Comandos salvos em: {commands_file}")
        
        self.report["validation_results"]["railway_commands"] = {
            "status": "PASS",
            "commands_generated": len(commands),
            "file": commands_file
        }
        
        return True
    
    def run_validation(self):
        """Executa todas as validações"""
        print("🔍 VALIDAÇÃO DE PRODUÇÃO NO RAILWAY")
        print("=" * 50)
        
        # Carregar variáveis de ambiente
        self.load_environment_variables()
        
        # Executar validações
        validations = [
            ("environment_variables", self.validate_required_variables),
            ("telegram_connectivity", self.validate_telegram_connectivity),
            ("instagram_credentials", self.validate_instagram_credentials),
            ("production_settings", self.validate_production_settings),
            ("railway_files", self.check_railway_files),
            ("railway_commands", self.generate_railway_commands)
        ]
        
        passed = 0
        total = len(validations)
        
        for name, validation_func in validations:
            try:
                if validation_func():
                    passed += 1
            except Exception as e:
                self.report["critical_issues"].append(f"Erro na validação {name}: {str(e)}")
        
        # Determinar status final
        success_rate = (passed / total) * 100
        if success_rate == 100:
            self.report["status"] = "SUCCESS"
        elif success_rate >= 80:
            self.report["status"] = "PARTIAL_SUCCESS"
        else:
            self.report["status"] = "CRITICAL_ISSUES_FOUND"
        
        # Gerar recomendações
        if self.report["critical_issues"]:
            self.report["recommendations"].append("Corrigir problemas críticos antes do deploy")
        if self.report["warnings"]:
            self.report["recommendations"].append("Revisar configurações com avisos")
        if success_rate == 100:
            self.report["recommendations"].append("Configuração pronta para produção no Railway")
        
        # Salvar relatório
        report_file = f"railway_production_validation_{self.report['timestamp']}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Relatório salvo: {Path(report_file).absolute()}")
        
        # Resumo final
        print(f"\n📊 RESUMO DA VALIDAÇÃO:")
        print(f"Status: {self.report['status']}")
        print(f"Validações aprovadas: {passed}/{total}")
        print(f"Taxa de sucesso: {success_rate:.1f}%")
        
        if self.report["critical_issues"]:
            print(f"\n❌ PROBLEMAS CRÍTICOS ({len(self.report['critical_issues'])}):")
            for issue in self.report["critical_issues"]:
                print(f"  • {issue}")
        
        if self.report["warnings"]:
            print(f"\n⚠️ AVISOS ({len(self.report['warnings'])}):")
            for warning in self.report["warnings"]:
                print(f"  • {warning}")
        
        if self.report["recommendations"]:
            print(f"\n💡 RECOMENDAÇÕES:")
            for rec in self.report["recommendations"]:
                print(f"  • {rec}")
        
        if success_rate == 100:
            print(f"\n🎉 CONFIGURAÇÃO PRONTA PARA PRODUÇÃO NO RAILWAY!")
        elif success_rate >= 80:
            print(f"\n⚠️ CONFIGURAÇÃO PARCIALMENTE PRONTA - REVISAR PROBLEMAS")
        else:
            print(f"\n❌ CONFIGURAÇÃO NÃO PRONTA - CORRIGIR PROBLEMAS CRÍTICOS")
        
        return success_rate == 100

if __name__ == "__main__":
    validator = RailwayProductionValidator()
    success = validator.run_validation()
    sys.exit(0 if success else 1)