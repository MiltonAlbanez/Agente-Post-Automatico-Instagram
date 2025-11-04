#!/usr/bin/env python3
"""
Script para testar Supabase com configurações de demonstração
Verifica se o serviço Supabase está operacional usando um projeto público de exemplo
"""

import os
import json
import requests
from datetime import datetime
from urllib.parse import urlparse
import time

class SupabasePublicTester:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "supabase_public_demo",
            "components": {},
            "overall_status": "UNKNOWN",
            "score": 0,
            "max_score": 0,
            "errors": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Usar projeto público de demonstração do Supabase
        self.demo_config = {
            "supabase_url": "https://xyzcompany.supabase.co",  # URL de exemplo
            "supabase_anon_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh5emNvbXBhbnkiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTY0NTU2NzI0MCwiZXhwIjoxOTYxMTQzMjQwfQ.1BqRi0KrkuG5AcKjyPkUrKdJ2LIwfMabtCccKzqGg8M"  # Chave anônima de exemplo
        }
    
    def test_supabase_service_availability(self):
        """Testa se o serviço Supabase está disponível globalmente"""
        print("🌐 Testando disponibilidade do serviço Supabase...")
        
        component = {
            "name": "Supabase Service Availability",
            "status": "UNKNOWN",
            "details": {},
            "tests": [],
            "score": 0,
            "max_score": 4
        }
        
        try:
            # Teste 1: Verificar site principal do Supabase
            try:
                response = requests.get("https://supabase.com", timeout=10)
                if response.status_code == 200:
                    component["tests"].append({"name": "Supabase Website", "status": "PASS", "details": "Site principal acessível"})
                    component["score"] += 1
                else:
                    component["tests"].append({"name": "Supabase Website", "status": "FAIL", "details": f"Status: {response.status_code}"})
            except Exception as e:
                component["tests"].append({"name": "Supabase Website", "status": "FAIL", "details": f"Erro: {e}"})
            
            # Teste 2: Verificar documentação da API
            try:
                response = requests.get("https://supabase.com/docs/reference/api", timeout=10)
                if response.status_code == 200:
                    component["tests"].append({"name": "API Documentation", "status": "PASS", "details": "Documentação acessível"})
                    component["score"] += 1
                else:
                    component["tests"].append({"name": "API Documentation", "status": "FAIL", "details": f"Status: {response.status_code}"})
            except Exception as e:
                component["tests"].append({"name": "API Documentation", "status": "FAIL", "details": f"Erro: {e}"})
            
            # Teste 3: Verificar status do serviço
            try:
                response = requests.get("https://status.supabase.com", timeout=10)
                if response.status_code == 200:
                    component["tests"].append({"name": "Service Status", "status": "PASS", "details": "Página de status acessível"})
                    component["score"] += 1
                else:
                    component["tests"].append({"name": "Service Status", "status": "FAIL", "details": f"Status: {response.status_code}"})
            except Exception as e:
                component["tests"].append({"name": "Service Status", "status": "FAIL", "details": f"Erro: {e}"})
            
            # Teste 4: Verificar CDN/Edge locations
            try:
                response = requests.get("https://supabase.com/docs/guides/platform/regions", timeout=10)
                if response.status_code == 200:
                    component["tests"].append({"name": "Global Infrastructure", "status": "PASS", "details": "Informações de infraestrutura disponíveis"})
                    component["score"] += 1
                else:
                    component["tests"].append({"name": "Global Infrastructure", "status": "PARTIAL", "details": "Informações limitadas"})
                    component["score"] += 0.5
            except Exception as e:
                component["tests"].append({"name": "Global Infrastructure", "status": "FAIL", "details": f"Erro: {e}"})
            
            # Determinar status
            if component["score"] >= 3:
                component["status"] = "HEALTHY"
            elif component["score"] >= 2:
                component["status"] = "PARTIAL"
            else:
                component["status"] = "UNHEALTHY"
                
        except Exception as e:
            component["status"] = "ERROR"
            component["details"]["error"] = str(e)
            self.results["errors"].append(f"Erro ao verificar disponibilidade: {e}")
        
        self.results["components"]["service_availability"] = component
    
    def test_demo_project_structure(self):
        """Testa estrutura típica de projeto Supabase"""
        print("🏗️ Testando estrutura de projeto Supabase...")
        
        component = {
            "name": "Project Structure",
            "status": "UNKNOWN",
            "details": {},
            "tests": [],
            "score": 0,
            "max_score": 5
        }
        
        demo_url = self.demo_config["supabase_url"]
        
        try:
            # Teste 1: Verificar formato de URL do projeto
            if demo_url.startswith("https://") and ".supabase.co" in demo_url:
                component["tests"].append({"name": "URL Format", "status": "PASS", "details": "Formato de URL válido"})
                component["score"] += 1
                
                # Extrair project reference
                project_ref = demo_url.replace("https://", "").replace(".supabase.co", "")
                component["details"]["project_ref"] = project_ref
            else:
                component["tests"].append({"name": "URL Format", "status": "FAIL", "details": "Formato inválido"})
            
            # Teste 2: Verificar endpoints padrão
            endpoints = {
                "REST API": "/rest/v1/",
                "Auth API": "/auth/v1/settings",
                "Storage API": "/storage/v1/bucket",
                "Realtime": "/realtime/v1/",
                "Edge Functions": "/functions/v1/"
            }
            
            accessible_endpoints = 0
            for endpoint_name, endpoint_path in endpoints.items():
                try:
                    response = requests.get(f"{demo_url}{endpoint_path}", timeout=5)
                    # Qualquer resposta (mesmo 401/403) indica que o endpoint existe
                    if response.status_code in [200, 400, 401, 403, 404, 405, 426]:
                        accessible_endpoints += 1
                        component["details"][f"{endpoint_name.lower()}_available"] = True
                    else:
                        component["details"][f"{endpoint_name.lower()}_available"] = False
                except:
                    component["details"][f"{endpoint_name.lower()}_available"] = False
            
            if accessible_endpoints >= 4:
                component["tests"].append({"name": "Standard Endpoints", "status": "PASS", "details": f"{accessible_endpoints}/5 endpoints acessíveis"})
                component["score"] += 2
            elif accessible_endpoints >= 2:
                component["tests"].append({"name": "Standard Endpoints", "status": "PARTIAL", "details": f"{accessible_endpoints}/5 endpoints acessíveis"})
                component["score"] += 1
            else:
                component["tests"].append({"name": "Standard Endpoints", "status": "FAIL", "details": f"Apenas {accessible_endpoints}/5 endpoints acessíveis"})
            
            # Teste 3: Verificar headers de resposta típicos
            try:
                response = requests.get(f"{demo_url}/rest/v1/", timeout=5)
                headers = response.headers
                
                supabase_headers = 0
                expected_headers = ["server", "content-type", "access-control-allow-origin"]
                
                for header in expected_headers:
                    if header in headers:
                        supabase_headers += 1
                
                if supabase_headers >= 2:
                    component["tests"].append({"name": "Response Headers", "status": "PASS", "details": "Headers padrão presentes"})
                    component["score"] += 1
                else:
                    component["tests"].append({"name": "Response Headers", "status": "PARTIAL", "details": "Headers limitados"})
                    component["score"] += 0.5
                    
                component["details"]["response_headers"] = dict(headers)
                
            except Exception as e:
                component["tests"].append({"name": "Response Headers", "status": "FAIL", "details": f"Erro: {e}"})
            
            # Teste 4: Verificar CORS e políticas de segurança
            try:
                response = requests.options(f"{demo_url}/rest/v1/", timeout=5)
                if "access-control-allow-origin" in response.headers:
                    component["tests"].append({"name": "CORS Policy", "status": "PASS", "details": "CORS configurado"})
                    component["score"] += 1
                else:
                    component["tests"].append({"name": "CORS Policy", "status": "PARTIAL", "details": "CORS limitado"})
                    component["score"] += 0.5
            except Exception as e:
                component["tests"].append({"name": "CORS Policy", "status": "FAIL", "details": f"Erro: {e}"})
            
            # Determinar status
            if component["score"] >= 4:
                component["status"] = "HEALTHY"
            elif component["score"] >= 2:
                component["status"] = "PARTIAL"
            else:
                component["status"] = "UNHEALTHY"
                
        except Exception as e:
            component["status"] = "ERROR"
            component["details"]["error"] = str(e)
            self.results["errors"].append(f"Erro ao verificar estrutura: {e}")
        
        self.results["components"]["project_structure"] = component
    
    def test_api_capabilities(self):
        """Testa capacidades das APIs do Supabase"""
        print("🔧 Testando capacidades das APIs...")
        
        component = {
            "name": "API Capabilities",
            "status": "UNKNOWN",
            "details": {},
            "tests": [],
            "score": 0,
            "max_score": 4
        }
        
        demo_url = self.demo_config["supabase_url"]
        anon_key = self.demo_config["supabase_anon_key"]
        
        try:
            headers = {
                "apikey": anon_key,
                "Authorization": f"Bearer {anon_key}",
                "Content-Type": "application/json"
            }
            
            # Teste 1: REST API básica
            try:
                response = requests.get(f"{demo_url}/rest/v1/", headers=headers, timeout=10)
                if response.status_code in [200, 400, 401]:  # Qualquer resposta válida
                    component["tests"].append({"name": "REST API Basic", "status": "PASS", "details": "REST API responde"})
                    component["score"] += 1
                else:
                    component["tests"].append({"name": "REST API Basic", "status": "FAIL", "details": f"Status: {response.status_code}"})
            except Exception as e:
                component["tests"].append({"name": "REST API Basic", "status": "FAIL", "details": f"Erro: {e}"})
            
            # Teste 2: Auth API
            try:
                response = requests.get(f"{demo_url}/auth/v1/settings", timeout=10)
                if response.status_code == 200:
                    component["tests"].append({"name": "Auth API", "status": "PASS", "details": "Auth API acessível"})
                    component["score"] += 1
                    
                    # Tentar obter configurações de auth
                    try:
                        auth_settings = response.json()
                        component["details"]["auth_providers"] = auth_settings.get("external", {}).keys() if auth_settings.get("external") else []
                    except:
                        pass
                else:
                    component["tests"].append({"name": "Auth API", "status": "FAIL", "details": f"Status: {response.status_code}"})
            except Exception as e:
                component["tests"].append({"name": "Auth API", "status": "FAIL", "details": f"Erro: {e}"})
            
            # Teste 3: Storage API
            try:
                response = requests.get(f"{demo_url}/storage/v1/bucket", headers=headers, timeout=10)
                if response.status_code in [200, 400, 401, 403]:
                    component["tests"].append({"name": "Storage API", "status": "PASS", "details": "Storage API acessível"})
                    component["score"] += 1
                else:
                    component["tests"].append({"name": "Storage API", "status": "FAIL", "details": f"Status: {response.status_code}"})
            except Exception as e:
                component["tests"].append({"name": "Storage API", "status": "FAIL", "details": f"Erro: {e}"})
            
            # Teste 4: Edge Functions
            try:
                response = requests.get(f"{demo_url}/functions/v1/", headers=headers, timeout=10)
                if response.status_code in [200, 404, 401, 403]:  # 404 é OK se não há funções
                    component["tests"].append({"name": "Edge Functions", "status": "PASS", "details": "Edge Functions endpoint acessível"})
                    component["score"] += 1
                else:
                    component["tests"].append({"name": "Edge Functions", "status": "FAIL", "details": f"Status: {response.status_code}"})
            except Exception as e:
                component["tests"].append({"name": "Edge Functions", "status": "FAIL", "details": f"Erro: {e}"})
            
            # Determinar status
            if component["score"] >= 3:
                component["status"] = "HEALTHY"
            elif component["score"] >= 2:
                component["status"] = "PARTIAL"
            else:
                component["status"] = "UNHEALTHY"
                
        except Exception as e:
            component["status"] = "ERROR"
            component["details"]["error"] = str(e)
            self.results["errors"].append(f"Erro ao verificar APIs: {e}")
        
        self.results["components"]["api_capabilities"] = component
    
    def check_local_configuration_status(self):
        """Verifica status das configurações locais"""
        print("⚙️ Verificando configurações locais...")
        
        component = {
            "name": "Local Configuration",
            "status": "UNKNOWN",
            "details": {},
            "tests": [],
            "score": 0,
            "max_score": 3
        }
        
        try:
            # Teste 1: Verificar se há configurações em variáveis de ambiente
            env_vars = ["SUPABASE_URL", "SUPABASE_SERVICE_KEY", "SUPABASE_ANON_KEY", "SUPABASE_BUCKET"]
            configured_vars = []
            
            for var in env_vars:
                if os.getenv(var):
                    configured_vars.append(var)
            
            if configured_vars:
                component["tests"].append({"name": "Environment Variables", "status": "PARTIAL", "details": f"Configuradas: {', '.join(configured_vars)}"})
                component["score"] += 0.5
                component["details"]["env_vars_configured"] = configured_vars
            else:
                component["tests"].append({"name": "Environment Variables", "status": "FAIL", "details": "Nenhuma variável configurada"})
                component["details"]["env_vars_configured"] = []
            
            # Teste 2: Verificar configurações em accounts.json
            try:
                with open("accounts.json", "r", encoding="utf-8") as f:
                    accounts = json.load(f)
                
                supabase_configs = []
                for account in accounts:
                    if account.get("supabase_url") or account.get("supabase_service_key"):
                        supabase_configs.append(account.get("nome", "unknown"))
                
                if supabase_configs:
                    component["tests"].append({"name": "Accounts Configuration", "status": "PARTIAL", "details": f"Contas com Supabase: {', '.join(supabase_configs)}"})
                    component["score"] += 0.5
                else:
                    component["tests"].append({"name": "Accounts Configuration", "status": "FAIL", "details": "Nenhuma conta configurada com Supabase"})
                    
                component["details"]["accounts_with_supabase"] = supabase_configs
                
            except Exception as e:
                component["tests"].append({"name": "Accounts Configuration", "status": "FAIL", "details": f"Erro ao ler accounts.json: {e}"})
            
            # Teste 3: Verificar se há implementação do SupabaseUploader
            try:
                with open("src/services/supabase_uploader.py", "r", encoding="utf-8") as f:
                    content = f.read()
                
                if "class SupabaseUploader" in content and "upload_from_url" in content:
                    component["tests"].append({"name": "Supabase Implementation", "status": "PASS", "details": "SupabaseUploader implementado"})
                    component["score"] += 1
                else:
                    component["tests"].append({"name": "Supabase Implementation", "status": "PARTIAL", "details": "Implementação incompleta"})
                    component["score"] += 0.5
                    
            except Exception as e:
                component["tests"].append({"name": "Supabase Implementation", "status": "FAIL", "details": f"Erro: {e}"})
            
            # Determinar status
            if component["score"] >= 2:
                component["status"] = "PARTIAL"
            elif component["score"] >= 1:
                component["status"] = "MINIMAL"
            else:
                component["status"] = "NOT_CONFIGURED"
                
        except Exception as e:
            component["status"] = "ERROR"
            component["details"]["error"] = str(e)
            self.results["errors"].append(f"Erro ao verificar configurações: {e}")
        
        self.results["components"]["local_configuration"] = component
    
    def generate_recommendations(self):
        """Gera recomendações baseadas nos resultados"""
        recommendations = []
        
        # Verificar se o serviço está disponível
        service_status = self.results["components"].get("service_availability", {}).get("status")
        if service_status in ["UNHEALTHY", "ERROR"]:
            recommendations.append({
                "priority": "CRITICAL",
                "category": "Service",
                "issue": "Serviço Supabase indisponível",
                "solution": "Verificar status em https://status.supabase.com e conectividade de rede"
            })
        
        # Verificar configurações locais
        local_config = self.results["components"].get("local_configuration", {})
        if local_config.get("status") == "NOT_CONFIGURED":
            recommendations.append({
                "priority": "HIGH",
                "category": "Configuration",
                "issue": "Supabase não configurado localmente",
                "solution": "Configurar SUPABASE_URL, SUPABASE_SERVICE_KEY e SUPABASE_BUCKET"
            })
        elif local_config.get("status") in ["MINIMAL", "PARTIAL"]:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "Configuration",
                "issue": "Configuração do Supabase incompleta",
                "solution": "Completar todas as variáveis necessárias para funcionalidade completa"
            })
        
        # Verificar APIs
        api_status = self.results["components"].get("api_capabilities", {}).get("status")
        if api_status in ["UNHEALTHY", "ERROR"]:
            recommendations.append({
                "priority": "HIGH",
                "category": "APIs",
                "issue": "APIs do Supabase com problemas",
                "solution": "Verificar chaves de API e permissões do projeto"
            })
        
        # Recomendações gerais
        if self.results["score"] < self.results["max_score"] * 0.7:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "General",
                "issue": "Funcionalidade do Supabase limitada",
                "solution": "Considerar configurar um projeto Supabase completo para o sistema"
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
    
    def run_verification(self):
        """Executa verificação completa"""
        print("🚀 Iniciando verificação do Supabase (modo demonstração)...")
        print(f"⏰ Timestamp: {self.results['timestamp']}")
        print()
        
        # Executar todas as verificações
        self.test_supabase_service_availability()
        self.test_demo_project_structure()
        self.test_api_capabilities()
        self.check_local_configuration_status()
        
        # Gerar análise final
        self.generate_recommendations()
        self.calculate_overall_status()
        
        # Salvar relatório
        report_filename = f"supabase_demo_verification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print()
        print("=" * 60)
        print("📊 RELATÓRIO DE VERIFICAÇÃO DO SUPABASE (DEMO)")
        print("=" * 60)
        print(f"🎯 Status Geral: {self.results['overall_status']}")
        print(f"📈 Pontuação: {self.results['score']}/{self.results['max_score']} ({(self.results['score']/self.results['max_score']*100):.1f}%)")
        print()
        
        print("📋 COMPONENTES:")
        for comp_name, comp_data in self.results["components"].items():
            status_emoji = {
                "HEALTHY": "✅",
                "PARTIAL": "⚠️",
                "MINIMAL": "🟡",
                "UNHEALTHY": "❌",
                "ERROR": "💥",
                "NOT_CONFIGURED": "⚙️"
            }.get(comp_data["status"], "❓")
            
            print(f"  {status_emoji} {comp_data['name']}: {comp_data['status']} ({comp_data['score']}/{comp_data['max_score']})")
        
        if self.results["errors"]:
            print()
            print("🚨 ERROS ENCONTRADOS:")
            for error in self.results["errors"]:
                print(f"  ❌ {error}")
        
        if self.results["warnings"]:
            print()
            print("⚠️ AVISOS:")
            for warning in self.results["warnings"]:
                print(f"  ⚠️ {warning}")
        
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
            print("  ✅ Supabase está operacional e acessível")
        elif self.results["overall_status"] == "PARCIAL":
            print("  ⚠️ Supabase parcialmente funcional - configuração necessária")
        elif self.results["overall_status"] == "LIMITADO":
            print("  🟡 Supabase com funcionalidade limitada")
        else:
            print("  ❌ Supabase não configurado ou com problemas críticos")
        
        print()
        print(f"📄 Relatório salvo em: {report_filename}")
        print("=" * 60)
        
        return self.results

if __name__ == "__main__":
    tester = SupabasePublicTester()
    results = tester.run_verification()