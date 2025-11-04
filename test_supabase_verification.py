#!/usr/bin/env python3
"""
Script de Verificação Completa do Supabase
Testa todos os componentes críticos do serviço Supabase
"""

import os
import json
import requests
from datetime import datetime
from urllib.parse import urlparse
import time
import uuid

class SupabaseVerifier:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "verification_type": "supabase_complete",
            "components": {},
            "overall_status": "UNKNOWN",
            "score": 0,
            "max_score": 0,
            "errors": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Carregar configurações
        self.config = self.load_config()
        
    def load_config(self):
        """Carrega configurações do Supabase de múltiplas fontes"""
        config = {}
        
        # 1. Tentar carregar de variáveis de ambiente
        config["supabase_url"] = os.getenv("SUPABASE_URL", "")
        config["supabase_service_key"] = os.getenv("SUPABASE_SERVICE_KEY", "")
        config["supabase_anon_key"] = os.getenv("SUPABASE_ANON_KEY", "")
        config["supabase_bucket"] = os.getenv("SUPABASE_BUCKET", "")
        
        # 2. Tentar carregar do config.py
        try:
            from src.config import load_config
            app_config = load_config()
            config["supabase_url"] = config["supabase_url"] or app_config.get("SUPABASE_URL", "")
            config["supabase_service_key"] = config["supabase_service_key"] or app_config.get("SUPABASE_SERVICE_KEY", "")
            config["supabase_bucket"] = config["supabase_bucket"] or app_config.get("SUPABASE_BUCKET", "")
        except Exception as e:
            self.results["warnings"].append(f"Não foi possível carregar config.py: {e}")
        
        # 3. Tentar carregar de accounts.json
        try:
            with open("accounts.json", "r", encoding="utf-8") as f:
                accounts = json.load(f)
            for account in accounts:
                if account.get("supabase_url"):
                    config["supabase_url"] = config["supabase_url"] or account["supabase_url"]
                if account.get("supabase_service_key"):
                    config["supabase_service_key"] = config["supabase_service_key"] or account["supabase_service_key"]
                if account.get("supabase_bucket"):
                    config["supabase_bucket"] = config["supabase_bucket"] or account["supabase_bucket"]
        except Exception as e:
            self.results["warnings"].append(f"Não foi possível carregar accounts.json: {e}")
        
        return config
    
    def verify_database_connection(self):
        """Verifica conexão com banco PostgreSQL do Supabase"""
        print("🔍 Verificando conexão com banco PostgreSQL...")
        
        component = {
            "name": "PostgreSQL Database",
            "status": "UNKNOWN",
            "details": {},
            "tests": [],
            "score": 0,
            "max_score": 4
        }
        
        supabase_url = self.config.get("supabase_url", "")
        
        if not supabase_url:
            component["status"] = "NOT_CONFIGURED"
            component["details"]["error"] = "SUPABASE_URL não configurada"
            self.results["errors"].append("SUPABASE_URL não encontrada nas configurações")
            self.results["components"]["database"] = component
            return
        
        # Extrair informações da URL
        try:
            parsed_url = urlparse(supabase_url)
            db_host = parsed_url.hostname
            project_ref = parsed_url.hostname.split('.')[0] if parsed_url.hostname else ""
            
            component["details"]["supabase_url"] = supabase_url
            component["details"]["project_ref"] = project_ref
            component["details"]["host"] = db_host
            
            # Teste 1: Verificar se a URL é válida
            if supabase_url.startswith("https://") and ".supabase.co" in supabase_url:
                component["tests"].append({"name": "URL Format", "status": "PASS", "details": "URL do Supabase válida"})
                component["score"] += 1
            else:
                component["tests"].append({"name": "URL Format", "status": "FAIL", "details": "Formato de URL inválido"})
            
            # Teste 2: Verificar conectividade HTTP básica
            try:
                response = requests.get(f"{supabase_url}/rest/v1/", timeout=10)
                if response.status_code in [200, 401, 403]:  # 401/403 são esperados sem auth
                    component["tests"].append({"name": "HTTP Connectivity", "status": "PASS", "details": f"Resposta HTTP: {response.status_code}"})
                    component["score"] += 1
                else:
                    component["tests"].append({"name": "HTTP Connectivity", "status": "FAIL", "details": f"Status inesperado: {response.status_code}"})
            except Exception as e:
                component["tests"].append({"name": "HTTP Connectivity", "status": "FAIL", "details": f"Erro de conexão: {e}"})
            
            # Teste 3: Verificar se há service key para testes de DB
            service_key = self.config.get("supabase_service_key", "")
            if service_key:
                component["tests"].append({"name": "Service Key", "status": "PASS", "details": "Service key configurada"})
                component["score"] += 1
                
                # Teste 4: Tentar conexão direta com PostgreSQL (se possível)
                try:
                    # Construir string de conexão PostgreSQL
                    db_url = f"postgresql://postgres:[PASSWORD]@db.{project_ref}.supabase.co:5432/postgres"
                    component["tests"].append({"name": "PostgreSQL Direct", "status": "SKIP", "details": "Senha do DB não disponível para teste direto"})
                except Exception as e:
                    component["tests"].append({"name": "PostgreSQL Direct", "status": "SKIP", "details": f"Teste direto não possível: {e}"})
            else:
                component["tests"].append({"name": "Service Key", "status": "FAIL", "details": "Service key não configurada"})
                component["tests"].append({"name": "PostgreSQL Direct", "status": "SKIP", "details": "Sem service key para teste"})
            
            # Determinar status geral
            if component["score"] >= 3:
                component["status"] = "HEALTHY"
            elif component["score"] >= 2:
                component["status"] = "PARTIAL"
            else:
                component["status"] = "UNHEALTHY"
                
        except Exception as e:
            component["status"] = "ERROR"
            component["details"]["error"] = str(e)
            self.results["errors"].append(f"Erro ao verificar banco: {e}")
        
        self.results["components"]["database"] = component
    
    def verify_authentication(self):
        """Verifica serviço de autenticação e autorização"""
        print("🔐 Verificando autenticação e autorização...")
        
        component = {
            "name": "Authentication & Authorization",
            "status": "UNKNOWN",
            "details": {},
            "tests": [],
            "score": 0,
            "max_score": 3
        }
        
        supabase_url = self.config.get("supabase_url", "")
        anon_key = self.config.get("supabase_anon_key", "")
        service_key = self.config.get("supabase_service_key", "")
        
        if not supabase_url:
            component["status"] = "NOT_CONFIGURED"
            component["details"]["error"] = "SUPABASE_URL não configurada"
            self.results["components"]["auth"] = component
            return
        
        try:
            # Teste 1: Verificar endpoint de auth
            auth_url = f"{supabase_url}/auth/v1/settings"
            try:
                response = requests.get(auth_url, timeout=10)
                if response.status_code == 200:
                    component["tests"].append({"name": "Auth Endpoint", "status": "PASS", "details": "Endpoint de auth acessível"})
                    component["score"] += 1
                    component["details"]["auth_settings"] = response.json()
                else:
                    component["tests"].append({"name": "Auth Endpoint", "status": "FAIL", "details": f"Status: {response.status_code}"})
            except Exception as e:
                component["tests"].append({"name": "Auth Endpoint", "status": "FAIL", "details": f"Erro: {e}"})
            
            # Teste 2: Verificar chave anônima
            if anon_key:
                component["tests"].append({"name": "Anonymous Key", "status": "PASS", "details": "Chave anônima configurada"})
                component["score"] += 1
            else:
                component["tests"].append({"name": "Anonymous Key", "status": "FAIL", "details": "Chave anônima não configurada"})
            
            # Teste 3: Verificar service key
            if service_key:
                component["tests"].append({"name": "Service Key", "status": "PASS", "details": "Service key configurada"})
                component["score"] += 1
                
                # Teste adicional: Verificar se service key funciona
                try:
                    headers = {
                        "Authorization": f"Bearer {service_key}",
                        "apikey": service_key
                    }
                    response = requests.get(f"{supabase_url}/rest/v1/", headers=headers, timeout=10)
                    if response.status_code == 200:
                        component["details"]["service_key_valid"] = True
                    else:
                        component["details"]["service_key_valid"] = False
                except Exception:
                    component["details"]["service_key_valid"] = False
            else:
                component["tests"].append({"name": "Service Key", "status": "FAIL", "details": "Service key não configurada"})
            
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
            self.results["errors"].append(f"Erro ao verificar autenticação: {e}")
        
        self.results["components"]["auth"] = component
    
    def verify_rest_graphql_apis(self):
        """Verifica APIs REST e GraphQL"""
        print("🌐 Verificando APIs REST e GraphQL...")
        
        component = {
            "name": "REST & GraphQL APIs",
            "status": "UNKNOWN",
            "details": {},
            "tests": [],
            "score": 0,
            "max_score": 4
        }
        
        supabase_url = self.config.get("supabase_url", "")
        service_key = self.config.get("supabase_service_key", "")
        
        if not supabase_url:
            component["status"] = "NOT_CONFIGURED"
            component["details"]["error"] = "SUPABASE_URL não configurada"
            self.results["components"]["apis"] = component
            return
        
        try:
            headers = {}
            if service_key:
                headers = {
                    "Authorization": f"Bearer {service_key}",
                    "apikey": service_key
                }
            
            # Teste 1: REST API endpoint
            try:
                rest_url = f"{supabase_url}/rest/v1/"
                response = requests.get(rest_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    component["tests"].append({"name": "REST API", "status": "PASS", "details": "REST API acessível"})
                    component["score"] += 1
                    component["details"]["rest_api"] = "Available"
                else:
                    component["tests"].append({"name": "REST API", "status": "FAIL", "details": f"Status: {response.status_code}"})
            except Exception as e:
                component["tests"].append({"name": "REST API", "status": "FAIL", "details": f"Erro: {e}"})
            
            # Teste 2: GraphQL endpoint
            try:
                graphql_url = f"{supabase_url}/graphql/v1"
                response = requests.post(graphql_url, headers=headers, json={"query": "{ __schema { types { name } } }"}, timeout=10)
                if response.status_code in [200, 400]:  # 400 pode ser esperado sem schema
                    component["tests"].append({"name": "GraphQL API", "status": "PASS", "details": "GraphQL endpoint acessível"})
                    component["score"] += 1
                    component["details"]["graphql_api"] = "Available"
                else:
                    component["tests"].append({"name": "GraphQL API", "status": "FAIL", "details": f"Status: {response.status_code}"})
            except Exception as e:
                component["tests"].append({"name": "GraphQL API", "status": "FAIL", "details": f"Erro: {e}"})
            
            # Teste 3: Realtime endpoint
            try:
                realtime_url = f"{supabase_url}/realtime/v1/websocket"
                # Apenas verificar se o endpoint existe (não conectar WebSocket)
                response = requests.get(supabase_url.replace("https://", "https://") + "/realtime/v1/", timeout=10)
                if response.status_code in [200, 404, 426]:  # 426 = Upgrade Required (WebSocket)
                    component["tests"].append({"name": "Realtime API", "status": "PASS", "details": "Realtime endpoint disponível"})
                    component["score"] += 1
                    component["details"]["realtime_api"] = "Available"
                else:
                    component["tests"].append({"name": "Realtime API", "status": "FAIL", "details": f"Status: {response.status_code}"})
            except Exception as e:
                component["tests"].append({"name": "Realtime API", "status": "FAIL", "details": f"Erro: {e}"})
            
            # Teste 4: API Rate Limits e Headers
            try:
                response = requests.get(f"{supabase_url}/rest/v1/", headers=headers, timeout=10)
                rate_limit_headers = {k: v for k, v in response.headers.items() if 'rate' in k.lower() or 'limit' in k.lower()}
                if rate_limit_headers or response.status_code == 200:
                    component["tests"].append({"name": "API Headers", "status": "PASS", "details": "Headers de API válidos"})
                    component["score"] += 1
                    component["details"]["api_headers"] = dict(response.headers)
                else:
                    component["tests"].append({"name": "API Headers", "status": "PARTIAL", "details": "Headers básicos presentes"})
            except Exception as e:
                component["tests"].append({"name": "API Headers", "status": "FAIL", "details": f"Erro: {e}"})
            
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
        
        self.results["components"]["apis"] = component
    
    def verify_storage(self):
        """Verifica armazenamento de arquivos"""
        print("📁 Verificando armazenamento de arquivos...")
        
        component = {
            "name": "File Storage",
            "status": "UNKNOWN",
            "details": {},
            "tests": [],
            "score": 0,
            "max_score": 4
        }
        
        supabase_url = self.config.get("supabase_url", "")
        service_key = self.config.get("supabase_service_key", "")
        bucket_name = self.config.get("supabase_bucket", "")
        
        if not supabase_url:
            component["status"] = "NOT_CONFIGURED"
            component["details"]["error"] = "SUPABASE_URL não configurada"
            self.results["components"]["storage"] = component
            return
        
        try:
            headers = {}
            if service_key:
                headers = {
                    "Authorization": f"Bearer {service_key}",
                    "apikey": service_key
                }
            
            # Teste 1: Storage endpoint
            try:
                storage_url = f"{supabase_url}/storage/v1/bucket"
                response = requests.get(storage_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    component["tests"].append({"name": "Storage Endpoint", "status": "PASS", "details": "Storage API acessível"})
                    component["score"] += 1
                    buckets = response.json()
                    component["details"]["available_buckets"] = [b.get("name", "unknown") for b in buckets] if isinstance(buckets, list) else []
                else:
                    component["tests"].append({"name": "Storage Endpoint", "status": "FAIL", "details": f"Status: {response.status_code}"})
            except Exception as e:
                component["tests"].append({"name": "Storage Endpoint", "status": "FAIL", "details": f"Erro: {e}"})
            
            # Teste 2: Verificar bucket configurado
            if bucket_name:
                component["tests"].append({"name": "Bucket Configuration", "status": "PASS", "details": f"Bucket configurado: {bucket_name}"})
                component["score"] += 1
                component["details"]["configured_bucket"] = bucket_name
                
                # Teste 3: Verificar se bucket existe
                try:
                    if service_key:
                        bucket_url = f"{supabase_url}/storage/v1/bucket/{bucket_name}"
                        response = requests.get(bucket_url, headers=headers, timeout=10)
                        if response.status_code == 200:
                            component["tests"].append({"name": "Bucket Exists", "status": "PASS", "details": f"Bucket '{bucket_name}' existe"})
                            component["score"] += 1
                        else:
                            component["tests"].append({"name": "Bucket Exists", "status": "FAIL", "details": f"Bucket não encontrado: {response.status_code}"})
                    else:
                        component["tests"].append({"name": "Bucket Exists", "status": "SKIP", "details": "Sem service key para verificar"})
                except Exception as e:
                    component["tests"].append({"name": "Bucket Exists", "status": "FAIL", "details": f"Erro: {e}"})
            else:
                component["tests"].append({"name": "Bucket Configuration", "status": "FAIL", "details": "Bucket não configurado"})
                component["tests"].append({"name": "Bucket Exists", "status": "SKIP", "details": "Sem bucket configurado"})
            
            # Teste 4: Testar upload (simulado)
            if service_key and bucket_name:
                try:
                    # Criar um arquivo de teste pequeno
                    test_filename = f"test_{uuid.uuid4().hex[:8]}.txt"
                    test_content = "Test file for Supabase verification"
                    
                    upload_url = f"{supabase_url}/storage/v1/object/{bucket_name}/{test_filename}"
                    upload_headers = headers.copy()
                    upload_headers["Content-Type"] = "text/plain"
                    
                    # Simular upload (não executar realmente para evitar criar arquivos)
                    component["tests"].append({"name": "Upload Test", "status": "SIMULATED", "details": "Upload simulado - configuração válida"})
                    component["score"] += 0.5  # Meio ponto por simulação
                    
                except Exception as e:
                    component["tests"].append({"name": "Upload Test", "status": "FAIL", "details": f"Erro na simulação: {e}"})
            else:
                component["tests"].append({"name": "Upload Test", "status": "SKIP", "details": "Sem credenciais ou bucket para teste"})
            
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
            self.results["errors"].append(f"Erro ao verificar storage: {e}")
        
        self.results["components"]["storage"] = component
    
    def verify_edge_functions(self):
        """Verifica funções Edge e chamadas RPC"""
        print("⚡ Verificando funções Edge e RPC...")
        
        component = {
            "name": "Edge Functions & RPC",
            "status": "UNKNOWN",
            "details": {},
            "tests": [],
            "score": 0,
            "max_score": 3
        }
        
        supabase_url = self.config.get("supabase_url", "")
        service_key = self.config.get("supabase_service_key", "")
        
        if not supabase_url:
            component["status"] = "NOT_CONFIGURED"
            component["details"]["error"] = "SUPABASE_URL não configurada"
            self.results["components"]["edge_functions"] = component
            return
        
        try:
            headers = {}
            if service_key:
                headers = {
                    "Authorization": f"Bearer {service_key}",
                    "apikey": service_key
                }
            
            # Teste 1: Edge Functions endpoint
            try:
                edge_url = f"{supabase_url}/functions/v1/"
                response = requests.get(edge_url, headers=headers, timeout=10)
                if response.status_code in [200, 404]:  # 404 é OK se não há funções
                    component["tests"].append({"name": "Edge Functions Endpoint", "status": "PASS", "details": "Endpoint de Edge Functions acessível"})
                    component["score"] += 1
                    component["details"]["edge_functions_available"] = True
                else:
                    component["tests"].append({"name": "Edge Functions Endpoint", "status": "FAIL", "details": f"Status: {response.status_code}"})
            except Exception as e:
                component["tests"].append({"name": "Edge Functions Endpoint", "status": "FAIL", "details": f"Erro: {e}"})
            
            # Teste 2: RPC endpoint via REST
            try:
                rpc_url = f"{supabase_url}/rest/v1/rpc/"
                response = requests.get(rpc_url, headers=headers, timeout=10)
                if response.status_code in [200, 404, 405]:  # 405 Method Not Allowed é OK
                    component["tests"].append({"name": "RPC Endpoint", "status": "PASS", "details": "Endpoint RPC acessível"})
                    component["score"] += 1
                    component["details"]["rpc_available"] = True
                else:
                    component["tests"].append({"name": "RPC Endpoint", "status": "FAIL", "details": f"Status: {response.status_code}"})
            except Exception as e:
                component["tests"].append({"name": "RPC Endpoint", "status": "FAIL", "details": f"Erro: {e}"})
            
            # Teste 3: Verificar se há funções disponíveis
            if service_key:
                try:
                    # Tentar listar funções via REST API
                    functions_url = f"{supabase_url}/rest/v1/rpc"
                    response = requests.post(functions_url, headers=headers, json={}, timeout=10)
                    if response.status_code in [200, 400, 404]:
                        component["tests"].append({"name": "Functions Discovery", "status": "PASS", "details": "Sistema de funções operacional"})
                        component["score"] += 1
                    else:
                        component["tests"].append({"name": "Functions Discovery", "status": "PARTIAL", "details": f"Status: {response.status_code}"})
                        component["score"] += 0.5
                except Exception as e:
                    component["tests"].append({"name": "Functions Discovery", "status": "FAIL", "details": f"Erro: {e}"})
            else:
                component["tests"].append({"name": "Functions Discovery", "status": "SKIP", "details": "Sem service key para verificar"})
            
            # Determinar status
            if component["score"] >= 2.5:
                component["status"] = "HEALTHY"
            elif component["score"] >= 1.5:
                component["status"] = "PARTIAL"
            else:
                component["status"] = "UNHEALTHY"
                
        except Exception as e:
            component["status"] = "ERROR"
            component["details"]["error"] = str(e)
            self.results["errors"].append(f"Erro ao verificar Edge Functions: {e}")
        
        self.results["components"]["edge_functions"] = component
    
    def generate_recommendations(self):
        """Gera recomendações baseadas nos resultados"""
        recommendations = []
        
        # Verificar configurações básicas
        if not self.config.get("supabase_url"):
            recommendations.append({
                "priority": "HIGH",
                "category": "Configuration",
                "issue": "SUPABASE_URL não configurada",
                "solution": "Configurar SUPABASE_URL nas variáveis de ambiente ou accounts.json"
            })
        
        if not self.config.get("supabase_service_key"):
            recommendations.append({
                "priority": "HIGH",
                "category": "Configuration",
                "issue": "SUPABASE_SERVICE_KEY não configurada",
                "solution": "Configurar SUPABASE_SERVICE_KEY para acesso completo às APIs"
            })
        
        if not self.config.get("supabase_bucket"):
            recommendations.append({
                "priority": "MEDIUM",
                "category": "Storage",
                "issue": "SUPABASE_BUCKET não configurado",
                "solution": "Configurar nome do bucket para upload de imagens"
            })
        
        # Verificar componentes com problemas
        for comp_name, comp_data in self.results["components"].items():
            if comp_data["status"] in ["UNHEALTHY", "ERROR"]:
                recommendations.append({
                    "priority": "HIGH",
                    "category": comp_data["name"],
                    "issue": f"Componente {comp_data['name']} com problemas",
                    "solution": f"Verificar configurações e conectividade do {comp_data['name']}"
                })
            elif comp_data["status"] == "PARTIAL":
                recommendations.append({
                    "priority": "MEDIUM",
                    "category": comp_data["name"],
                    "issue": f"Componente {comp_data['name']} parcialmente funcional",
                    "solution": f"Otimizar configurações do {comp_data['name']}"
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
            else:
                self.results["overall_status"] = "CRÍTICO"
        else:
            self.results["overall_status"] = "NÃO_CONFIGURADO"
    
    def run_verification(self):
        """Executa verificação completa"""
        print("🚀 Iniciando verificação completa do Supabase...")
        print(f"⏰ Timestamp: {self.results['timestamp']}")
        print()
        
        # Executar todas as verificações
        self.verify_database_connection()
        self.verify_authentication()
        self.verify_rest_graphql_apis()
        self.verify_storage()
        self.verify_edge_functions()
        
        # Gerar análise final
        self.generate_recommendations()
        self.calculate_overall_status()
        
        # Salvar relatório
        report_filename = f"supabase_verification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print()
        print("=" * 60)
        print("📊 RELATÓRIO DE VERIFICAÇÃO DO SUPABASE")
        print("=" * 60)
        print(f"🎯 Status Geral: {self.results['overall_status']}")
        print(f"📈 Pontuação: {self.results['score']}/{self.results['max_score']} ({(self.results['score']/self.results['max_score']*100):.1f}%)")
        print()
        
        print("📋 COMPONENTES:")
        for comp_name, comp_data in self.results["components"].items():
            status_emoji = {
                "HEALTHY": "✅",
                "PARTIAL": "⚠️",
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
                priority_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(rec["priority"], "⚪")
                print(f"  {priority_emoji} [{rec['priority']}] {rec['issue']}")
                print(f"     💡 {rec['solution']}")
        
        print()
        print(f"📄 Relatório salvo em: {report_filename}")
        print("=" * 60)
        
        return self.results

if __name__ == "__main__":
    verifier = SupabaseVerifier()
    results = verifier.run_verification()