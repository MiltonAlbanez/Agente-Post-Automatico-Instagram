#!/usr/bin/env python3
"""
Script para configurar credenciais do Supabase no Railway
Verifica se o Railway CLI está instalado e executa os comandos necessários
"""

import os
import subprocess
import json
import sys
from datetime import datetime
from typing import Dict, List, Tuple

class RailwaySupabaseConfigurator:
    def __init__(self):
        self.supabase_credentials = {
            "SUPABASE_URL": "https://ccvfdupucmsjxwtfwzkd.supabase.co",
            "SUPABASE_SERVICE_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNjdmZkdXB1Y21zanh3dGZ3emtkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg3OTgwNywiZXhwIjoyMDc1NDU1ODA3fQ.HcQb9CpoF9sQcRUBQWmcmx6RmokXd64FbGpBV3GVUzM",
            "SUPABASE_ANON_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNjdmZkdXB1Y21zanh3dGZ3emtkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4Nzk4MDcsImV4cCI6MjA3NTQ1NTgwN30.2M9-ieZ-PMnO7NQ-aDHjxor4ytAHa0pKwH7j1gsrXjI",
            "SUPABASE_BUCKET": "instagram-images",
            "SUPABASE_PROJECT_REF": "ccvfdupucmsjxwtfwzkd",
            "SUPABASE_DB_URL": "postgresql://postgres:HVt^le2l0QaDZ0JS@db.ccvfdupucmsjxwtfwzkd.supabase.co:5432/postgres",
            "SUPABASE_ACCESS_TOKEN": "sbp_a497779d74107ea60b909508cc9ad2f784429b01"
        }
        
        self.results = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "railway_cli_status": "UNKNOWN",
            "authentication_status": "UNKNOWN",
            "project_status": "UNKNOWN",
            "variables_configured": [],
            "failed_variables": [],
            "overall_status": "UNKNOWN",
            "recommendations": []
        }

    def check_railway_cli(self) -> bool:
        """Verifica se o Railway CLI está instalado"""
        print("🚂 Verificando Railway CLI...")
        
        try:
            # Tentar diferentes comandos para Windows
            commands_to_try = ["railway", "railway.ps1", "powershell", "-Command", "railway"]
            
            result = subprocess.run(
                ["powershell", "-Command", "railway --version"], 
                capture_output=True, 
                text=True, 
                timeout=10,
                shell=True
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"  ✅ Railway CLI encontrado: {version}")
                self.results["railway_cli_status"] = "INSTALLED"
                self.results["railway_cli_version"] = version
                return True
            else:
                print(f"  ❌ Railway CLI não encontrado: {result.stderr}")
                self.results["railway_cli_status"] = "NOT_INSTALLED"
                return False
                
        except subprocess.TimeoutExpired:
            print("  ⏰ Timeout ao verificar Railway CLI")
            self.results["railway_cli_status"] = "TIMEOUT"
            return False
        except FileNotFoundError:
            print("  ❌ Railway CLI não está instalado")
            self.results["railway_cli_status"] = "NOT_FOUND"
            return False
        except Exception as e:
            print(f"  ❌ Erro ao verificar Railway CLI: {e}")
            self.results["railway_cli_status"] = f"ERROR: {e}"
            return False

    def check_railway_auth(self) -> bool:
        """Verifica se está autenticado no Railway"""
        print("\n🔐 Verificando autenticação Railway...")
        
        try:
            result = subprocess.run(
                ["powershell", "-Command", "railway whoami"], 
                capture_output=True, 
                text=True, 
                timeout=15,
                shell=True
            )
            
            if result.returncode == 0:
                user_info = result.stdout.strip()
                print(f"  ✅ Autenticado como: {user_info}")
                self.results["authentication_status"] = "AUTHENTICATED"
                self.results["railway_user"] = user_info
                return True
            else:
                print(f"  ❌ Não autenticado: {result.stderr}")
                self.results["authentication_status"] = "NOT_AUTHENTICATED"
                return False
                
        except subprocess.TimeoutExpired:
            print("  ⏰ Timeout ao verificar autenticação")
            self.results["authentication_status"] = "TIMEOUT"
            return False
        except Exception as e:
            print(f"  ❌ Erro ao verificar autenticação: {e}")
            self.results["authentication_status"] = f"ERROR: {e}"
            return False

    def check_railway_project(self) -> bool:
        """Verifica se há um projeto Railway configurado"""
        print("\n📁 Verificando projeto Railway...")
        
        try:
            result = subprocess.run(
                ["powershell", "-Command", "railway status"], 
                capture_output=True, 
                text=True, 
                timeout=15,
                shell=True
            )
            
            if result.returncode == 0:
                status_info = result.stdout.strip()
                print(f"  ✅ Projeto encontrado:")
                print(f"    {status_info}")
                self.results["project_status"] = "CONNECTED"
                self.results["project_info"] = status_info
                return True
            else:
                print(f"  ❌ Nenhum projeto conectado: {result.stderr}")
                self.results["project_status"] = "NOT_CONNECTED"
                return False
                
        except subprocess.TimeoutExpired:
            print("  ⏰ Timeout ao verificar projeto")
            self.results["project_status"] = "TIMEOUT"
            return False
        except Exception as e:
            print(f"  ❌ Erro ao verificar projeto: {e}")
            self.results["project_status"] = f"ERROR: {e}"
            return False

    def configure_variables(self) -> bool:
        """Configura as variáveis do Supabase no Railway"""
        print("\n⚙️ Configurando variáveis do Supabase no Railway...")
        
        success_count = 0
        total_count = len(self.supabase_credentials)
        
        for var_name, var_value in self.supabase_credentials.items():
            print(f"\n  📝 Configurando {var_name}...")
            
            try:
                # Usar aspas duplas para valores que podem conter caracteres especiais
                command_str = f'railway variables --set "{var_name}={var_value}"'
                
                result = subprocess.run(
                    ["powershell", "-Command", command_str],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    shell=True
                )
                
                if result.returncode == 0:
                    print(f"    ✅ {var_name} configurada com sucesso")
                    self.results["variables_configured"].append({
                        "name": var_name,
                        "status": "SUCCESS",
                        "output": result.stdout.strip()
                    })
                    success_count += 1
                else:
                    print(f"    ❌ Erro ao configurar {var_name}: {result.stderr}")
                    self.results["failed_variables"].append({
                        "name": var_name,
                        "status": "FAILED",
                        "error": result.stderr.strip()
                    })
                    
            except subprocess.TimeoutExpired:
                print(f"    ⏰ Timeout ao configurar {var_name}")
                self.results["failed_variables"].append({
                    "name": var_name,
                    "status": "TIMEOUT",
                    "error": "Timeout durante configuração"
                })
            except Exception as e:
                print(f"    ❌ Erro ao configurar {var_name}: {e}")
                self.results["failed_variables"].append({
                    "name": var_name,
                    "status": "ERROR",
                    "error": str(e)
                })
        
        success_rate = (success_count / total_count) * 100
        print(f"\n📊 Resultado: {success_count}/{total_count} variáveis configuradas ({success_rate:.1f}%)")
        
        return success_count == total_count

    def verify_variables(self) -> bool:
        """Verifica se as variáveis foram configuradas corretamente"""
        print("\n🔍 Verificando variáveis configuradas...")
        
        try:
            result = subprocess.run(
                ["powershell", "-Command", "railway variables"], 
                capture_output=True, 
                text=True, 
                timeout=15,
                shell=True
            )
            
            if result.returncode == 0:
                variables_output = result.stdout
                configured_vars = []
                
                for var_name in self.supabase_credentials.keys():
                    if var_name in variables_output:
                        configured_vars.append(var_name)
                        print(f"  ✅ {var_name} encontrada")
                    else:
                        print(f"  ❌ {var_name} não encontrada")
                
                verification_rate = (len(configured_vars) / len(self.supabase_credentials)) * 100
                print(f"\n📊 Verificação: {len(configured_vars)}/{len(self.supabase_credentials)} variáveis encontradas ({verification_rate:.1f}%)")
                
                self.results["verification"] = {
                    "configured_variables": configured_vars,
                    "missing_variables": [var for var in self.supabase_credentials.keys() if var not in configured_vars],
                    "verification_rate": verification_rate
                }
                
                return len(configured_vars) == len(self.supabase_credentials)
            else:
                print(f"  ❌ Erro ao listar variáveis: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"  ❌ Erro ao verificar variáveis: {e}")
            return False

    def generate_recommendations(self):
        """Gera recomendações baseadas nos resultados"""
        recommendations = []
        
        if self.results["railway_cli_status"] != "INSTALLED":
            recommendations.append({
                "priority": "CRITICAL",
                "category": "Installation",
                "issue": "Railway CLI não está instalado",
                "solution": "Instalar Railway CLI: npm install -g @railway/cli"
            })
        
        if self.results["authentication_status"] != "AUTHENTICATED":
            recommendations.append({
                "priority": "CRITICAL",
                "category": "Authentication",
                "issue": "Não autenticado no Railway",
                "solution": "Executar: railway login"
            })
        
        if self.results["project_status"] != "CONNECTED":
            recommendations.append({
                "priority": "HIGH",
                "category": "Project",
                "issue": "Nenhum projeto Railway conectado",
                "solution": "Conectar ao projeto: railway link"
            })
        
        if self.results["failed_variables"]:
            recommendations.append({
                "priority": "HIGH",
                "category": "Configuration",
                "issue": f"{len(self.results['failed_variables'])} variáveis falharam na configuração",
                "solution": "Verificar permissões e tentar novamente"
            })
        
        self.results["recommendations"] = recommendations

    def determine_overall_status(self):
        """Determina o status geral da configuração"""
        if self.results["railway_cli_status"] != "INSTALLED":
            self.results["overall_status"] = "CLI_NOT_INSTALLED"
        elif self.results["authentication_status"] != "AUTHENTICATED":
            self.results["overall_status"] = "NOT_AUTHENTICATED"
        elif self.results["project_status"] != "CONNECTED":
            self.results["overall_status"] = "NO_PROJECT"
        elif self.results["failed_variables"]:
            if len(self.results["variables_configured"]) > len(self.results["failed_variables"]):
                self.results["overall_status"] = "PARTIALLY_CONFIGURED"
            else:
                self.results["overall_status"] = "CONFIGURATION_FAILED"
        else:
            self.results["overall_status"] = "FULLY_CONFIGURED"

    def save_report(self):
        """Salva o relatório da configuração"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"railway_supabase_configuration_report_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Relatório salvo em: {filename}")
        return filename

    def run_configuration(self):
        """Executa todo o processo de configuração"""
        print("🚂 CONFIGURAÇÃO DO SUPABASE NO RAILWAY")
        print("=" * 50)
        
        # Verificar Railway CLI
        if not self.check_railway_cli():
            print("\n❌ Railway CLI não encontrado. Instale com: npm install -g @railway/cli")
            self.determine_overall_status()
            self.generate_recommendations()
            self.save_report()
            return False
        
        # Verificar autenticação
        if not self.check_railway_auth():
            print("\n❌ Não autenticado. Execute: railway login")
            self.determine_overall_status()
            self.generate_recommendations()
            self.save_report()
            return False
        
        # Verificar projeto
        if not self.check_railway_project():
            print("\n❌ Nenhum projeto conectado. Execute: railway link")
            self.determine_overall_status()
            self.generate_recommendations()
            self.save_report()
            return False
        
        # Configurar variáveis
        variables_success = self.configure_variables()
        
        # Verificar configuração
        verification_success = self.verify_variables()
        
        # Gerar relatório final
        self.determine_overall_status()
        self.generate_recommendations()
        
        print(f"\n🎯 STATUS FINAL: {self.results['overall_status']}")
        
        if self.results["overall_status"] == "FULLY_CONFIGURED":
            print("✅ Todas as variáveis do Supabase foram configuradas com sucesso no Railway!")
        else:
            print("⚠️ Configuração incompleta. Verifique as recomendações no relatório.")
        
        self.save_report()
        return variables_success and verification_success

if __name__ == "__main__":
    configurator = RailwaySupabaseConfigurator()
    success = configurator.run_configuration()
    
    if success:
        print("\n🎉 Configuração do Railway concluída com sucesso!")
        sys.exit(0)
    else:
        print("\n❌ Configuração do Railway falhou. Verifique o relatório para detalhes.")
        sys.exit(1)