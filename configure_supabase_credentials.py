#!/usr/bin/env python3
"""
Script para configurar credenciais do Supabase
Configura variáveis de ambiente e atualiza arquivos de configuração
"""

import os
import json
from datetime import datetime

class SupabaseCredentialsConfigurator:
    def __init__(self):
        self.credentials = {
            "SUPABASE_URL": "https://ccvfdupucmsjxwtfwzkd.supabase.co",
            "SUPABASE_SERVICE_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNjdmZkdXB1Y21zanh3dGZ3emtkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg3OTgwNywiZXhwIjoyMDc1NDU1ODA3fQ.HcQb9CpoF9sQcRUBQWmcmx6RmokXd64FbGpBV3GVUzM",
            "SUPABASE_ANON_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNjdmZkdXB1Y21zanh3dGZ3emtkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4Nzk4MDcsImV4cCI6MjA3NTQ1NTgwN30.2M9-ieZ-PMnO7NQ-aDHjxor4ytAHa0pKwH7j1gsrXjI",
            "SUPABASE_BUCKET": "instagram-images",
            "SUPABASE_PROJECT_REF": "ccvfdupucmsjxwtfwzkd",
            "SUPABASE_DB_URL": "postgresql://postgres:HVt^le2l0QaDZ0JS@db.ccvfdupucmsjxwtfwzkd.supabase.co:5432/postgres",
            "SUPABASE_ACCESS_TOKEN": "sbp_a497779d74107ea60b909508cc9ad2f784429b01"
        }
        
        self.config_files = [
            "accounts.json",
            "accounts_backup.json", 
            "accounts_corrected.json",
            "CREDENCIAIS_PERMANENTES.json"
        ]
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "environment_variables": {},
            "config_files_updated": {},
            "railway_commands": [],
            "verification_results": {}
        }
    
    def set_environment_variables(self):
        """Define variáveis de ambiente do Supabase"""
        print("🔧 Configurando variáveis de ambiente do Supabase...")
        
        for key, value in self.credentials.items():
            try:
                os.environ[key] = value
                self.results["environment_variables"][key] = "SET"
                print(f"  ✅ {key}: Configurada")
            except Exception as e:
                self.results["environment_variables"][key] = f"ERROR: {str(e)}"
                print(f"  ❌ {key}: Erro - {e}")
        
        return self.results["environment_variables"]
    
    def update_config_files(self):
        """Atualiza arquivos de configuração com credenciais do Supabase"""
        print("\n📝 Atualizando arquivos de configuração...")
        
        for config_file in self.config_files:
            if os.path.exists(config_file):
                try:
                    # Carregar arquivo existente
                    with open(config_file, "r", encoding="utf-8") as f:
                        config_data = json.load(f)
                    
                    # Atualizar com credenciais do Supabase
                    updated = False
                    
                    # Se for um arquivo de contas
                    if "accounts" in config_data or isinstance(config_data, list):
                        accounts = config_data.get("accounts", config_data) if isinstance(config_data, dict) else config_data
                        
                        for account in accounts:
                            if isinstance(account, dict):
                                # Atualizar credenciais do Supabase para cada conta
                                account.update({
                                    "supabase_url": self.credentials["SUPABASE_URL"],
                                    "supabase_service_key": self.credentials["SUPABASE_SERVICE_KEY"],
                                    "supabase_bucket": self.credentials["SUPABASE_BUCKET"]
                                })
                                updated = True
                    
                    # Se for arquivo de credenciais permanentes
                    elif "railway_vars" in config_data or "environment" in config_data:
                        if "railway_vars" not in config_data:
                            config_data["railway_vars"] = {}
                        
                        config_data["railway_vars"].update(self.credentials)
                        updated = True
                    
                    # Adicionar seção Supabase se não existir
                    else:
                        config_data["supabase"] = self.credentials
                        updated = True
                    
                    if updated:
                        # Salvar arquivo atualizado
                        with open(config_file, "w", encoding="utf-8") as f:
                            json.dump(config_data, f, indent=2, ensure_ascii=False)
                        
                        self.results["config_files_updated"][config_file] = "UPDATED"
                        print(f"  ✅ {config_file}: Atualizado")
                    else:
                        self.results["config_files_updated"][config_file] = "NO_CHANGES"
                        print(f"  ⚠️ {config_file}: Nenhuma alteração necessária")
                
                except Exception as e:
                    self.results["config_files_updated"][config_file] = f"ERROR: {str(e)}"
                    print(f"  ❌ {config_file}: Erro - {e}")
            else:
                self.results["config_files_updated"][config_file] = "FILE_NOT_FOUND"
                print(f"  ⚠️ {config_file}: Arquivo não encontrado")
    
    def generate_railway_commands(self):
        """Gera comandos para configurar variáveis no Railway"""
        print("\n🚂 Gerando comandos para Railway...")
        
        commands = []
        for key, value in self.credentials.items():
            # Escapar caracteres especiais para Railway
            escaped_value = value.replace('"', '\\"').replace("'", "\\'")
            command = f'railway variables set {key}="{escaped_value}"'
            commands.append(command)
        
        self.results["railway_commands"] = commands
        
        # Salvar comandos em arquivo
        with open("railway_supabase_commands.txt", "w", encoding="utf-8") as f:
            f.write("# Comandos para configurar Supabase no Railway\n")
            f.write("# Execute estes comandos no terminal com Railway CLI instalado\n\n")
            for command in commands:
                f.write(f"{command}\n")
        
        print(f"  ✅ {len(commands)} comandos gerados")
        print("  📄 Comandos salvos em: railway_supabase_commands.txt")
        
        return commands
    
    def verify_configuration(self):
        """Verifica se as configurações foram aplicadas corretamente"""
        print("\n🔍 Verificando configurações...")
        
        verification = {
            "environment_variables": {},
            "config_files": {},
            "overall_status": "UNKNOWN"
        }
        
        # Verificar variáveis de ambiente
        env_success = 0
        for key in self.credentials.keys():
            if os.environ.get(key):
                verification["environment_variables"][key] = "OK"
                env_success += 1
            else:
                verification["environment_variables"][key] = "MISSING"
        
        # Verificar arquivos de configuração
        config_success = 0
        for config_file in self.config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, "r", encoding="utf-8") as f:
                        config_data = json.load(f)
                    
                    # Verificar se contém configurações do Supabase
                    config_str = json.dumps(config_data).lower()
                    if "supabase" in config_str or "ccvfdupucmsjxwtfwzkd" in config_str:
                        verification["config_files"][config_file] = "CONFIGURED"
                        config_success += 1
                    else:
                        verification["config_files"][config_file] = "NOT_CONFIGURED"
                
                except Exception as e:
                    verification["config_files"][config_file] = f"ERROR: {str(e)}"
            else:
                verification["config_files"][config_file] = "NOT_FOUND"
        
        # Determinar status geral
        total_env = len(self.credentials)
        total_configs = len([f for f in self.config_files if os.path.exists(f)])
        
        if env_success == total_env and config_success >= total_configs // 2:
            verification["overall_status"] = "EXCELLENT"
        elif env_success >= total_env // 2:
            verification["overall_status"] = "GOOD"
        elif env_success > 0:
            verification["overall_status"] = "PARTIAL"
        else:
            verification["overall_status"] = "FAILED"
        
        self.results["verification_results"] = verification
        
        print(f"  📊 Variáveis de ambiente: {env_success}/{total_env}")
        print(f"  📁 Arquivos configurados: {config_success}/{total_configs}")
        print(f"  🎯 Status geral: {verification['overall_status']}")
        
        return verification
    
    def save_configuration_report(self):
        """Salva relatório de configuração"""
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"supabase_configuration_report_{timestamp_str}.json"
        
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Relatório salvo em: {report_file}")
        return report_file
    
    def configure_all(self):
        """Executa configuração completa do Supabase"""
        print("=" * 70)
        print("🔧 CONFIGURAÇÃO COMPLETA DO SUPABASE")
        print("=" * 70)
        
        # 1. Configurar variáveis de ambiente
        env_results = self.set_environment_variables()
        
        # 2. Atualizar arquivos de configuração
        self.update_config_files()
        
        # 3. Gerar comandos do Railway
        railway_commands = self.generate_railway_commands()
        
        # 4. Verificar configurações
        verification = self.verify_configuration()
        
        # 5. Salvar relatório
        report_file = self.save_configuration_report()
        
        print("\n" + "=" * 70)
        print("📊 RESUMO DA CONFIGURAÇÃO")
        print("=" * 70)
        
        print(f"🎯 Status Geral: {verification['overall_status']}")
        print(f"🔧 Variáveis de Ambiente: {sum(1 for v in env_results.values() if v == 'SET')}/{len(env_results)}")
        print(f"📝 Arquivos Atualizados: {sum(1 for v in self.results['config_files_updated'].values() if v == 'UPDATED')}")
        print(f"🚂 Comandos Railway: {len(railway_commands)} gerados")
        
        print("\n💡 PRÓXIMOS PASSOS:")
        print("1. ✅ Variáveis configuradas localmente")
        print("2. 🚂 Execute os comandos do Railway (railway_supabase_commands.txt)")
        print("3. 🧪 Teste a conectividade com o Supabase")
        print("4. 📦 Verifique o bucket de armazenamento")
        
        print("=" * 70)
        
        return self.results

if __name__ == "__main__":
    configurator = SupabaseCredentialsConfigurator()
    results = configurator.configure_all()