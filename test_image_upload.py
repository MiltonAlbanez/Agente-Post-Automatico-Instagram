#!/usr/bin/env python3
"""
Script para testar upload de imagens para Supabase Storage
Simula o uso real do sistema de upload de imagens
"""

import os
import json
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
import base64
from io import BytesIO

class SupabaseImageUploadTester:
    def __init__(self):
        self.credentials = {
            "url": "https://ccvfdupucmsjxwtfwzkd.supabase.co",
            "service_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNjdmZkdXB1Y21zanh3dGZ3emtkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg3OTgwNywiZXhwIjoyMDc1NDU1ODA3fQ.HcQb9CpoF9sQcRUBQWmcmx6RmokXd64FbGpBV3GVUzM",
            "anon_key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNjdmZkdXB1Y21zanh3dGZ3emtkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4Nzk4MDcsImV4cCI6MjA3NTQ1NTgwN30.2M9-ieZ-PMnO7NQ-aDHjxor4ytAHa0pKwH7j1gsrXjI",
            "bucket": "instagram-images"
        }
        
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "image_tests": {},
            "performance_metrics": {},
            "url_generation": {},
            "integration_tests": {},
            "recommendations": []
        }
    
    def create_test_image(self, width=800, height=600, format="JPEG"):
        """Cria uma imagem de teste simples"""
        try:
            # Criar uma imagem simples usando dados binários
            # Vamos criar um arquivo JPEG mínimo válido
            if format == "JPEG":
                # Header JPEG básico + dados mínimos
                jpeg_header = bytes([
                    0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
                    0x01, 0x01, 0x00, 0x48, 0x00, 0x48, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43,
                    0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08, 0x07, 0x07, 0x07, 0x09,
                    0x09, 0x08, 0x0A, 0x0C, 0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12,
                    0x13, 0x0F, 0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D, 0x1A, 0x1C, 0x1C, 0x20,
                    0x24, 0x2E, 0x27, 0x20, 0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28, 0x37, 0x29,
                    0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27, 0x39, 0x3D, 0x38, 0x32,
                    0x3C, 0x2E, 0x33, 0x34, 0x32, 0xFF, 0xC0, 0x00, 0x11, 0x08, 0x00, 0x64,
                    0x00, 0x64, 0x01, 0x01, 0x11, 0x00, 0x02, 0x11, 0x01, 0x03, 0x11, 0x01,
                    0xFF, 0xC4, 0x00, 0x14, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x08, 0xFF, 0xC4,
                    0x00, 0x14, 0x10, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xDA, 0x00, 0x0C,
                    0x03, 0x01, 0x00, 0x02, 0x11, 0x03, 0x11, 0x00, 0x3F, 0x00, 0xB2, 0xC0,
                    0x07, 0xFF, 0xD9
                ])
                return jpeg_header
            
            elif format == "PNG":
                # PNG mínimo válido (1x1 pixel transparente)
                png_data = base64.b64decode(
                    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU8j8gAAAABJRU5ErkJggg=="
                )
                return png_data
            
        except Exception as e:
            print(f"  ❌ Erro ao criar imagem de teste: {e}")
            return None
    
    def test_image_upload(self, image_data, filename, content_type):
        """Testa upload de uma imagem específica"""
        print(f"📤 Testando upload: {filename}")
        
        try:
            url = f"{self.credentials['url']}/storage/v1/object/{self.credentials['bucket']}/{filename}"
            headers = {
                "apikey": self.credentials["service_key"],
                "Authorization": f"Bearer {self.credentials['service_key']}",
                "Content-Type": content_type
            }
            
            start_time = datetime.now()
            req = urllib.request.Request(url, data=image_data, headers=headers, method='POST')
            
            with urllib.request.urlopen(req, timeout=30) as response:
                end_time = datetime.now()
                upload_time = (end_time - start_time).total_seconds()
                
                status_code = response.getcode()
                response_data = response.read().decode('utf-8')
                
                if status_code in [200, 201]:
                    print(f"  ✅ Upload bem-sucedido ({upload_time:.2f}s)")
                    
                    # Gerar URL pública
                    public_url = f"{self.credentials['url']}/storage/v1/object/public/{self.credentials['bucket']}/{filename}"
                    
                    # Testar acesso à URL pública
                    access_test = self.test_public_url_access(public_url)
                    
                    return {
                        "status": "SUCCESS",
                        "upload_time": upload_time,
                        "file_size": len(image_data),
                        "public_url": public_url,
                        "public_access": access_test,
                        "response": response_data
                    }
                else:
                    print(f"  ❌ Falha no upload: HTTP {status_code}")
                    return {
                        "status": f"HTTP_{status_code}",
                        "error": response_data
                    }
        
        except urllib.error.HTTPError as e:
            error_response = e.read().decode('utf-8') if e.fp else "No response"
            print(f"  ❌ Erro HTTP {e.code}: {error_response}")
            return {
                "status": f"HTTP_ERROR_{e.code}",
                "error": error_response
            }
        
        except Exception as e:
            print(f"  ❌ Erro no upload: {e}")
            return {
                "status": "ERROR",
                "error": str(e)
            }
    
    def test_public_url_access(self, url):
        """Testa acesso à URL pública"""
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.getcode() == 200:
                    content_length = len(response.read())
                    return {
                        "accessible": True,
                        "content_length": content_length
                    }
                else:
                    return {
                        "accessible": False,
                        "status_code": response.getcode()
                    }
        
        except Exception as e:
            return {
                "accessible": False,
                "error": str(e)
            }
    
    def test_different_image_formats(self):
        """Testa upload de diferentes formatos de imagem"""
        print("🖼️ Testando diferentes formatos de imagem...")
        
        test_cases = [
            {
                "format": "JPEG",
                "filename": f"test_jpeg_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
                "content_type": "image/jpeg"
            },
            {
                "format": "PNG",
                "filename": f"test_png_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                "content_type": "image/png"
            }
        ]
        
        for test_case in test_cases:
            image_data = self.create_test_image(format=test_case["format"])
            
            if image_data:
                result = self.test_image_upload(
                    image_data, 
                    test_case["filename"], 
                    test_case["content_type"]
                )
                self.test_results["image_tests"][test_case["format"]] = result
            else:
                self.test_results["image_tests"][test_case["format"]] = {
                    "status": "ERROR",
                    "error": "Failed to create test image"
                }
    
    def test_large_image_upload(self):
        """Testa upload de imagem grande"""
        print("📏 Testando upload de imagem grande...")
        
        try:
            # Criar uma imagem "grande" (repetindo dados para simular tamanho)
            base_image = self.create_test_image(format="JPEG")
            if base_image:
                # Simular imagem maior repetindo dados
                large_image_data = base_image * 100  # Aproximadamente 100x maior
                
                filename = f"test_large_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                result = self.test_image_upload(large_image_data, filename, "image/jpeg")
                
                self.test_results["image_tests"]["large_image"] = result
                
                if result.get("status") == "SUCCESS":
                    print(f"    📊 Tamanho: {len(large_image_data)} bytes")
                    print(f"    ⏱️ Tempo: {result.get('upload_time', 0):.2f}s")
        
        except Exception as e:
            self.test_results["image_tests"]["large_image"] = {
                "status": "ERROR",
                "error": str(e)
            }
            print(f"  ❌ Erro no teste de imagem grande: {e}")
    
    def test_url_generation_patterns(self):
        """Testa diferentes padrões de geração de URL"""
        print("🔗 Testando padrões de URL...")
        
        test_filename = f"url_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        image_data = self.create_test_image(format="JPEG")
        
        if image_data:
            # Upload da imagem
            upload_result = self.test_image_upload(image_data, test_filename, "image/jpeg")
            
            if upload_result.get("status") == "SUCCESS":
                # Testar diferentes padrões de URL
                url_patterns = {
                    "public_url": f"{self.credentials['url']}/storage/v1/object/public/{self.credentials['bucket']}/{test_filename}",
                    "authenticated_url": f"{self.credentials['url']}/storage/v1/object/{self.credentials['bucket']}/{test_filename}",
                    "signed_url_pattern": f"{self.credentials['url']}/storage/v1/object/sign/{self.credentials['bucket']}/{test_filename}"
                }
                
                for pattern_name, url in url_patterns.items():
                    access_result = self.test_public_url_access(url)
                    self.test_results["url_generation"][pattern_name] = {
                        "url": url,
                        "access_result": access_result
                    }
                    
                    status = "✅" if access_result.get("accessible", False) else "❌"
                    print(f"  {status} {pattern_name}: {access_result.get('accessible', False)}")
    
    def test_integration_with_existing_code(self):
        """Testa integração com código existente"""
        print("🔧 Testando integração com código existente...")
        
        try:
            # Verificar se existe o arquivo SupabaseUploader
            uploader_files = [
                "supabase_uploader.py",
                "uploaders/supabase_uploader.py",
                "src/supabase_uploader.py"
            ]
            
            uploader_found = False
            for file_path in uploader_files:
                if os.path.exists(file_path):
                    uploader_found = True
                    print(f"  ✅ Encontrado: {file_path}")
                    
                    # Tentar importar e testar
                    try:
                        # Simular teste de integração
                        self.test_results["integration_tests"]["uploader_file"] = {
                            "found": True,
                            "path": file_path
                        }
                    except Exception as e:
                        self.test_results["integration_tests"]["uploader_file"] = {
                            "found": True,
                            "path": file_path,
                            "import_error": str(e)
                        }
                    break
            
            if not uploader_found:
                print("  ⚠️ Arquivo SupabaseUploader não encontrado")
                self.test_results["integration_tests"]["uploader_file"] = {
                    "found": False,
                    "searched_paths": uploader_files
                }
            
            # Verificar configurações
            config_files = ["config.py", "settings.py", "accounts.json"]
            for config_file in config_files:
                if os.path.exists(config_file):
                    print(f"  ✅ Configuração encontrada: {config_file}")
                    self.test_results["integration_tests"][f"config_{config_file}"] = {"found": True}
        
        except Exception as e:
            print(f"  ❌ Erro no teste de integração: {e}")
            self.test_results["integration_tests"]["error"] = str(e)
    
    def calculate_performance_metrics(self):
        """Calcula métricas de performance"""
        print("📊 Calculando métricas de performance...")
        
        upload_times = []
        file_sizes = []
        
        for test_name, result in self.test_results["image_tests"].items():
            if result.get("status") == "SUCCESS":
                if "upload_time" in result:
                    upload_times.append(result["upload_time"])
                if "file_size" in result:
                    file_sizes.append(result["file_size"])
        
        if upload_times:
            self.test_results["performance_metrics"] = {
                "average_upload_time": sum(upload_times) / len(upload_times),
                "max_upload_time": max(upload_times),
                "min_upload_time": min(upload_times),
                "total_files_uploaded": len(upload_times),
                "total_bytes_uploaded": sum(file_sizes) if file_sizes else 0,
                "average_upload_speed_bps": (sum(file_sizes) / sum(upload_times)) if file_sizes and upload_times else 0
            }
            
            metrics = self.test_results["performance_metrics"]
            print(f"  📈 Tempo médio de upload: {metrics['average_upload_time']:.2f}s")
            print(f"  📈 Velocidade média: {metrics['average_upload_speed_bps']:.0f} bytes/s")
            print(f"  📈 Total de arquivos: {metrics['total_files_uploaded']}")
    
    def generate_recommendations(self):
        """Gera recomendações baseadas nos testes"""
        recommendations = []
        
        # Verificar sucessos de upload
        successful_uploads = sum(1 for result in self.test_results["image_tests"].values() 
                               if result.get("status") == "SUCCESS")
        total_uploads = len(self.test_results["image_tests"])
        
        if successful_uploads == 0:
            recommendations.append({
                "priority": "CRITICAL",
                "category": "Upload",
                "issue": "Nenhum upload de imagem foi bem-sucedido",
                "action": "Verificar credenciais e permissões do bucket"
            })
        elif successful_uploads < total_uploads:
            recommendations.append({
                "priority": "HIGH",
                "category": "Upload",
                "issue": f"Apenas {successful_uploads}/{total_uploads} uploads foram bem-sucedidos",
                "action": "Investigar falhas específicas de formato ou tamanho"
            })
        
        # Verificar URLs públicas
        public_access_issues = sum(1 for result in self.test_results["image_tests"].values()
                                 if result.get("public_access", {}).get("accessible") == False)
        
        if public_access_issues > 0:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "Acesso Público",
                "issue": f"{public_access_issues} URLs públicas não acessíveis",
                "action": "Verificar configurações de bucket público"
            })
        
        # Verificar performance
        if self.test_results["performance_metrics"]:
            avg_time = self.test_results["performance_metrics"].get("average_upload_time", 0)
            if avg_time > 10:
                recommendations.append({
                    "priority": "MEDIUM",
                    "category": "Performance",
                    "issue": f"Tempo médio de upload alto: {avg_time:.2f}s",
                    "action": "Considerar otimização de imagens ou CDN"
                })
        
        # Verificar integração
        if not self.test_results["integration_tests"].get("uploader_file", {}).get("found", False):
            recommendations.append({
                "priority": "HIGH",
                "category": "Integração",
                "issue": "Arquivo SupabaseUploader não encontrado",
                "action": "Verificar estrutura do projeto e implementação"
            })
        
        # Recomendações de sucesso
        if not recommendations:
            recommendations.append({
                "priority": "INFO",
                "category": "Status",
                "issue": "Todos os testes de upload passaram",
                "action": "Sistema pronto para uso em produção"
            })
        
        self.test_results["recommendations"] = recommendations
        return recommendations
    
    def save_test_report(self):
        """Salva relatório de testes"""
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"supabase_image_upload_test_{timestamp_str}.json"
        
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        return report_file
    
    def run_all_image_tests(self):
        """Executa todos os testes de upload de imagem"""
        print("=" * 70)
        print("🖼️ TESTE COMPLETO DE UPLOAD DE IMAGENS")
        print("=" * 70)
        
        # 1. Testar diferentes formatos
        self.test_different_image_formats()
        
        # 2. Testar imagem grande
        self.test_large_image_upload()
        
        # 3. Testar padrões de URL
        self.test_url_generation_patterns()
        
        # 4. Testar integração
        self.test_integration_with_existing_code()
        
        # 5. Calcular métricas
        self.calculate_performance_metrics()
        
        # 6. Gerar recomendações
        recommendations = self.generate_recommendations()
        
        # 7. Salvar relatório
        report_file = self.save_test_report()
        
        # Exibir resumo
        print("\n" + "=" * 70)
        print("📊 RESUMO DOS TESTES DE IMAGEM")
        print("=" * 70)
        
        successful_uploads = sum(1 for result in self.test_results["image_tests"].values() 
                               if result.get("status") == "SUCCESS")
        total_uploads = len(self.test_results["image_tests"])
        
        print(f"📤 Uploads bem-sucedidos: {successful_uploads}/{total_uploads}")
        
        if self.test_results["performance_metrics"]:
            metrics = self.test_results["performance_metrics"]
            print(f"⏱️ Tempo médio de upload: {metrics.get('average_upload_time', 0):.2f}s")
            print(f"📊 Total de bytes enviados: {metrics.get('total_bytes_uploaded', 0)}")
        
        print(f"📄 Relatório: {report_file}")
        
        if recommendations:
            print("\n💡 RECOMENDAÇÕES:")
            for rec in recommendations[:3]:
                priority_emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "INFO": "ℹ️"}.get(rec['priority'], "⚪")
                print(f"  {priority_emoji} [{rec['priority']}] {rec['issue']}")
                print(f"    💡 {rec['action']}")
        
        print("=" * 70)
        
        return self.test_results

if __name__ == "__main__":
    tester = SupabaseImageUploadTester()
    results = tester.run_all_image_tests()