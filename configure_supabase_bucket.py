#!/usr/bin/env python3
"""
Script para verificar e configurar bucket de armazenamento Supabase
Configura políticas de segurança e permissões adequadas
"""

import os
import json
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime

class SupabaseBucketConfigurator:
    def __init__(self):
        # Carregar credenciais diretamente (fallback para variáveis de ambiente)
        self.credentials = {
            "url": os.environ.get("SUPABASE_URL", "https://ccvfdupucmsjxwtfwzkd.supabase.co"),
            "service_key": os.environ.get("SUPABASE_SERVICE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNjdmZkdXB1Y21zanh3dGZ3emtkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg3OTgwNywiZXhwIjoyMDc1NDU1ODA3fQ.HcQb9CpoF9sQcRUBQWmcmx6RmokXd64FbGpBV3GVUzM"),
            "anon_key": os.environ.get("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNjdmZkdXB1Y21zanh3dGZ3emtkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4Nzk4MDcsImV4cCI6MjA3NTQ1NTgwN30.2M9-ieZ-PMnO7NQ-aDHjxor4ytAHa0pKwH7j1gsrXjI"),
            "bucket": os.environ.get("SUPABASE_BUCKET", "instagram-images"),
            "project_ref": os.environ.get("SUPABASE_PROJECT_REF", "ccvfdupucmsjxwtfwzkd")
        }
        
        self.bucket_config = {
            "name": self.credentials["bucket"],
            "public": True,  # Para permitir acesso público às imagens
            "file_size_limit": 10485760,  # 10MB
            "allowed_mime_types": ["image/jpeg", "image/png", "image/webp", "image/gif"]
        }
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "bucket_status": {},
            "policies_status": {},
            "configuration_applied": {},
            "recommendations": []
        }
    
    def check_bucket_exists(self):
        """Verifica se o bucket existe"""
        print("🔍 Verificando existência do bucket...")
        
        try:
            url = f"{self.credentials['url']}/storage/v1/bucket"
            headers = {
                "apikey": self.credentials["service_key"],
                "Authorization": f"Bearer {self.credentials['service_key']}",
                "Content-Type": "application/json"
            }
            
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                buckets = json.loads(response.read().decode('utf-8'))
                
                bucket_names = [bucket.get("name", "") for bucket in buckets]
                
                if self.credentials["bucket"] in bucket_names:
                    bucket_info = next((b for b in buckets if b.get("name") == self.credentials["bucket"]), {})
                    self.results["bucket_status"]["exists"] = True
                    self.results["bucket_status"]["info"] = bucket_info
                    print(f"  ✅ Bucket '{self.credentials['bucket']}' encontrado")
                    print(f"    📊 Público: {bucket_info.get('public', 'N/A')}")
                    print(f"    📊 Criado em: {bucket_info.get('created_at', 'N/A')}")
                    return True
                else:
                    self.results["bucket_status"]["exists"] = False
                    print(f"  ❌ Bucket '{self.credentials['bucket']}' não encontrado")
                    print(f"    📋 Buckets disponíveis: {bucket_names}")
                    return False
        
        except Exception as e:
            self.results["bucket_status"]["error"] = str(e)
            print(f"  ❌ Erro ao verificar bucket: {e}")
            return False
    
    def create_bucket_if_needed(self):
        """Cria o bucket se não existir"""
        if self.results["bucket_status"].get("exists", False):
            print("  ℹ️ Bucket já existe, pulando criação")
            return True
        
        print(f"🏗️ Criando bucket '{self.credentials['bucket']}'...")
        
        try:
            url = f"{self.credentials['url']}/storage/v1/bucket"
            headers = {
                "apikey": self.credentials["service_key"],
                "Authorization": f"Bearer {self.credentials['service_key']}",
                "Content-Type": "application/json"
            }
            
            bucket_data = {
                "name": self.bucket_config["name"],
                "public": self.bucket_config["public"],
                "file_size_limit": self.bucket_config["file_size_limit"],
                "allowed_mime_types": self.bucket_config["allowed_mime_types"]
            }
            
            data = json.dumps(bucket_data).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers=headers, method='POST')
            
            with urllib.request.urlopen(req, timeout=15) as response:
                status_code = response.getcode()
                response_data = response.read().decode('utf-8')
                
                if status_code in [200, 201]:
                    self.results["bucket_status"]["created"] = True
                    print(f"  ✅ Bucket criado com sucesso")
                    print(f"    📄 Resposta: {response_data}")
                    return True
                else:
                    self.results["bucket_status"]["creation_error"] = f"HTTP_{status_code}"
                    print(f"  ❌ Falha na criação: HTTP {status_code}")
                    print(f"    📄 Resposta: {response_data}")
                    return False
        
        except urllib.error.HTTPError as e:
            error_response = e.read().decode('utf-8') if e.fp else "No response"
            self.results["bucket_status"]["creation_error"] = f"HTTP_{e.code}: {error_response}"
            print(f"  ❌ Erro HTTP {e.code}: {error_response}")
            return False
        
        except Exception as e:
            self.results["bucket_status"]["creation_error"] = str(e)
            print(f"  ❌ Erro na criação: {e}")
            return False
    
    def check_bucket_policies(self):
        """Verifica políticas RLS do bucket"""
        print("🔒 Verificando políticas de segurança...")
        
        try:
            # Verificar políticas existentes
            url = f"{self.credentials['url']}/rest/v1/rpc/get_bucket_policies"
            headers = {
                "apikey": self.credentials["service_key"],
                "Authorization": f"Bearer {self.credentials['service_key']}",
                "Content-Type": "application/json"
            }
            
            # Como não temos acesso direto às políticas via API REST,
            # vamos testar as operações básicas
            self.test_bucket_operations()
            
        except Exception as e:
            print(f"  ⚠️ Não foi possível verificar políticas: {e}")
            self.results["policies_status"]["check_error"] = str(e)
    
    def test_bucket_operations(self):
        """Testa operações básicas do bucket"""
        print("🧪 Testando operações do bucket...")
        
        # Teste 1: Listar arquivos
        try:
            url = f"{self.credentials['url']}/storage/v1/object/list/{self.credentials['bucket']}"
            headers = {
                "apikey": self.credentials["service_key"],
                "Authorization": f"Bearer {self.credentials['service_key']}",
                "Content-Type": "application/json"
            }
            
            data = json.dumps({"limit": 10, "offset": 0}).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers=headers, method='POST')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                status_code = response.getcode()
                if status_code == 200:
                    files = json.loads(response.read().decode('utf-8'))
                    self.results["policies_status"]["list_files"] = "SUCCESS"
                    print(f"  ✅ Listagem de arquivos: Funcionando ({len(files)} arquivos)")
                else:
                    self.results["policies_status"]["list_files"] = f"HTTP_{status_code}"
                    print(f"  ⚠️ Listagem de arquivos: HTTP {status_code}")
        
        except Exception as e:
            self.results["policies_status"]["list_files"] = f"ERROR: {str(e)}"
            print(f"  ❌ Listagem de arquivos: {e}")
        
        # Teste 2: Upload de arquivo
        self.test_file_upload_permissions()
        
        # Teste 3: Acesso público
        self.test_public_access()
    
    def test_file_upload_permissions(self):
        """Testa permissões de upload"""
        print("📤 Testando permissões de upload...")
        
        try:
            test_content = f"Test upload permissions - {datetime.now().isoformat()}"
            test_filename = f"test_permissions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
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
                
                if status_code in [200, 201]:
                    self.results["policies_status"]["upload_permission"] = "SUCCESS"
                    print(f"  ✅ Upload com service_key: Funcionando")
                    
                    # Testar upload com anon_key
                    self.test_anonymous_upload(test_filename + "_anon")
                else:
                    self.results["policies_status"]["upload_permission"] = f"HTTP_{status_code}"
                    print(f"  ⚠️ Upload com service_key: HTTP {status_code}")
        
        except Exception as e:
            self.results["policies_status"]["upload_permission"] = f"ERROR: {str(e)}"
            print(f"  ❌ Upload com service_key: {e}")
    
    def test_anonymous_upload(self, filename):
        """Testa upload com chave anônima"""
        try:
            test_content = "Test anonymous upload"
            
            url = f"{self.credentials['url']}/storage/v1/object/{self.credentials['bucket']}/{filename}"
            headers = {
                "apikey": self.credentials["anon_key"],
                "Authorization": f"Bearer {self.credentials['anon_key']}",
                "Content-Type": "text/plain"
            }
            
            data = test_content.encode('utf-8')
            req = urllib.request.Request(url, data=data, headers=headers, method='POST')
            
            with urllib.request.urlopen(req, timeout=15) as response:
                status_code = response.getcode()
                
                if status_code in [200, 201]:
                    self.results["policies_status"]["anonymous_upload"] = "SUCCESS"
                    print(f"  ✅ Upload anônimo: Permitido")
                else:
                    self.results["policies_status"]["anonymous_upload"] = f"HTTP_{status_code}"
                    print(f"  ⚠️ Upload anônimo: HTTP {status_code}")
        
        except urllib.error.HTTPError as e:
            if e.code == 403:
                self.results["policies_status"]["anonymous_upload"] = "FORBIDDEN"
                print(f"  🔒 Upload anônimo: Bloqueado (segurança adequada)")
            else:
                self.results["policies_status"]["anonymous_upload"] = f"HTTP_{e.code}"
                print(f"  ⚠️ Upload anônimo: HTTP {e.code}")
        
        except Exception as e:
            self.results["policies_status"]["anonymous_upload"] = f"ERROR: {str(e)}"
            print(f"  ❌ Upload anônimo: {e}")
    
    def test_public_access(self):
        """Testa acesso público aos arquivos"""
        print("🌐 Testando acesso público...")
        
        # Primeiro, fazer upload de um arquivo de teste
        test_filename = f"public_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        test_content = "Public access test file"
        
        try:
            # Upload do arquivo
            upload_url = f"{self.credentials['url']}/storage/v1/object/{self.credentials['bucket']}/{test_filename}"
            headers = {
                "apikey": self.credentials["service_key"],
                "Authorization": f"Bearer {self.credentials['service_key']}",
                "Content-Type": "text/plain"
            }
            
            data = test_content.encode('utf-8')
            req = urllib.request.Request(upload_url, data=data, headers=headers, method='POST')
            
            with urllib.request.urlopen(req, timeout=15) as response:
                if response.getcode() in [200, 201]:
                    # Testar acesso público
                    public_url = f"{self.credentials['url']}/storage/v1/object/public/{self.credentials['bucket']}/{test_filename}"
                    
                    public_req = urllib.request.Request(public_url)
                    with urllib.request.urlopen(public_req, timeout=10) as public_response:
                        if public_response.getcode() == 200:
                            content = public_response.read().decode('utf-8')
                            if content == test_content:
                                self.results["policies_status"]["public_access"] = "SUCCESS"
                                print(f"  ✅ Acesso público: Funcionando")
                                print(f"    🔗 URL pública: {public_url}")
                            else:
                                self.results["policies_status"]["public_access"] = "CONTENT_MISMATCH"
                                print(f"  ⚠️ Acesso público: Conteúdo não confere")
                        else:
                            self.results["policies_status"]["public_access"] = f"HTTP_{public_response.getcode()}"
                            print(f"  ⚠️ Acesso público: HTTP {public_response.getcode()}")
        
        except Exception as e:
            self.results["policies_status"]["public_access"] = f"ERROR: {str(e)}"
            print(f"  ❌ Acesso público: {e}")
    
    def generate_bucket_recommendations(self):
        """Gera recomendações para configuração do bucket"""
        recommendations = []
        
        # Verificar se bucket existe
        if not self.results["bucket_status"].get("exists", False):
            recommendations.append({
                "priority": "CRITICAL",
                "category": "Bucket",
                "issue": f"Bucket '{self.credentials['bucket']}' não existe",
                "action": "Criar bucket com configurações adequadas"
            })
        
        # Verificar políticas de upload
        if self.results["policies_status"].get("upload_permission") != "SUCCESS":
            recommendations.append({
                "priority": "HIGH",
                "category": "Permissões",
                "issue": "Upload com service_key falhando",
                "action": "Verificar políticas RLS e permissões do bucket"
            })
        
        # Verificar acesso público
        if self.results["policies_status"].get("public_access") != "SUCCESS":
            recommendations.append({
                "priority": "MEDIUM",
                "category": "Acesso Público",
                "issue": "Acesso público não funcionando",
                "action": "Configurar bucket como público e verificar políticas"
            })
        
        # Verificar segurança de upload anônimo
        if self.results["policies_status"].get("anonymous_upload") == "SUCCESS":
            recommendations.append({
                "priority": "HIGH",
                "category": "Segurança",
                "issue": "Upload anônimo permitido",
                "action": "Implementar políticas RLS para restringir uploads"
            })
        
        # Recomendações de sucesso
        if not recommendations:
            recommendations.append({
                "priority": "INFO",
                "category": "Status",
                "issue": "Bucket configurado corretamente",
                "action": "Configuração adequada para uso em produção"
            })
        
        self.results["recommendations"] = recommendations
        return recommendations
    
    def save_bucket_report(self):
        """Salva relatório de configuração do bucket"""
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"supabase_bucket_config_{timestamp_str}.json"
        
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        return report_file
    
    def run_bucket_configuration(self):
        """Executa configuração completa do bucket"""
        print("=" * 70)
        print("🪣 CONFIGURAÇÃO DO BUCKET SUPABASE")
        print("=" * 70)
        
        # 1. Verificar se bucket existe
        bucket_exists = self.check_bucket_exists()
        
        # 2. Criar bucket se necessário
        if not bucket_exists:
            self.create_bucket_if_needed()
        
        # 3. Verificar políticas
        self.check_bucket_policies()
        
        # 4. Gerar recomendações
        recommendations = self.generate_bucket_recommendations()
        
        # 5. Salvar relatório
        report_file = self.save_bucket_report()
        
        # Exibir resumo
        print("\n" + "=" * 70)
        print("📊 RESUMO DA CONFIGURAÇÃO")
        print("=" * 70)
        
        bucket_status = "✅ CONFIGURADO" if self.results["bucket_status"].get("exists", False) else "❌ NÃO CONFIGURADO"
        print(f"🪣 Status do Bucket: {bucket_status}")
        
        policies_ok = sum(1 for v in self.results["policies_status"].values() if v == "SUCCESS")
        policies_total = len(self.results["policies_status"])
        print(f"🔒 Políticas: {policies_ok}/{policies_total} funcionando")
        
        print(f"📄 Relatório: {report_file}")
        
        if recommendations:
            print("\n💡 RECOMENDAÇÕES:")
            for rec in recommendations[:3]:
                priority_emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "INFO": "ℹ️"}.get(rec['priority'], "⚪")
                print(f"  {priority_emoji} [{rec['priority']}] {rec['issue']}")
                print(f"    💡 {rec['action']}")
        
        print("=" * 70)
        
        return self.results

if __name__ == "__main__":
    configurator = SupabaseBucketConfigurator()
    results = configurator.run_bucket_configuration()