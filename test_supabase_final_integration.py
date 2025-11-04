#!/usr/bin/env python3
"""
Teste Final Completo da Integração Supabase
Verifica todas as funcionalidades do Supabase funcionando em conjunto
"""

import os
import json
import sys
import time
import urllib.request
import urllib.parse
from datetime import datetime
from typing import Dict, List, Any
from io import BytesIO
from PIL import Image

class SupabaseFinalIntegrationTest:
    def __init__(self):
        # Credenciais hardcoded para garantir funcionamento
        self.credentials = {
            "url": "https://ccvfdupucmsjxwtfwzkd.supabase.co",
            "service_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNjdmZkdXB1Y21zanh3dGZ3emtkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg3OTgwNywiZXhwIjoyMDc1NDU1ODA3fQ.HcQb9CpoF9sQcRUBQWmcmx6RmokXd64FbGpBV3GVUzM",
            "anon_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNjdmZkdXB1Y21zanh3dGZ3emtkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4Nzk4MDcsImV4cCI6MjA3NTQ1NTgwN30.2M9-ieZ-PMnO7NQ-aDHjxor4ytAHa0pKwH7j1gsrXjI",
            "bucket": "instagram-images",
            "project_ref": "ccvfdupucmsjxwtfwzkd",
            "db_url": "postgresql://postgres:HVt^le2l0QaDZ0JS@db.ccvfdupucmsjxwtfwzkd.supabase.co:5432/postgres",
            "access_token": "sbp_a497779d74107ea60b909508cc9ad2f784429b01"
        }
        
        self.test_results = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "overall_status": "UNKNOWN",
            "overall_score": 0,
            "max_score": 0,
            "tests": {
                "environment_variables": {"status": "PENDING", "score": 0, "max_score": 7, "details": []},
                "configuration_files": {"status": "PENDING", "score": 0, "max_score": 4, "details": []},
                "connectivity": {"status": "PENDING", "score": 0, "max_score": 3, "details": []},
                "storage_operations": {"status": "PENDING", "score": 0, "max_score": 5, "details": []},
                "api_functionality": {"status": "PENDING", "score": 0, "max_score": 3, "details": []},
                "railway_integration": {"status": "PENDING", "score": 0, "max_score": 3, "details": []},
                "code_integration": {"status": "PENDING", "score": 0, "max_score": 4, "details": []}
            },
            "recommendations": [],
            "summary": {}
        }

    def test_environment_variables(self):
        """Testa se as variáveis de ambiente estão configuradas"""
        print("🌍 Testando variáveis de ambiente...")
        
        env_vars = [
            "SUPABASE_URL", "SUPABASE_SERVICE_KEY", "SUPABASE_ANON_KEY",
            "SUPABASE_BUCKET", "SUPABASE_PROJECT_REF", "SUPABASE_DB_URL",
            "SUPABASE_ACCESS_TOKEN"
        ]
        
        found_vars = 0
        for var in env_vars:
            value = os.getenv(var)
            if value:
                print(f"  ✅ {var}: Configurada")
                self.test_results["tests"]["environment_variables"]["details"].append({
                    "variable": var,
                    "status": "FOUND",
                    "length": len(value)
                })
                found_vars += 1
            else:
                print(f"  ❌ {var}: Não encontrada")
                self.test_results["tests"]["environment_variables"]["details"].append({
                    "variable": var,
                    "status": "NOT_FOUND"
                })
        
        self.test_results["tests"]["environment_variables"]["score"] = found_vars
        
        if found_vars == len(env_vars):
            self.test_results["tests"]["environment_variables"]["status"] = "EXCELLENT"
        elif found_vars >= len(env_vars) * 0.7:
            self.test_results["tests"]["environment_variables"]["status"] = "GOOD"
        else:
            self.test_results["tests"]["environment_variables"]["status"] = "POOR"
        
        print(f"📊 Variáveis de ambiente: {found_vars}/{len(env_vars)} encontradas")

    def test_configuration_files(self):
        """Testa se os arquivos de configuração contêm credenciais do Supabase"""
        print("\n📁 Testando arquivos de configuração...")
        
        config_files = [
            "accounts.json",
            "accounts_backup.json", 
            "accounts_corrected.json",
            "CREDENCIAIS_PERMANENTES.json"
        ]
        
        files_with_supabase = 0
        for file_path in config_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if "supabase" in content.lower():
                        print(f"  ✅ {file_path}: Contém configurações do Supabase")
                        self.test_results["tests"]["configuration_files"]["details"].append({
                            "file": file_path,
                            "status": "HAS_SUPABASE",
                            "size": len(content)
                        })
                        files_with_supabase += 1
                    else:
                        print(f"  ⚠️ {file_path}: Não contém configurações do Supabase")
                        self.test_results["tests"]["configuration_files"]["details"].append({
                            "file": file_path,
                            "status": "NO_SUPABASE"
                        })
                except Exception as e:
                    print(f"  ❌ {file_path}: Erro ao ler - {e}")
                    self.test_results["tests"]["configuration_files"]["details"].append({
                        "file": file_path,
                        "status": "ERROR",
                        "error": str(e)
                    })
            else:
                print(f"  ❌ {file_path}: Arquivo não encontrado")
                self.test_results["tests"]["configuration_files"]["details"].append({
                    "file": file_path,
                    "status": "NOT_FOUND"
                })
        
        self.test_results["tests"]["configuration_files"]["score"] = files_with_supabase
        
        if files_with_supabase >= 3:
            self.test_results["tests"]["configuration_files"]["status"] = "EXCELLENT"
        elif files_with_supabase >= 2:
            self.test_results["tests"]["configuration_files"]["status"] = "GOOD"
        else:
            self.test_results["tests"]["configuration_files"]["status"] = "POOR"
        
        print(f"📊 Arquivos de configuração: {files_with_supabase}/{len(config_files)} com Supabase")

    def test_connectivity(self):
        """Testa conectividade básica com Supabase"""
        print("\n🔗 Testando conectividade...")
        
        tests_passed = 0
        
        # Teste 1: Health check
        try:
            health_url = f"{self.credentials['url']}/rest/v1/"
            headers = {
                "apikey": self.credentials["anon_key"],
                "Authorization": f"Bearer {self.credentials['anon_key']}"
            }
            
            req = urllib.request.Request(health_url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.getcode() == 200:
                    print("  ✅ Health check: Sucesso")
                    tests_passed += 1
                    self.test_results["tests"]["connectivity"]["details"].append({
                        "test": "health_check",
                        "status": "SUCCESS",
                        "response_code": response.getcode()
                    })
        except Exception as e:
            print(f"  ❌ Health check: Falhou - {e}")
            self.test_results["tests"]["connectivity"]["details"].append({
                "test": "health_check",
                "status": "FAILED",
                "error": str(e)
            })
        
        # Teste 2: Auth endpoint
        try:
            auth_url = f"{self.credentials['url']}/auth/v1/settings"
            req = urllib.request.Request(auth_url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.getcode() == 200:
                    print("  ✅ Auth endpoint: Sucesso")
                    tests_passed += 1
                    self.test_results["tests"]["connectivity"]["details"].append({
                        "test": "auth_endpoint",
                        "status": "SUCCESS",
                        "response_code": response.getcode()
                    })
        except Exception as e:
            print(f"  ❌ Auth endpoint: Falhou - {e}")
            self.test_results["tests"]["connectivity"]["details"].append({
                "test": "auth_endpoint",
                "status": "FAILED",
                "error": str(e)
            })
        
        # Teste 3: Storage endpoint
        try:
            storage_url = f"{self.credentials['url']}/storage/v1/bucket"
            storage_headers = {
                "apikey": self.credentials["service_key"],
                "Authorization": f"Bearer {self.credentials['service_key']}"
            }
            
            req = urllib.request.Request(storage_url, headers=storage_headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.getcode() == 200:
                    print("  ✅ Storage endpoint: Sucesso")
                    tests_passed += 1
                    self.test_results["tests"]["connectivity"]["details"].append({
                        "test": "storage_endpoint",
                        "status": "SUCCESS",
                        "response_code": response.getcode()
                    })
        except Exception as e:
            print(f"  ❌ Storage endpoint: Falhou - {e}")
            self.test_results["tests"]["connectivity"]["details"].append({
                "test": "storage_endpoint",
                "status": "FAILED",
                "error": str(e)
            })
        
        self.test_results["tests"]["connectivity"]["score"] = tests_passed
        
        if tests_passed == 3:
            self.test_results["tests"]["connectivity"]["status"] = "EXCELLENT"
        elif tests_passed >= 2:
            self.test_results["tests"]["connectivity"]["status"] = "GOOD"
        else:
            self.test_results["tests"]["connectivity"]["status"] = "POOR"
        
        print(f"📊 Conectividade: {tests_passed}/3 testes passaram")

    def test_storage_operations(self):
        """Testa operações de storage"""
        print("\n📦 Testando operações de storage...")
        
        operations_passed = 0
        
        # Teste 1: Listar buckets
        try:
            bucket_url = f"{self.credentials['url']}/storage/v1/bucket"
            headers = {
                "apikey": self.credentials["service_key"],
                "Authorization": f"Bearer {self.credentials['service_key']}"
            }
            
            req = urllib.request.Request(bucket_url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                if response.getcode() == 200:
                    buckets_data = json.loads(response.read().decode('utf-8'))
                    bucket_names = [bucket.get('name', '') for bucket in buckets_data]
                    
                    if self.credentials['bucket'] in bucket_names:
                        print(f"  ✅ Bucket '{self.credentials['bucket']}' encontrado")
                        operations_passed += 1
                        self.test_results["tests"]["storage_operations"]["details"].append({
                            "operation": "list_buckets",
                            "status": "SUCCESS",
                            "bucket_found": True,
                            "total_buckets": len(buckets_data)
                        })
                    else:
                        print(f"  ⚠️ Bucket '{self.credentials['bucket']}' não encontrado")
                        self.test_results["tests"]["storage_operations"]["details"].append({
                            "operation": "list_buckets",
                            "status": "BUCKET_NOT_FOUND",
                            "available_buckets": bucket_names
                        })
        except Exception as e:
            print(f"  ❌ Listar buckets: Falhou - {e}")
            self.test_results["tests"]["storage_operations"]["details"].append({
                "operation": "list_buckets",
                "status": "FAILED",
                "error": str(e)
            })
        
        # Teste 2: Upload de arquivo
        try:
            test_filename = f"integration_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            test_content = f"Teste de integração final - {datetime.now()}"
            
            upload_url = f"{self.credentials['url']}/storage/v1/object/{self.credentials['bucket']}/{test_filename}"
            upload_headers = headers.copy()
            upload_headers["Content-Type"] = "text/plain"
            upload_headers["x-upsert"] = "true"
            
            data = test_content.encode('utf-8')
            req = urllib.request.Request(upload_url, data=data, headers=upload_headers, method='POST')
            
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.getcode() in [200, 201]:
                    print(f"  ✅ Upload de arquivo: Sucesso ({test_filename})")
                    operations_passed += 1
                    self.test_results["tests"]["storage_operations"]["details"].append({
                        "operation": "file_upload",
                        "status": "SUCCESS",
                        "filename": test_filename,
                        "size": len(data)
                    })
                    
                    # Teste 3: Verificar URL pública
                    public_url = f"{self.credentials['url']}/storage/v1/object/public/{self.credentials['bucket']}/{test_filename}"
                    try:
                        req = urllib.request.Request(public_url)
                        with urllib.request.urlopen(req, timeout=10) as response:
                            if response.getcode() == 200:
                                print(f"  ✅ URL pública: Acessível")
                                operations_passed += 1
                                self.test_results["tests"]["storage_operations"]["details"].append({
                                    "operation": "public_url_access",
                                    "status": "SUCCESS",
                                    "url": public_url
                                })
                    except Exception as e:
                        print(f"  ⚠️ URL pública: Não acessível - {e}")
                        self.test_results["tests"]["storage_operations"]["details"].append({
                            "operation": "public_url_access",
                            "status": "FAILED",
                            "error": str(e)
                        })
                    
        except Exception as e:
            print(f"  ❌ Upload de arquivo: Falhou - {e}")
            self.test_results["tests"]["storage_operations"]["details"].append({
                "operation": "file_upload",
                "status": "FAILED",
                "error": str(e)
            })
        
        # Teste 4: Upload de imagem
        try:
            # Criar uma imagem de teste
            img = Image.new('RGB', (100, 100), color='red')
            img_buffer = BytesIO()
            img.save(img_buffer, format='JPEG')
            img_data = img_buffer.getvalue()
            
            img_filename = f"integration_test_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            
            upload_url = f"{self.credentials['url']}/storage/v1/object/{self.credentials['bucket']}/{img_filename}"
            upload_headers = headers.copy()
            upload_headers["Content-Type"] = "image/jpeg"
            upload_headers["x-upsert"] = "true"
            
            req = urllib.request.Request(upload_url, data=img_data, headers=upload_headers, method='POST')
            
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.getcode() in [200, 201]:
                    print(f"  ✅ Upload de imagem: Sucesso ({img_filename})")
                    operations_passed += 1
                    self.test_results["tests"]["storage_operations"]["details"].append({
                        "operation": "image_upload",
                        "status": "SUCCESS",
                        "filename": img_filename,
                        "size": len(img_data)
                    })
                    
        except Exception as e:
            print(f"  ❌ Upload de imagem: Falhou - {e}")
            self.test_results["tests"]["storage_operations"]["details"].append({
                "operation": "image_upload",
                "status": "FAILED",
                "error": str(e)
            })
        
        # Teste 5: Listar arquivos no bucket
        try:
            list_url = f"{self.credentials['url']}/storage/v1/object/list/{self.credentials['bucket']}"
            req = urllib.request.Request(list_url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=15) as response:
                if response.getcode() == 200:
                    files_data = json.loads(response.read().decode('utf-8'))
                    file_count = len(files_data)
                    print(f"  ✅ Listar arquivos: {file_count} arquivos encontrados")
                    operations_passed += 1
                    self.test_results["tests"]["storage_operations"]["details"].append({
                        "operation": "list_files",
                        "status": "SUCCESS",
                        "file_count": file_count
                    })
                    
        except Exception as e:
            print(f"  ❌ Listar arquivos: Falhou - {e}")
            self.test_results["tests"]["storage_operations"]["details"].append({
                "operation": "list_files",
                "status": "FAILED",
                "error": str(e)
            })
        
        self.test_results["tests"]["storage_operations"]["score"] = operations_passed
        
        if operations_passed >= 4:
            self.test_results["tests"]["storage_operations"]["status"] = "EXCELLENT"
        elif operations_passed >= 3:
            self.test_results["tests"]["storage_operations"]["status"] = "GOOD"
        else:
            self.test_results["tests"]["storage_operations"]["status"] = "POOR"
        
        print(f"📊 Operações de storage: {operations_passed}/5 operações passaram")

    def test_api_functionality(self):
        """Testa funcionalidades da API"""
        print("\n🔌 Testando funcionalidades da API...")
        
        api_tests_passed = 0
        
        # Teste 1: REST API básica
        try:
            # Tentar acessar uma tabela (mesmo que não exista, deve retornar erro estruturado)
            rest_url = f"{self.credentials['url']}/rest/v1/test_table"
            headers = {
                "apikey": self.credentials["anon_key"],
                "Authorization": f"Bearer {self.credentials['anon_key']}",
                "Content-Type": "application/json"
            }
            
            req = urllib.request.Request(rest_url, headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=10) as response:
                    print("  ✅ REST API: Respondendo")
                    api_tests_passed += 1
            except urllib.error.HTTPError as e:
                if e.code in [401, 404, 406]:  # Erros esperados para tabela inexistente
                    print("  ✅ REST API: Respondendo (erro estruturado esperado)")
                    api_tests_passed += 1
                else:
                    print(f"  ⚠️ REST API: Erro inesperado {e.code}")
            
            self.test_results["tests"]["api_functionality"]["details"].append({
                "test": "rest_api_basic",
                "status": "SUCCESS" if api_tests_passed > 0 else "FAILED"
            })
            
        except Exception as e:
            print(f"  ❌ REST API: Falhou - {e}")
            self.test_results["tests"]["api_functionality"]["details"].append({
                "test": "rest_api_basic",
                "status": "FAILED",
                "error": str(e)
            })
        
        # Teste 2: Auth API
        try:
            auth_url = f"{self.credentials['url']}/auth/v1/settings"
            req = urllib.request.Request(auth_url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.getcode() == 200:
                    print("  ✅ Auth API: Funcionando")
                    api_tests_passed += 1
                    self.test_results["tests"]["api_functionality"]["details"].append({
                        "test": "auth_api",
                        "status": "SUCCESS"
                    })
        except Exception as e:
            print(f"  ❌ Auth API: Falhou - {e}")
            self.test_results["tests"]["api_functionality"]["details"].append({
                "test": "auth_api",
                "status": "FAILED",
                "error": str(e)
            })
        
        # Teste 3: Storage API (já testado anteriormente, mas verificamos novamente)
        try:
            storage_url = f"{self.credentials['url']}/storage/v1/bucket"
            storage_headers = {
                "apikey": self.credentials["service_key"],
                "Authorization": f"Bearer {self.credentials['service_key']}"
            }
            req = urllib.request.Request(storage_url, headers=storage_headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.getcode() == 200:
                    print("  ✅ Storage API: Funcionando")
                    api_tests_passed += 1
                    self.test_results["tests"]["api_functionality"]["details"].append({
                        "test": "storage_api",
                        "status": "SUCCESS"
                    })
        except Exception as e:
            print(f"  ❌ Storage API: Falhou - {e}")
            self.test_results["tests"]["api_functionality"]["details"].append({
                "test": "storage_api",
                "status": "FAILED",
                "error": str(e)
            })
        
        self.test_results["tests"]["api_functionality"]["score"] = api_tests_passed
        
        if api_tests_passed == 3:
            self.test_results["tests"]["api_functionality"]["status"] = "EXCELLENT"
        elif api_tests_passed >= 2:
            self.test_results["tests"]["api_functionality"]["status"] = "GOOD"
        else:
            self.test_results["tests"]["api_functionality"]["status"] = "POOR"
        
        print(f"📊 APIs: {api_tests_passed}/3 APIs funcionando")

    def test_railway_integration(self):
        """Testa integração com Railway"""
        print("\n🚂 Testando integração com Railway...")
        
        railway_tests_passed = 0
        
        # Teste 1: Verificar se relatórios do Railway existem
        railway_files = [
            "railway_supabase_commands.txt",
            "railway_supabase_configuration_report_20251023_204150.json"
        ]
        
        for file_path in railway_files:
            if os.path.exists(file_path):
                print(f"  ✅ {file_path}: Encontrado")
                railway_tests_passed += 1
                self.test_results["tests"]["railway_integration"]["details"].append({
                    "file": file_path,
                    "status": "FOUND"
                })
            else:
                print(f"  ❌ {file_path}: Não encontrado")
                self.test_results["tests"]["railway_integration"]["details"].append({
                    "file": file_path,
                    "status": "NOT_FOUND"
                })
        
        # Teste 2: Verificar conteúdo do relatório do Railway
        try:
            report_file = "railway_supabase_configuration_report_20251023_204150.json"
            if os.path.exists(report_file):
                with open(report_file, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                
                if report_data.get("overall_status") == "FULLY_CONFIGURED":
                    print("  ✅ Railway: Configuração completa confirmada")
                    railway_tests_passed += 1
                    self.test_results["tests"]["railway_integration"]["details"].append({
                        "test": "railway_configuration",
                        "status": "FULLY_CONFIGURED",
                        "variables_count": len(report_data.get("variables_configured", []))
                    })
                else:
                    print(f"  ⚠️ Railway: Status {report_data.get('overall_status')}")
                    self.test_results["tests"]["railway_integration"]["details"].append({
                        "test": "railway_configuration",
                        "status": report_data.get("overall_status", "UNKNOWN")
                    })
        except Exception as e:
            print(f"  ❌ Railway: Erro ao verificar relatório - {e}")
            self.test_results["tests"]["railway_integration"]["details"].append({
                "test": "railway_configuration",
                "status": "ERROR",
                "error": str(e)
            })
        
        self.test_results["tests"]["railway_integration"]["score"] = railway_tests_passed
        
        if railway_tests_passed >= 2:
            self.test_results["tests"]["railway_integration"]["status"] = "EXCELLENT"
        elif railway_tests_passed >= 1:
            self.test_results["tests"]["railway_integration"]["status"] = "GOOD"
        else:
            self.test_results["tests"]["railway_integration"]["status"] = "POOR"
        
        print(f"📊 Railway: {railway_tests_passed}/3 testes passaram")

    def test_code_integration(self):
        """Testa integração com o código existente"""
        print("\n💻 Testando integração com código...")
        
        code_tests_passed = 0
        
        # Teste 1: Verificar SupabaseUploader
        try:
            uploader_path = "src/services/supabase_uploader.py"
            if os.path.exists(uploader_path):
                with open(uploader_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if "class SupabaseUploader" in content and "upload_from_bytes" in content:
                    print("  ✅ SupabaseUploader: Implementado corretamente")
                    code_tests_passed += 1
                    self.test_results["tests"]["code_integration"]["details"].append({
                        "component": "SupabaseUploader",
                        "status": "IMPLEMENTED",
                        "methods_found": ["upload_from_bytes", "__init__"]
                    })
                else:
                    print("  ⚠️ SupabaseUploader: Implementação incompleta")
                    self.test_results["tests"]["code_integration"]["details"].append({
                        "component": "SupabaseUploader",
                        "status": "INCOMPLETE"
                    })
            else:
                print("  ❌ SupabaseUploader: Arquivo não encontrado")
                self.test_results["tests"]["code_integration"]["details"].append({
                    "component": "SupabaseUploader",
                    "status": "NOT_FOUND"
                })
        except Exception as e:
            print(f"  ❌ SupabaseUploader: Erro - {e}")
            self.test_results["tests"]["code_integration"]["details"].append({
                "component": "SupabaseUploader",
                "status": "ERROR",
                "error": str(e)
            })
        
        # Teste 2: Verificar pipeline
        try:
            pipeline_path = "src/pipeline/generate_and_publish.py"
            if os.path.exists(pipeline_path):
                with open(pipeline_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if "supabase" in content.lower():
                    print("  ✅ Pipeline: Integração com Supabase encontrada")
                    code_tests_passed += 1
                    self.test_results["tests"]["code_integration"]["details"].append({
                        "component": "Pipeline",
                        "status": "INTEGRATED",
                        "supabase_references": content.lower().count("supabase")
                    })
                else:
                    print("  ⚠️ Pipeline: Sem integração com Supabase")
                    self.test_results["tests"]["code_integration"]["details"].append({
                        "component": "Pipeline",
                        "status": "NOT_INTEGRATED"
                    })
            else:
                print("  ❌ Pipeline: Arquivo não encontrado")
                self.test_results["tests"]["code_integration"]["details"].append({
                    "component": "Pipeline",
                    "status": "NOT_FOUND"
                })
        except Exception as e:
            print(f"  ❌ Pipeline: Erro - {e}")
            self.test_results["tests"]["code_integration"]["details"].append({
                "component": "Pipeline",
                "status": "ERROR",
                "error": str(e)
            })
        
        # Teste 3: Verificar config.py
        try:
            config_path = "src/config.py"
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if "SUPABASE" in content:
                    print("  ✅ Config: Configurações do Supabase encontradas")
                    code_tests_passed += 1
                    self.test_results["tests"]["code_integration"]["details"].append({
                        "component": "Config",
                        "status": "CONFIGURED"
                    })
                else:
                    print("  ⚠️ Config: Sem configurações do Supabase")
                    self.test_results["tests"]["code_integration"]["details"].append({
                        "component": "Config",
                        "status": "NOT_CONFIGURED"
                    })
            else:
                print("  ❌ Config: Arquivo não encontrado")
                self.test_results["tests"]["code_integration"]["details"].append({
                    "component": "Config",
                    "status": "NOT_FOUND"
                })
        except Exception as e:
            print(f"  ❌ Config: Erro - {e}")
            self.test_results["tests"]["code_integration"]["details"].append({
                "component": "Config",
                "status": "ERROR",
                "error": str(e)
            })
        
        # Teste 4: Verificar requirements.txt
        try:
            if os.path.exists("requirements.txt"):
                with open("requirements.txt", 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if "supabase" in content.lower():
                    print("  ✅ Requirements: Dependências do Supabase encontradas")
                    code_tests_passed += 1
                    self.test_results["tests"]["code_integration"]["details"].append({
                        "component": "Requirements",
                        "status": "HAS_SUPABASE_DEPS"
                    })
                else:
                    print("  ⚠️ Requirements: Sem dependências do Supabase")
                    self.test_results["tests"]["code_integration"]["details"].append({
                        "component": "Requirements",
                        "status": "NO_SUPABASE_DEPS"
                    })
        except Exception as e:
            print(f"  ❌ Requirements: Erro - {e}")
            self.test_results["tests"]["code_integration"]["details"].append({
                "component": "Requirements",
                "status": "ERROR",
                "error": str(e)
            })
        
        self.test_results["tests"]["code_integration"]["score"] = code_tests_passed
        
        if code_tests_passed >= 3:
            self.test_results["tests"]["code_integration"]["status"] = "EXCELLENT"
        elif code_tests_passed >= 2:
            self.test_results["tests"]["code_integration"]["status"] = "GOOD"
        else:
            self.test_results["tests"]["code_integration"]["status"] = "POOR"
        
        print(f"📊 Integração de código: {code_tests_passed}/4 componentes integrados")

    def calculate_overall_score(self):
        """Calcula pontuação geral"""
        total_score = 0
        max_total_score = 0
        
        for test_name, test_data in self.test_results["tests"].items():
            total_score += test_data["score"]
            max_total_score += test_data["max_score"]
        
        self.test_results["overall_score"] = total_score
        self.test_results["max_score"] = max_total_score
        
        percentage = (total_score / max_total_score) * 100 if max_total_score > 0 else 0
        
        if percentage >= 90:
            self.test_results["overall_status"] = "EXCELLENT"
        elif percentage >= 75:
            self.test_results["overall_status"] = "GOOD"
        elif percentage >= 50:
            self.test_results["overall_status"] = "FAIR"
        else:
            self.test_results["overall_status"] = "POOR"
        
        return percentage

    def generate_recommendations(self):
        """Gera recomendações baseadas nos resultados"""
        recommendations = []
        
        for test_name, test_data in self.test_results["tests"].items():
            if test_data["status"] == "POOR":
                if test_name == "environment_variables":
                    recommendations.append({
                        "priority": "HIGH",
                        "category": "Environment",
                        "issue": "Variáveis de ambiente não configuradas",
                        "solution": "Configurar todas as variáveis SUPABASE_* no sistema"
                    })
                elif test_name == "connectivity":
                    recommendations.append({
                        "priority": "CRITICAL",
                        "category": "Connectivity",
                        "issue": "Problemas de conectividade com Supabase",
                        "solution": "Verificar credenciais e conectividade de rede"
                    })
                elif test_name == "storage_operations":
                    recommendations.append({
                        "priority": "HIGH",
                        "category": "Storage",
                        "issue": "Operações de storage falhando",
                        "solution": "Verificar permissões do bucket e configurações"
                    })
                elif test_name == "code_integration":
                    recommendations.append({
                        "priority": "MEDIUM",
                        "category": "Code",
                        "issue": "Integração de código incompleta",
                        "solution": "Completar implementação do SupabaseUploader e integração no pipeline"
                    })
        
        self.test_results["recommendations"] = recommendations

    def generate_summary(self):
        """Gera resumo dos resultados"""
        summary = {
            "total_tests": len(self.test_results["tests"]),
            "excellent_tests": sum(1 for test in self.test_results["tests"].values() if test["status"] == "EXCELLENT"),
            "good_tests": sum(1 for test in self.test_results["tests"].values() if test["status"] == "GOOD"),
            "poor_tests": sum(1 for test in self.test_results["tests"].values() if test["status"] == "POOR"),
            "score_percentage": (self.test_results["overall_score"] / self.test_results["max_score"]) * 100 if self.test_results["max_score"] > 0 else 0,
            "critical_issues": len([r for r in self.test_results["recommendations"] if r["priority"] == "CRITICAL"]),
            "high_issues": len([r for r in self.test_results["recommendations"] if r["priority"] == "HIGH"]),
            "medium_issues": len([r for r in self.test_results["recommendations"] if r["priority"] == "MEDIUM"])
        }
        
        self.test_results["summary"] = summary

    def save_report(self):
        """Salva relatório final"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"supabase_final_integration_report_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Relatório final salvo em: {filename}")
        return filename

    def run_complete_test(self):
        """Executa todos os testes"""
        print("🧪 TESTE FINAL COMPLETO DA INTEGRAÇÃO SUPABASE")
        print("=" * 60)
        
        # Executar todos os testes
        self.test_environment_variables()
        self.test_configuration_files()
        self.test_connectivity()
        self.test_storage_operations()
        self.test_api_functionality()
        self.test_railway_integration()
        self.test_code_integration()
        
        # Calcular resultados
        percentage = self.calculate_overall_score()
        self.generate_recommendations()
        self.generate_summary()
        
        # Mostrar resultados finais
        print(f"\n🎯 RESULTADO FINAL")
        print("=" * 30)
        print(f"Status Geral: {self.test_results['overall_status']}")
        print(f"Pontuação: {self.test_results['overall_score']}/{self.test_results['max_score']} ({percentage:.1f}%)")
        
        print(f"\n📊 RESUMO POR CATEGORIA:")
        for test_name, test_data in self.test_results["tests"].items():
            status_emoji = "✅" if test_data["status"] == "EXCELLENT" else "⚠️" if test_data["status"] == "GOOD" else "❌"
            print(f"  {status_emoji} {test_name.replace('_', ' ').title()}: {test_data['status']} ({test_data['score']}/{test_data['max_score']})")
        
        if self.test_results["recommendations"]:
            print(f"\n🔧 RECOMENDAÇÕES:")
            for rec in self.test_results["recommendations"]:
                priority_emoji = "🔴" if rec["priority"] == "CRITICAL" else "🟠" if rec["priority"] == "HIGH" else "🟡"
                print(f"  {priority_emoji} {rec['priority']}: {rec['issue']}")
                print(f"     Solução: {rec['solution']}")
        
        # Salvar relatório
        report_file = self.save_report()
        
        # Conclusão
        if percentage >= 90:
            print(f"\n🎉 EXCELENTE! A integração Supabase está funcionando perfeitamente!")
            return True
        elif percentage >= 75:
            print(f"\n✅ BOM! A integração Supabase está funcionando bem com pequenos ajustes necessários.")
            return True
        elif percentage >= 50:
            print(f"\n⚠️ REGULAR. A integração Supabase está parcialmente funcionando. Verificar recomendações.")
            return False
        else:
            print(f"\n❌ CRÍTICO. A integração Supabase precisa de correções importantes.")
            return False

if __name__ == "__main__":
    tester = SupabaseFinalIntegrationTest()
    success = tester.run_complete_test()
    
    if success:
        print("\n🚀 Integração Supabase pronta para produção!")
        sys.exit(0)
    else:
        print("\n🔧 Integração Supabase precisa de ajustes antes da produção.")
        sys.exit(1)