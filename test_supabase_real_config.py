#!/usr/bin/env python3
"""
Script para verificar configurações reais do Supabase
Busca por configurações em Railway, arquivos de configuração e testa conectividade
"""

import os
import json
import requests
from datetime import datetime
import subprocess
import sys

class SupabaseRealConfigTester:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "supabase_real_configuration",
            "components": {},
            "overall_status": "UNKNOWN",
            "score": 0,
            "max_score": 0,
            "errors": [],
            "warnings": [],
            "recommendations": [],
            "found_configurations": []
        }
        
        self.supabase_configs = []
    
    def search_railway_variables(self):
        """Busca variáveis do Supabase no Railway"""
        print("🚂 Verificando variáveis do Railway...")
        
        component = {
            "name": "Railway Environment Variables",
            "status": "UNKNOWN",
            "details": {},
            "tests": [],
            "score": 0,
            "max_score": 3
        }
        
        try:
            # Verificar se Railway CLI está disponível
            try:
                result = subprocess.run(["railway", "--version"], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    component["tests"].append({"name": "Railway CLI Available", "status": "PASS", "details": "Railway CLI instalado"})
                    component["score"] += 0.5
                    
                    # Tentar listar variáveis
                    try:
                        result = subprocess.run(["railway", "variables"], capture_output=True, text=True, timeout=15)
                        if result.returncode == 0:
                            output = result.stdout
                            
                            # Procurar por variáveis do Supabase
                            supabase_vars = []
                            for line in output.split('\n'):
                                if any(var in line.upper() for var in ['SUPABASE_URL', 'SUPABASE_SERVICE_KEY', 'SUPABASE_ANON_KEY', 'SUPABASE_BUCKET']):
                                    supabase_vars.append(line.strip())
                            
                            if supabase_vars:
                                component["tests"].append({"name": "Supabase Variables in Railway", "status": "PASS", "details": f"Encontradas {len(supabase_vars)} variáveis"})
                                component["score"] += 2
                                component["details"]["supabase_variables"] = supabase_vars
                                self.supabase_configs.extend(supabase_vars)
                            else:
                                component["tests"].append({"name": "Supabase Variables in Railway", "status": "FAIL", "details": "Nenhuma variável do Supabase encontrada"})
                        else:
                            component["tests"].append({"name": "Railway Variables Access", "status": "FAIL", "details": f"Erro ao acessar variáveis: {result.stderr}"})
                    except subprocess.TimeoutExpired:
                        component["tests"].append({"name": "Railway Variables Access", "status": "FAIL", "details": "Timeout ao acessar variáveis"})
                    except Exception as e:
                        component["tests"].append({"name": "Railway Variables Access", "status": "FAIL", "details": f"Erro: {e}"})
                else:
                    component["tests"].append({"name": "Railway CLI Available", "status": "FAIL", "details": "Railway CLI não disponível"})
            except FileNotFoundError:
                component["tests"].append({"name": "Railway CLI Available", "status": "FAIL", "details": "Railway CLI não instalado"})
            except Exception as e:
                component["tests"].append({"name": "Railway CLI Available", "status": "FAIL", "details": f"Erro: {e}"})
            
            # Verificar arquivo de deploy
            try:
                if os.path.exists("deploy_feed_vars.py"):
                    with open("deploy_feed_vars.py", "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    if "SUPABASE" in content.upper():
                        component["tests"].append({"name": "Deploy Script Config", "status": "PASS", "details": "Configurações do Supabase encontradas no script de deploy"})
                        component["score"] += 0.5
                    else:
                        component["tests"].append({"name": "Deploy Script Config", "status": "FAIL", "details": "Nenhuma configuração do Supabase no script de deploy"})
                else:
                    component["tests"].append({"name": "Deploy Script Config", "status": "FAIL", "details": "Script de deploy não encontrado"})
            except Exception as e:
                component["tests"].append({"name": "Deploy Script Config", "status": "FAIL", "details": f"Erro: {e}"})
            
            # Determinar status
            if component["score"] >= 2:
                component["status"] = "CONFIGURED"
            elif component["score"] >= 1:
                component["status"] = "PARTIAL"
            else:
                component["status"] = "NOT_CONFIGURED"
                
        except Exception as e:
            component["status"] = "ERROR"
            component["details"]["error"] = str(e)
            self.results["errors"].append(f"Erro ao verificar Railway: {e}")
        
        self.results["components"]["railway_variables"] = component
    
    def search_local_configurations(self):
        """Busca configurações locais do Supabase"""
        print("📁 Verificando configurações locais...")
        
        component = {
            "name": "Local Configuration Files",
            "status": "UNKNOWN",
            "details": {},
            "tests": [],
            "score": 0,
            "max_score": 4
        }
        
        try:
            # Verificar variáveis de ambiente
            env_supabase_vars = {}
            for var in ["SUPABASE_URL", "SUPABASE_SERVICE_KEY", "SUPABASE_ANON_KEY", "SUPABASE_BUCKET"]:
                value = os.getenv(var)
                if value:
                    env_supabase_vars[var] = value[:20] + "..." if len(value) > 20 else value
            
            if env_supabase_vars:
                component["tests"].append({"name": "Environment Variables", "status": "PASS", "details": f"Variáveis configuradas: {list(env_supabase_vars.keys())}"})
                component["score"] += 1
                component["details"]["env_variables"] = env_supabase_vars
                self.supabase_configs.append(f"Environment variables: {list(env_supabase_vars.keys())}")
            else:
                component["tests"].append({"name": "Environment Variables", "status": "FAIL", "details": "Nenhuma variável de ambiente configurada"})
            
            # Verificar config.py
            try:
                if os.path.exists("src/config.py"):
                    with open("src/config.py", "r", encoding="utf-8") as f:
                        config_content = f.read()
                    
                    supabase_lines = [line.strip() for line in config_content.split('\n') if 'SUPABASE' in line.upper()]
                    
                    if supabase_lines:
                        component["tests"].append({"name": "Config.py File", "status": "PASS", "details": f"Encontradas {len(supabase_lines)} linhas com Supabase"})
                        component["score"] += 1
                        component["details"]["config_py_lines"] = supabase_lines
                    else:
                        component["tests"].append({"name": "Config.py File", "status": "FAIL", "details": "Nenhuma configuração do Supabase encontrada"})
                else:
                    component["tests"].append({"name": "Config.py File", "status": "FAIL", "details": "Arquivo config.py não encontrado"})
            except Exception as e:
                component["tests"].append({"name": "Config.py File", "status": "FAIL", "details": f"Erro: {e}"})
            
            # Verificar accounts.json
            try:
                if os.path.exists("accounts.json"):
                    with open("accounts.json", "r", encoding="utf-8") as f:
                        accounts = json.load(f)
                    
                    accounts_with_supabase = []
                    for account in accounts:
                        if any(key.startswith('supabase') for key in account.keys()):
                            accounts_with_supabase.append(account.get('nome', 'unknown'))
                    
                    if accounts_with_supabase:
                        component["tests"].append({"name": "Accounts.json File", "status": "PASS", "details": f"Contas com Supabase: {accounts_with_supabase}"})
                        component["score"] += 1
                        component["details"]["accounts_with_supabase"] = accounts_with_supabase
                    else:
                        component["tests"].append({"name": "Accounts.json File", "status": "FAIL", "details": "Nenhuma conta configurada com Supabase"})
                else:
                    component["tests"].append({"name": "Accounts.json File", "status": "FAIL", "details": "Arquivo accounts.json não encontrado"})
            except Exception as e:
                component["tests"].append({"name": "Accounts.json File", "status": "FAIL", "details": f"Erro: {e}"})
            
            # Verificar CREDENCIAIS_PERMANENTES.json
            try:
                if os.path.exists("CREDENCIAIS_PERMANENTES.json"):
                    with open("CREDENCIAIS_PERMANENTES.json", "r", encoding="utf-8") as f:
                        creds = json.load(f)
                    
                    supabase_creds = {}
                    for key, value in creds.items():
                        if 'supabase' in key.lower():
                            supabase_creds[key] = str(value)[:20] + "..." if len(str(value)) > 20 else str(value)
                    
                    if supabase_creds:
                        component["tests"].append({"name": "Permanent Credentials", "status": "PASS", "details": f"Credenciais encontradas: {list(supabase_creds.keys())}"})
                        component["score"] += 1
                        component["details"]["permanent_credentials"] = supabase_creds
                    else:
                        component["tests"].append({"name": "Permanent Credentials", "status": "FAIL", "details": "Nenhuma credencial do Supabase encontrada"})
                else:
                    component["tests"].append({"name": "Permanent Credentials", "status": "FAIL", "details": "Arquivo de credenciais não encontrado"})
            except Exception as e:
                component["tests"].append({"name": "Permanent Credentials", "status": "FAIL", "details": f"Erro: {e}"})
            
            # Determinar status
            if component["score"] >= 3:
                component["status"] = "WELL_CONFIGURED"
            elif component["score"] >= 2:
                component["status"] = "CONFIGURED"
            elif component["score"] >= 1:
                component["status"] = "PARTIAL"
            else:
                component["status"] = "NOT_CONFIGURED"
                
        except Exception as e:
            component["status"] = "ERROR"
            component["details"]["error"] = str(e)
            self.results["errors"].append(f"Erro ao verificar configurações locais: {e}")
        
        self.results["components"]["local_configurations"] = component
    
    def test_supabase_implementation(self):
        """Testa a implementação do Supabase no código"""
        print("🔧 Verificando implementação do Supabase...")
        
        component = {
            "name": "Supabase Implementation",
            "status": "UNKNOWN",
            "details": {},
            "tests": [],
            "score": 0,
            "max_score": 3
        }
        
        try:
            # Verificar SupabaseUploader
            try:
                if os.path.exists("src/services/supabase_uploader.py"):
                    with open("src/services/supabase_uploader.py", "r", encoding="utf-8") as f:
                        uploader_content = f.read()
                    
                    # Verificar métodos essenciais
                    essential_methods = ["upload_from_url", "__init__", "upload_file"]
                    found_methods = []
                    
                    for method in essential_methods:
                        if f"def {method}" in uploader_content:
                            found_methods.append(method)
                    
                    if len(found_methods) >= 2:
                        component["tests"].append({"name": "SupabaseUploader Class", "status": "PASS", "details": f"Métodos encontrados: {found_methods}"})
                        component["score"] += 1
                        component["details"]["uploader_methods"] = found_methods
                    else:
                        component["tests"].append({"name": "SupabaseUploader Class", "status": "PARTIAL", "details": f"Implementação incompleta: {found_methods}"})
                        component["score"] += 0.5
                else:
                    component["tests"].append({"name": "SupabaseUploader Class", "status": "FAIL", "details": "Arquivo não encontrado"})
            except Exception as e:
                component["tests"].append({"name": "SupabaseUploader Class", "status": "FAIL", "details": f"Erro: {e}"})
            
            # Verificar uso no pipeline
            try:
                if os.path.exists("src/pipeline/generate_and_publish.py"):
                    with open("src/pipeline/generate_and_publish.py", "r", encoding="utf-8") as f:
                        pipeline_content = f.read()
                    
                    if "supabase" in pipeline_content.lower():
                        component["tests"].append({"name": "Pipeline Integration", "status": "PASS", "details": "Supabase integrado no pipeline"})
                        component["score"] += 1
                        
                        # Contar ocorrências
                        supabase_occurrences = pipeline_content.lower().count("supabase")
                        component["details"]["pipeline_occurrences"] = supabase_occurrences
                    else:
                        component["tests"].append({"name": "Pipeline Integration", "status": "FAIL", "details": "Supabase não integrado no pipeline"})
                else:
                    component["tests"].append({"name": "Pipeline Integration", "status": "FAIL", "details": "Arquivo de pipeline não encontrado"})
            except Exception as e:
                component["tests"].append({"name": "Pipeline Integration", "status": "FAIL", "details": f"Erro: {e}"})
            
            # Verificar imports e dependências
            try:
                files_to_check = [
                    "src/main.py",
                    "src/config.py",
                    "src/services/supabase_uploader.py"
                ]
                
                supabase_imports = []
                for file_path in files_to_check:
                    if os.path.exists(file_path):
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        
                        # Procurar por imports relacionados ao Supabase
                        for line in content.split('\n'):
                            if 'import' in line and 'supabase' in line.lower():
                                supabase_imports.append(f"{file_path}: {line.strip()}")
                
                if supabase_imports:
                    component["tests"].append({"name": "Supabase Imports", "status": "PASS", "details": f"Encontrados {len(supabase_imports)} imports"})
                    component["score"] += 1
                    component["details"]["supabase_imports"] = supabase_imports
                else:
                    component["tests"].append({"name": "Supabase Imports", "status": "FAIL", "details": "Nenhum import do Supabase encontrado"})
            except Exception as e:
                component["tests"].append({"name": "Supabase Imports", "status": "FAIL", "details": f"Erro: {e}"})
            
            # Determinar status
            if component["score"] >= 2.5:
                component["status"] = "WELL_IMPLEMENTED"
            elif component["score"] >= 1.5:
                component["status"] = "IMPLEMENTED"
            elif component["score"] >= 0.5:
                component["status"] = "PARTIAL"
            else:
                component["status"] = "NOT_IMPLEMENTED"
                
        except Exception as e:
            component["status"] = "ERROR"
            component["details"]["error"] = str(e)
            self.results["errors"].append(f"Erro ao verificar implementação: {e}")
        
        self.results["components"]["supabase_implementation"] = component
    
    def test_connectivity_with_found_configs(self):
        """Testa conectividade usando configurações encontradas"""
        print("🌐 Testando conectividade com configurações encontradas...")
        
        component = {
            "name": "Connectivity Test",
            "status": "UNKNOWN",
            "details": {},
            "tests": [],
            "score": 0,
            "max_score": 2
        }
        
        try:
            # Tentar obter configurações reais
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
            
            if not supabase_url:
                # Tentar obter de accounts.json
                try:
                    if os.path.exists("accounts.json"):
                        with open("accounts.json", "r", encoding="utf-8") as f:
                            accounts = json.load(f)
                        
                        for account in accounts:
                            if account.get("supabase_url"):
                                supabase_url = account["supabase_url"]
                                supabase_key = account.get("supabase_service_key") or account.get("supabase_anon_key")
                                break
                except:
                    pass
            
            if supabase_url and supabase_key:
                component["details"]["config_source"] = "Found valid configuration"
                
                # Teste 1: Verificar se a URL é válida
                try:
                    if supabase_url.startswith("https://") and ".supabase.co" in supabase_url:
                        component["tests"].append({"name": "URL Validation", "status": "PASS", "details": "URL válida"})
                        component["score"] += 0.5
                        
                        # Teste 2: Tentar conectar
                        try:
                            headers = {
                                "apikey": supabase_key,
                                "Authorization": f"Bearer {supabase_key}",
                                "Content-Type": "application/json"
                            }
                            
                            response = requests.get(f"{supabase_url}/rest/v1/", headers=headers, timeout=10)
                            
                            if response.status_code in [200, 400, 401, 403]:  # Qualquer resposta válida
                                component["tests"].append({"name": "Connection Test", "status": "PASS", "details": f"Conectado - Status: {response.status_code}"})
                                component["score"] += 1.5
                                component["details"]["connection_status"] = response.status_code
                                component["details"]["response_headers"] = dict(response.headers)
                            else:
                                component["tests"].append({"name": "Connection Test", "status": "FAIL", "details": f"Status inesperado: {response.status_code}"})
                        except Exception as e:
                            component["tests"].append({"name": "Connection Test", "status": "FAIL", "details": f"Erro de conexão: {e}"})
                    else:
                        component["tests"].append({"name": "URL Validation", "status": "FAIL", "details": "URL inválida"})
                except Exception as e:
                    component["tests"].append({"name": "URL Validation", "status": "FAIL", "details": f"Erro: {e}"})
            else:
                component["tests"].append({"name": "Configuration Available", "status": "FAIL", "details": "Nenhuma configuração válida encontrada"})
                component["details"]["config_source"] = "No valid configuration found"
            
            # Determinar status
            if component["score"] >= 1.5:
                component["status"] = "CONNECTED"
            elif component["score"] >= 0.5:
                component["status"] = "PARTIAL"
            else:
                component["status"] = "NOT_CONNECTED"
                
        except Exception as e:
            component["status"] = "ERROR"
            component["details"]["error"] = str(e)
            self.results["errors"].append(f"Erro ao testar conectividade: {e}")
        
        self.results["components"]["connectivity_test"] = component
    
    def generate_recommendations(self):
        """Gera recomendações baseadas nos resultados"""
        recommendations = []
        
        # Verificar configurações do Railway
        railway_status = self.results["components"].get("railway_variables", {}).get("status")
        if railway_status == "NOT_CONFIGURED":
            recommendations.append({
                "priority": "HIGH",
                "category": "Railway",
                "issue": "Variáveis do Supabase não configuradas no Railway",
                "solution": "Configurar SUPABASE_URL, SUPABASE_SERVICE_KEY e SUPABASE_BUCKET no Railway"
            })
        
        # Verificar configurações locais
        local_status = self.results["components"].get("local_configurations", {}).get("status")
        if local_status == "NOT_CONFIGURED":
            recommendations.append({
                "priority": "HIGH",
                "category": "Configuration",
                "issue": "Nenhuma configuração local do Supabase encontrada",
                "solution": "Configurar variáveis de ambiente ou arquivos de configuração"
            })
        elif local_status == "PARTIAL":
            recommendations.append({
                "priority": "MEDIUM",
                "category": "Configuration",
                "issue": "Configuração local do Supabase incompleta",
                "solution": "Completar todas as variáveis necessárias"
            })
        
        # Verificar implementação
        impl_status = self.results["components"].get("supabase_implementation", {}).get("status")
        if impl_status in ["NOT_IMPLEMENTED", "PARTIAL"]:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "Implementation",
                "issue": "Implementação do Supabase incompleta",
                "solution": "Completar a implementação do SupabaseUploader e integração no pipeline"
            })
        
        # Verificar conectividade
        conn_status = self.results["components"].get("connectivity_test", {}).get("status")
        if conn_status == "NOT_CONNECTED":
            recommendations.append({
                "priority": "CRITICAL",
                "category": "Connectivity",
                "issue": "Não foi possível conectar ao Supabase",
                "solution": "Verificar credenciais e configurações de rede"
            })
        
        # Recomendações gerais
        if not self.supabase_configs:
            recommendations.append({
                "priority": "HIGH",
                "category": "General",
                "issue": "Supabase não está configurado no sistema",
                "solution": "Criar projeto no Supabase e configurar todas as credenciais necessárias"
            })
        
        self.results["recommendations"] = recommendations
    
    def calculate_overall_status(self):
        """Calcula status geral e pontuação"""
        total_score = 0
        max_total_score = 0
        
        for component in self.results["components"].values():
            total_score += component["score"]
            max_total_score += component["max_score"]
        
        self.results["score"] = total_score
        self.results["max_score"] = max_total_score
        
        if max_total_score > 0:
            percentage = (total_score / max_total_score) * 100
            
            if percentage >= 90:
                self.results["overall_status"] = "EXCELENTE"
            elif percentage >= 75:
                self.results["overall_status"] = "BOM"
            elif percentage >= 50:
                self.results["overall_status"] = "PARCIAL"
            elif percentage >= 25:
                self.results["overall_status"] = "LIMITADO"
            else:
                self.results["overall_status"] = "CRÍTICO"
        else:
            self.results["overall_status"] = "NÃO_TESTADO"
        
        # Adicionar configurações encontradas ao resultado
        self.results["found_configurations"] = self.supabase_configs
    
    def run_verification(self):
        """Executa verificação completa"""
        print("🚀 Iniciando verificação real do Supabase...")
        print(f"⏰ Timestamp: {self.results['timestamp']}")
        print()
        
        # Executar todas as verificações
        self.search_railway_variables()
        self.search_local_configurations()
        self.test_supabase_implementation()
        self.test_connectivity_with_found_configs()
        
        # Gerar análise final
        self.generate_recommendations()
        self.calculate_overall_status()
        
        # Salvar relatório
        report_filename = f"supabase_real_config_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print()
        print("=" * 70)
        print("📊 RELATÓRIO DE VERIFICAÇÃO REAL DO SUPABASE")
        print("=" * 70)
        print(f"🎯 Status Geral: {self.results['overall_status']}")
        print(f"📈 Pontuação: {self.results['score']}/{self.results['max_score']} ({(self.results['score']/self.results['max_score']*100):.1f}%)")
        print()
        
        print("📋 COMPONENTES:")
        for comp_name, comp_data in self.results["components"].items():
            status_emoji = {
                "WELL_CONFIGURED": "✅",
                "CONFIGURED": "✅",
                "WELL_IMPLEMENTED": "✅",
                "IMPLEMENTED": "✅",
                "CONNECTED": "✅",
                "PARTIAL": "⚠️",
                "NOT_CONFIGURED": "❌",
                "NOT_IMPLEMENTED": "❌",
                "NOT_CONNECTED": "❌",
                "ERROR": "💥"
            }.get(comp_data["status"], "❓")
            
            print(f"  {status_emoji} {comp_data['name']}: {comp_data['status']} ({comp_data['score']}/{comp_data['max_score']})")
        
        if self.results["found_configurations"]:
            print()
            print("🔍 CONFIGURAÇÕES ENCONTRADAS:")
            for config in self.results["found_configurations"]:
                print(f"  📝 {config}")
        
        if self.results["errors"]:
            print()
            print("🚨 ERROS ENCONTRADOS:")
            for error in self.results["errors"]:
                print(f"  ❌ {error}")
        
        if self.results["recommendations"]:
            print()
            print("💡 RECOMENDAÇÕES:")
            for rec in self.results["recommendations"]:
                priority_emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(rec["priority"], "⚪")
                print(f"  {priority_emoji} [{rec['priority']}] {rec['issue']}")
                print(f"     💡 {rec['solution']}")
        
        print()
        print("📝 CONCLUSÃO:")
        if self.results["overall_status"] in ["EXCELENTE", "BOM"]:
            print("  ✅ Supabase está bem configurado e funcional")
        elif self.results["overall_status"] == "PARCIAL":
            print("  ⚠️ Supabase parcialmente configurado - melhorias necessárias")
        elif self.results["overall_status"] == "LIMITADO":
            print("  🟡 Supabase com configuração limitada")
        else:
            print("  ❌ Supabase não configurado ou com problemas críticos")
        
        print()
        print(f"📄 Relatório salvo em: {report_filename}")
        print("=" * 70)
        
        return self.results

if __name__ == "__main__":
    tester = SupabaseRealConfigTester()
    results = tester.run_verification()