#!/usr/bin/env python3
"""
Script para testar conectividade completa com Supabase
Testa PostgreSQL, APIs REST, Storage e autenticação
"""

import os
import json
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
import base64

class SupabaseConnectivityTester:
    def __init__(self):
        self.credentials = {
            "url": os.environ.get("SUPABASE_URL", "https://ccvfdupucmsjxwtfwzkd.supabase.co"),
            "service_key": os.environ.get("SUPABASE_SERVICE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNjdmZkdXB1Y21zanh3dGZ3emtkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg3OTgwNywiZXhwIjoyMDc1NDU1ODA3fQ.HcQb9CpoF9sQcRUBQWmcmx6RmokXd64FbGpBV3GVUzM"),
            "anon_key": os.environ.get("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNjdmZkdXB1Y21zanh3dGZ3emtkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4Nzk4MDcsImV4cCI6MjA3NTQ1NTgwN30.2M9-ieZ-PMnO7NQ-aDHjxor4ytAHa0pKwH7j1gsrXjI"),
            "bucket": os.environ.get("SUPABASE_BUCKET", "instagram-images"),
            "project_ref": os.environ.get("SUPABASE_PROJECT_REF", "ccvfdupucmsjxwtfwzkd"),
            "db_url": os.environ.get("SUPABASE_DB_URL", "postgresql://postgres:HVt^le2l0QaDZ0JS@db.ccvfdupucmsjxwtfwzkd.supabase.co:5432/postgres")
        }
        
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "credentials_loaded": {},
            "connectivity_tests": {},
            "api_tests": {},
            "storage_tests": {},
            "overall_status": "UNKNOWN",
            "recommendations": []
        }
    
    def verify_credentials(self):
        """Verifica se as credenciais foram carregadas corretamente"""
        print("🔑 Verificando credenciais...")
        
        for key, value in self.credentials.items():
            if value and value != "":
                self.test_results["credentials_loaded"][key] = "LOADED"
                print(f"  ✅ {key}: Carregada")
            else:
                self.test_results["credentials_loaded"][key] = "MISSING"
                print(f"  ❌ {key}: Não encontrada")
        
        loaded_count = sum(1 for status in self.test_results["credentials_loaded"].values() if status == "LOADED")
        total_count = len(self.credentials)
        
        print(f"  📊 Credenciais carregadas: {loaded_count}/{total_count}")
        return loaded_count == total_count
    
    def test_basic_connectivity(self):
        """Testa conectividade básica com Supabase"""
        print("\n🌐 Testando conectividade básica...")
        
        tests = {
            "supabase_health": f"{self.credentials['url']}/rest/v1/",
            "supabase_auth": f"{self.credentials['url']}/auth/v1/settings",
            "supabase_storage": f"{self.credentials['url']}/storage/v1/bucket"
        }
        
        for test_name, url in tests.items():
            try:
                headers = {
                    "apikey": self.credentials["anon_key"],
                    "Authorization": f"Bearer {self.credentials['anon_key']}",
                    "Content-Type": "application/json"
                }
                
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as response:
                    status_code = response.getcode()
                    
                    if status_code in [200, 201, 401]:  # 401 é esperado para alguns endpoints sem auth
                        self.test_results["connectivity_tests"][test_name] = "SUCCESS"
                        print(f"  ✅ {test_name}: Conectado (HTTP {status_code})")
                    else:
                        self.test_results["connectivity_tests"][test_name] = f"HTTP_{status_code}"
                        print(f"  ⚠️ {test_name}: HTTP {status_code}")
            
            except urllib.error.HTTPError as e:
                if e.code in [401, 403]:  # Esperado para alguns endpoints
                    self.test_results["connectivity_tests"][test_name] = "SUCCESS_AUTH_REQUIRED"
                    print(f"  ✅ {test_name}: Conectado (Auth necessária)")
                else:
                    self.test_results["connectivity_tests"][test_name] = f"HTTP_ERROR_{e.code}"
                    print(f"  ❌ {test_name}: Erro HTTP {e.code}")
            
            except Exception as e:
                self.test_results["connectivity_tests"][test_name] = f"ERROR: {str(e)}"
                print(f"  ❌ {test_name}: Erro - {e}")
    
    def test_rest_api(self):
        """Testa APIs REST do Supabase"""
        print("\n🔌 Testando APIs REST...")
        
        # Teste de listagem de tabelas (usando service key)
        try:
            url = f"{self.credentials['url']}/rest/v1/"
            headers = {
                "apikey": self.credentials["service_key"],
                "Authorization": f"Bearer {self.credentials['service_key']}",
                "Content-Type": "application/json"
            }
            
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                status_code = response.getcode()
                response_data = response.read().decode('utf-8')
                
                if status_code == 200:
                    self.test_results["api_tests"]["rest_api"] = "SUCCESS"
                    print(f"  ✅ REST API: Funcionando (HTTP {status_code})")
                    
                    # Tentar parsear resposta
                    try:
                        if response_data:
                            data = json.loads(response_data)
                            print(f"    📄 Resposta recebida: {len(response_data)} caracteres")
                    except:
                        print(f"    📄 Resposta não-JSON recebida")
                else:
                    self.test_results["api_tests"]["rest_api"] = f"HTTP_{status_code}"
                    print(f"  ⚠️ REST API: HTTP {status_code}")
        
        except Exception as e:
            self.test_results["api_tests"]["rest_api"] = f"ERROR: {str(e)}"
            print(f"  ❌ REST API: Erro - {e}")
    
    def test_storage_api(self):
        """Testa API de Storage do Supabase"""
        print("\n📦 Testando Storage API...")
        
        # Teste de listagem de buckets
        try:
            url = f"{self.credentials['url']}/storage/v1/bucket"
            headers = {
                "apikey": self.credentials["service_key"],
                "Authorization": f"Bearer {self.credentials['service_key']}",
                "Content-Type": "application/json"
            }
            
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                status_code = response.getcode()
                response_data = response.read().decode('utf-8')
                
                if status_code == 200:
                    buckets = json.loads(response_data)
                    self.test_results["storage_tests"]["list_buckets"] = "SUCCESS"
                    print(f"  ✅ Listagem de buckets: Funcionando")
                    print(f"    📦 Buckets encontrados: {len(buckets)}")
                    
                    # Verificar se o bucket específico existe
                    bucket_names = [bucket.get("name", "") for bucket in buckets]
                    if self.credentials["bucket"] in bucket_names:
                        self.test_results["storage_tests"]["target_bucket"] = "EXISTS"
                        print(f"    ✅ Bucket '{self.credentials['bucket']}': Encontrado")
                    else:
                        self.test_results["storage_tests"]["target_bucket"] = "NOT_FOUND"
                        print(f"    ⚠️ Bucket '{self.credentials['bucket']}': Não encontrado")
                        print(f"    📋 Buckets disponíveis: {bucket_names}")
                else:
                    self.test_results["storage_tests"]["list_buckets"] = f"HTTP_{status_code}"
                    print(f"  ❌ Listagem de buckets: HTTP {status_code}")
        
        except Exception as e:
            self.test_results["storage_tests"]["list_buckets"] = f"ERROR: {str(e)}"
            print(f"  ❌ Storage API: Erro - {e}")
    
    def test_file_upload(self):
        """Testa upload de arquivo para o Storage"""
        print("\n📤 Testando upload de arquivo...")
        
        try:
            # Criar um arquivo de teste simples
            test_content = "Test file for Supabase Storage"
            test_filename = f"test_upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            url = f"{self.credentials['url']}/storage/v1/object/{self.credentials['bucket']}/{test_filename}"
            headers = {
                "apikey": self.credentials["service_key"],
                "Authorization": f"Bearer {self.credentials['service_key']}",
                "Content-Type": "text/plain"
            }
            
            data = test_content.encode('utf-8')
            req = urllib.request.Request(url, data=data, headers=headers, method='POST')
            
            with urllib.request.urlopen(req, timeout=15) as response:
                status_code = response.getcode()
                response_data = response.read().decode('utf-8')
                
                if status_code in [200, 201]:
                    self.test_results["storage_tests"]["file_upload"] = "SUCCESS"
                    print(f"  ✅ Upload de arquivo: Sucesso (HTTP {status_code})")
                    print(f"    📁 Arquivo: {test_filename}")
                    
                    # Tentar fazer download do arquivo para confirmar
                    self.test_file_download(test_filename)
                else:
                    self.test_results["storage_tests"]["file_upload"] = f"HTTP_{status_code}"
                    print(f"  ❌ Upload de arquivo: HTTP {status_code}")
                    print(f"    📄 Resposta: {response_data}")
        
        except urllib.error.HTTPError as e:
            error_response = e.read().decode('utf-8') if e.fp else "No response"
            self.test_results["storage_tests"]["file_upload"] = f"HTTP_ERROR_{e.code}"
            print(f"  ❌ Upload de arquivo: HTTP {e.code}")
            print(f"    📄 Erro: {error_response}")
        
        except Exception as e:
            self.test_results["storage_tests"]["file_upload"] = f"ERROR: {str(e)}"
            print(f"  ❌ Upload de arquivo: Erro - {e}")
    
    def test_file_download(self, filename):
        """Testa download de arquivo do Storage"""
        try:
            url = f"{self.credentials['url']}/storage/v1/object/{self.credentials['bucket']}/{filename}"
            headers = {
                "apikey": self.credentials["service_key"],
                "Authorization": f"Bearer {self.credentials['service_key']}"
            }
            
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                status_code = response.getcode()
                
                if status_code == 200:
                    content = response.read().decode('utf-8')
                    self.test_results["storage_tests"]["file_download"] = "SUCCESS"
                    print(f"    ✅ Download confirmado: {len(content)} caracteres")
                else:
                    self.test_results["storage_tests"]["file_download"] = f"HTTP_{status_code}"
                    print(f"    ⚠️ Download: HTTP {status_code}")
        
        except Exception as e:
            self.test_results["storage_tests"]["file_download"] = f"ERROR: {str(e)}"
            print(f"    ❌ Download: Erro - {e}")
    
    def generate_recommendations(self):
        """Gera recomendações baseadas nos testes"""
        recommendations = []
        
        # Verificar credenciais
        missing_creds = [k for k, v in self.test_results["credentials_loaded"].items() if v != "LOADED"]
        if missing_creds:
            recommendations.append({
                "priority": "HIGH",
                "category": "Credenciais",
                "issue": f"Credenciais não carregadas: {', '.join(missing_creds)}",
                "action": "Verificar variáveis de ambiente"
            })
        
        # Verificar conectividade
        failed_connections = [k for k, v in self.test_results["connectivity_tests"].items() if "ERROR" in v]
        if failed_connections:
            recommendations.append({
                "priority": "CRITICAL",
                "category": "Conectividade",
                "issue": f"Falhas de conexão: {', '.join(failed_connections)}",
                "action": "Verificar rede e URLs do Supabase"
            })
        
        # Verificar APIs
        failed_apis = [k for k, v in self.test_results["api_tests"].items() if "ERROR" in v]
        if failed_apis:
            recommendations.append({
                "priority": "HIGH",
                "category": "APIs",
                "issue": f"APIs com falha: {', '.join(failed_apis)}",
                "action": "Verificar chaves de API e permissões"
            })
        
        # Verificar Storage
        if self.test_results["storage_tests"].get("target_bucket") == "NOT_FOUND":
            recommendations.append({
                "priority": "MEDIUM",
                "category": "Storage",
                "issue": f"Bucket '{self.credentials['bucket']}' não encontrado",
                "action": "Criar bucket ou verificar nome"
            })
        
        if self.test_results["storage_tests"].get("file_upload", "").startswith("ERROR"):
            recommendations.append({
                "priority": "HIGH",
                "category": "Storage",
                "issue": "Upload de arquivos falhando",
                "action": "Verificar permissões do bucket e políticas RLS"
            })
        
        # Recomendações de sucesso
        if not recommendations:
            recommendations.append({
                "priority": "INFO",
                "category": "Status",
                "issue": "Todos os testes passaram",
                "action": "Supabase está configurado e funcionando corretamente"
            })
        
        self.test_results["recommendations"] = recommendations
        return recommendations
    
    def calculate_overall_status(self):
        """Calcula status geral baseado nos testes"""
        total_tests = 0
        successful_tests = 0
        
        # Contar testes de credenciais
        for status in self.test_results["credentials_loaded"].values():
            total_tests += 1
            if status == "LOADED":
                successful_tests += 1
        
        # Contar testes de conectividade
        for status in self.test_results["connectivity_tests"].values():
            total_tests += 1
            if "SUCCESS" in status:
                successful_tests += 1
        
        # Contar testes de API
        for status in self.test_results["api_tests"].values():
            total_tests += 1
            if status == "SUCCESS":
                successful_tests += 1
        
        # Contar testes de Storage
        for status in self.test_results["storage_tests"].values():
            total_tests += 1
            if status == "SUCCESS":
                successful_tests += 1
        
        if total_tests == 0:
            percentage = 0
        else:
            percentage = (successful_tests / total_tests) * 100
        
        if percentage >= 90:
            overall_status = "EXCELLENT"
        elif percentage >= 75:
            overall_status = "GOOD"
        elif percentage >= 50:
            overall_status = "PARTIAL"
        elif percentage >= 25:
            overall_status = "LIMITED"
        else:
            overall_status = "CRITICAL"
        
        self.test_results["overall_status"] = overall_status
        self.test_results["success_rate"] = f"{successful_tests}/{total_tests} ({percentage:.1f}%)"
        
        return overall_status, successful_tests, total_tests
    
    def save_test_report(self):
        """Salva relatório de testes"""
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"supabase_connectivity_test_{timestamp_str}.json"
        
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        return report_file
    
    def run_all_tests(self):
        """Executa todos os testes de conectividade"""
        print("=" * 70)
        print("🧪 TESTE COMPLETO DE CONECTIVIDADE SUPABASE")
        print("=" * 70)
        
        # 1. Verificar credenciais
        creds_ok = self.verify_credentials()
        
        if not creds_ok:
            print("\n❌ Credenciais incompletas. Abortando testes.")
            return self.test_results
        
        # 2. Teste de conectividade básica
        self.test_basic_connectivity()
        
        # 3. Teste de APIs REST
        self.test_rest_api()
        
        # 4. Teste de Storage
        self.test_storage_api()
        
        # 5. Teste de upload
        self.test_file_upload()
        
        # 6. Gerar recomendações
        recommendations = self.generate_recommendations()
        
        # 7. Calcular status geral
        overall_status, successful, total = self.calculate_overall_status()
        
        # 8. Salvar relatório
        report_file = self.save_test_report()
        
        # Exibir resumo
        print("\n" + "=" * 70)
        print("📊 RESUMO DOS TESTES")
        print("=" * 70)
        
        print(f"🎯 Status Geral: {overall_status}")
        print(f"📈 Taxa de Sucesso: {self.test_results['success_rate']}")
        print(f"📄 Relatório: {report_file}")
        
        print("\n🔍 RESULTADOS DETALHADOS:")
        print(f"  🔑 Credenciais: {sum(1 for v in self.test_results['credentials_loaded'].values() if v == 'LOADED')}/{len(self.test_results['credentials_loaded'])}")
        print(f"  🌐 Conectividade: {sum(1 for v in self.test_results['connectivity_tests'].values() if 'SUCCESS' in v)}/{len(self.test_results['connectivity_tests'])}")
        print(f"  🔌 APIs: {sum(1 for v in self.test_results['api_tests'].values() if v == 'SUCCESS')}/{len(self.test_results['api_tests'])}")
        print(f"  📦 Storage: {sum(1 for v in self.test_results['storage_tests'].values() if v == 'SUCCESS')}/{len(self.test_results['storage_tests'])}")
        
        if recommendations:
            print("\n💡 RECOMENDAÇÕES:")
            for rec in recommendations[:3]:  # Mostrar apenas as 3 principais
                priority_emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "INFO": "ℹ️"}.get(rec['priority'], "⚪")
                print(f"  {priority_emoji} [{rec['priority']}] {rec['issue']}")
                print(f"    💡 {rec['action']}")
        
        print("=" * 70)
        
        return self.test_results

if __name__ == "__main__":
    tester = SupabaseConnectivityTester()
    results = tester.run_all_tests()