#!/usr/bin/env python3
"""
SCRIPT DE VERIFICAÇÃO PÓS-CORREÇÃO RAILWAY
==========================================

Este script deve ser executado APÓS aplicar as correções no Railway para verificar
se todas as variáveis de ambiente estão corretamente configuradas.

Uso:
    python verificacao_pos_correcao_railway.py

Autor: Sistema de Análise Railway
Data: 23/10/2024
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Tuple, Any

class RailwayPostCorrectionVerifier:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = {
            "timestamp": self.timestamp,
            "verification_status": "UNKNOWN",
            "critical_variables": {},
            "optional_variables": {},
            "renamed_variables": {},
            "missing_variables": [],
            "configuration_errors": [],
            "system_status": "UNKNOWN",
            "recommendations": []
        }
        
        # Variáveis críticas que DEVEM existir
        self.critical_vars = {
            "INSTAGRAM_ACCESS_TOKEN": "Token de acesso do Instagram (renomeado)",
            "INSTAGRAM_BUSINESS_ACCOUNT_ID": "ID da conta comercial Instagram (renomeado)",
            "OPENAI_API_KEY": "Chave API OpenAI (nova)",
            "RAPIDAPI_KEY": "Chave API RapidAPI (nova)",
            "TELEGRAM_BOT_TOKEN": "Token do bot Telegram (nova)",
            "TELEGRAM_CHAT_ID": "ID do chat Telegram (nova)",
            "POSTGRES_DSN": "String de conexão PostgreSQL (existente)",
            "DATABASE_URL": "URL do banco de dados (existente)"
        }
        
        # Variáveis opcionais recomendadas
        self.optional_vars = {
            "SUPABASE_URL": "URL do Supabase",
            "SUPABASE_SERVICE_KEY": "Chave de serviço Supabase",
            "SUPABASE_BUCKET": "Bucket do Supabase",
            "SUPABASE_ANON_KEY": "Chave anônima Supabase",
            "RAPIDAPI_HOST": "Host específico RapidAPI",
            "RAILWAY_ENVIRONMENT": "Ambiente Railway",
            "AUTOCMD": "Comando automático"
        }
        
        # Variáveis antigas que NÃO devem mais existir
        self.deprecated_vars = {
            "TOKEN_DE_ACESSO_DO_INSTAGRAM": "Deve ter sido renomeado para INSTAGRAM_ACCESS_TOKEN",
            "ID_DA_CONTA_COMERCIAL_DO_INSTAGRAM": "Deve ter sido renomeado para INSTAGRAM_BUSINESS_ACCOUNT_ID"
        }

    def print_header(self):
        """Imprime cabeçalho do relatório"""
        print("=" * 80)
        print("🔍 VERIFICAÇÃO PÓS-CORREÇÃO RAILWAY")
        print("=" * 80)
        print(f"Timestamp: {self.timestamp}")
        print(f"Ambiente: {os.getenv('RAILWAY_ENVIRONMENT', 'LOCAL')}")
        print("-" * 80)

    def check_critical_variables(self) -> bool:
        """Verifica variáveis críticas"""
        print("\n🚨 VERIFICANDO VARIÁVEIS CRÍTICAS...")
        all_critical_present = True
        
        for var_name, description in self.critical_vars.items():
            value = os.getenv(var_name)
            
            if value:
                # Mascarar valores sensíveis para exibição
                display_value = self.mask_sensitive_value(var_name, value)
                print(f"✅ {var_name}: {display_value}")
                self.results["critical_variables"][var_name] = {
                    "present": True,
                    "description": description,
                    "value_length": len(value),
                    "masked_value": display_value
                }
            else:
                print(f"❌ {var_name}: AUSENTE")
                self.results["critical_variables"][var_name] = {
                    "present": False,
                    "description": description,
                    "value_length": 0,
                    "masked_value": None
                }
                self.results["missing_variables"].append(var_name)
                all_critical_present = False
        
        return all_critical_present

    def check_optional_variables(self):
        """Verifica variáveis opcionais"""
        print("\n📋 VERIFICANDO VARIÁVEIS OPCIONAIS...")
        
        for var_name, description in self.optional_vars.items():
            value = os.getenv(var_name)
            
            if value:
                display_value = self.mask_sensitive_value(var_name, value)
                print(f"✅ {var_name}: {display_value}")
                self.results["optional_variables"][var_name] = {
                    "present": True,
                    "description": description,
                    "value_length": len(value),
                    "masked_value": display_value
                }
            else:
                print(f"⚠️  {var_name}: AUSENTE (opcional)")
                self.results["optional_variables"][var_name] = {
                    "present": False,
                    "description": description,
                    "value_length": 0,
                    "masked_value": None
                }

    def check_deprecated_variables(self):
        """Verifica se variáveis antigas ainda existem (não devem)"""
        print("\n🗑️  VERIFICANDO VARIÁVEIS DEPRECIADAS...")
        
        deprecated_found = False
        for var_name, message in self.deprecated_vars.items():
            value = os.getenv(var_name)
            
            if value:
                print(f"⚠️  {var_name}: AINDA EXISTE - {message}")
                self.results["configuration_errors"].append({
                    "type": "deprecated_variable_exists",
                    "variable": var_name,
                    "message": message
                })
                deprecated_found = True
            else:
                print(f"✅ {var_name}: Corretamente removido/renomeado")
        
        if not deprecated_found:
            print("✅ Nenhuma variável depreciada encontrada")

    def validate_variable_formats(self):
        """Valida formatos específicos de variáveis"""
        print("\n🔍 VALIDANDO FORMATOS DE VARIÁVEIS...")
        
        # Validar OPENAI_API_KEY
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            if openai_key.startswith("sk-"):
                print("✅ OPENAI_API_KEY: Formato válido")
            else:
                print("⚠️  OPENAI_API_KEY: Formato suspeito (deve começar com 'sk-')")
                self.results["configuration_errors"].append({
                    "type": "invalid_format",
                    "variable": "OPENAI_API_KEY",
                    "message": "Deve começar com 'sk-'"
                })
        
        # Validar TELEGRAM_BOT_TOKEN
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if telegram_token:
            if ":" in telegram_token and len(telegram_token) > 40:
                print("✅ TELEGRAM_BOT_TOKEN: Formato válido")
            else:
                print("⚠️  TELEGRAM_BOT_TOKEN: Formato suspeito")
                self.results["configuration_errors"].append({
                    "type": "invalid_format",
                    "variable": "TELEGRAM_BOT_TOKEN",
                    "message": "Formato inválido para token do Telegram"
                })
        
        # Validar TELEGRAM_CHAT_ID
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if chat_id:
            try:
                int(chat_id)
                print("✅ TELEGRAM_CHAT_ID: Formato válido")
            except ValueError:
                print("⚠️  TELEGRAM_CHAT_ID: Deve ser um número")
                self.results["configuration_errors"].append({
                    "type": "invalid_format",
                    "variable": "TELEGRAM_CHAT_ID",
                    "message": "Deve ser um número"
                })

    def test_basic_imports(self):
        """Testa se imports básicos funcionam"""
        print("\n🧪 TESTANDO IMPORTS BÁSICOS...")
        
        try:
            import openai
            print("✅ OpenAI: Import bem-sucedido")
        except ImportError:
            print("⚠️  OpenAI: Biblioteca não encontrada")
        
        try:
            import requests
            print("✅ Requests: Import bem-sucedido")
        except ImportError:
            print("⚠️  Requests: Biblioteca não encontrada")
        
        try:
            import psycopg2
            print("✅ Psycopg2: Import bem-sucedido")
        except ImportError:
            print("⚠️  Psycopg2: Biblioteca não encontrada")

    def generate_recommendations(self):
        """Gera recomendações baseadas na verificação"""
        recommendations = []
        
        if self.results["missing_variables"]:
            recommendations.append({
                "priority": "CRÍTICA",
                "action": f"Adicionar variáveis ausentes: {', '.join(self.results['missing_variables'])}",
                "impact": "Sistema não funcionará sem essas variáveis"
            })
        
        if self.results["configuration_errors"]:
            recommendations.append({
                "priority": "ALTA",
                "action": "Corrigir erros de configuração identificados",
                "impact": "Pode causar falhas em funcionalidades específicas"
            })
        
        if not self.results["missing_variables"] and not self.results["configuration_errors"]:
            recommendations.append({
                "priority": "INFORMATIVA",
                "action": "Configuração parece correta - fazer redeploy e monitorar",
                "impact": "Sistema deve funcionar normalmente"
            })
        
        self.results["recommendations"] = recommendations
        return recommendations

    def determine_system_status(self) -> str:
        """Determina status geral do sistema"""
        if self.results["missing_variables"]:
            return "CRÍTICO - Variáveis ausentes"
        elif self.results["configuration_errors"]:
            return "ATENÇÃO - Erros de configuração"
        else:
            return "OK - Configuração válida"

    def mask_sensitive_value(self, var_name: str, value: str) -> str:
        """Mascara valores sensíveis para exibição"""
        if not value:
            return "VAZIO"
        
        sensitive_vars = ["TOKEN", "KEY", "SECRET", "PASSWORD", "DSN", "URL"]
        
        if any(sensitive in var_name.upper() for sensitive in sensitive_vars):
            if len(value) <= 8:
                return "*" * len(value)
            else:
                return f"{value[:4]}...{value[-4:]}"
        
        return value

    def print_summary(self):
        """Imprime resumo da verificação"""
        print("\n" + "=" * 80)
        print("📊 RESUMO DA VERIFICAÇÃO")
        print("=" * 80)
        
        # Status geral
        status = self.determine_system_status()
        self.results["system_status"] = status
        
        if "CRÍTICO" in status:
            print(f"🚨 STATUS: {status}")
        elif "ATENÇÃO" in status:
            print(f"⚠️  STATUS: {status}")
        else:
            print(f"✅ STATUS: {status}")
        
        # Estatísticas
        total_critical = len(self.critical_vars)
        present_critical = sum(1 for var in self.results["critical_variables"].values() if var["present"])
        
        print(f"\n📈 ESTATÍSTICAS:")
        print(f"   Variáveis críticas: {present_critical}/{total_critical}")
        print(f"   Variáveis ausentes: {len(self.results['missing_variables'])}")
        print(f"   Erros de configuração: {len(self.results['configuration_errors'])}")
        
        # Recomendações
        recommendations = self.generate_recommendations()
        if recommendations:
            print(f"\n🎯 RECOMENDAÇÕES:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. [{rec['priority']}] {rec['action']}")

    def save_results(self):
        """Salva resultados em arquivo JSON"""
        filename = f"verificacao_pos_correcao_{self.timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados salvos em: {filename}")
        return filename

    def run_verification(self):
        """Executa verificação completa"""
        self.print_header()
        
        # Verificações principais
        critical_ok = self.check_critical_variables()
        self.check_optional_variables()
        self.check_deprecated_variables()
        self.validate_variable_formats()
        self.test_basic_imports()
        
        # Resumo e salvamento
        self.print_summary()
        report_file = self.save_results()
        
        print("\n" + "=" * 80)
        print("🏁 VERIFICAÇÃO CONCLUÍDA")
        print("=" * 80)
        
        if critical_ok and not self.results["configuration_errors"]:
            print("✅ SUCESSO: Todas as variáveis críticas estão configuradas corretamente!")
            print("🚀 Próximo passo: Fazer redeploy da aplicação no Railway")
            return True
        else:
            print("❌ AÇÃO NECESSÁRIA: Corrija os problemas identificados antes do redeploy")
            return False

def main():
    """Função principal"""
    verifier = RailwayPostCorrectionVerifier()
    success = verifier.run_verification()
    
    # Exit code para scripts automatizados
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()