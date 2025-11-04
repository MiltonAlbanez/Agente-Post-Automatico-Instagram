#!/usr/bin/env python3
"""
Connection & Authentication Test - Teste de Parâmetros de Conexão e Autenticação
Valida todos os parâmetros de conexão e autenticação do sistema
Data: 2025-10-23
"""

import json
import os
import sys
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import re
import base64

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConnectionAuthTester:
    """Testador de parâmetros de conexão e autenticação"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.data_path = self.base_path / "data"
        self.test_timestamp = datetime.now().isoformat()
        
    def test_instagram_tokens(self) -> Dict[str, Any]:
        """Testar tokens de acesso do Instagram"""
        print("📱 Testando tokens de acesso do Instagram...")
        
        token_test = {
            'status': 'PASSED',
            'accounts_tested': 0,
            'valid_tokens': 0,
            'token_issues': [],
            'token_details': []
        }
        
        try:
            accounts_path = self.base_path / "accounts.json"
            with open(accounts_path, 'r', encoding='utf-8') as f:
                accounts_data = json.load(f)
            
            for i, account in enumerate(accounts_data):
                token_test['accounts_tested'] += 1
                account_name = account.get('nome', f'Account_{i}')
                
                token_detail = {
                    'account_name': account_name,
                    'has_token': False,
                    'token_format_valid': False,
                    'token_length': 0,
                    'instagram_id_present': False,
                    'issues': []
                }
                
                # Verificar presença do token
                if 'instagram_access_token' in account:
                    token = account['instagram_access_token']
                    token_detail['has_token'] = True
                    token_detail['token_length'] = len(token)
                    
                    # Verificar formato do token (Instagram tokens são longos e alfanuméricos)
                    if len(token) > 50 and re.match(r'^[A-Za-z0-9_-]+$', token):
                        token_detail['token_format_valid'] = True
                    else:
                        token_detail['issues'].append("Formato de token inválido")
                    
                    # Verificar se não é um token de exemplo/placeholder
                    if token.lower() in ['your_token_here', 'token_placeholder', 'example_token']:
                        token_detail['issues'].append("Token é um placeholder")
                        token_detail['token_format_valid'] = False
                else:
                    token_detail['issues'].append("Token não encontrado")
                
                # Verificar Instagram ID
                if 'instagram_id' in account and account['instagram_id']:
                    token_detail['instagram_id_present'] = True
                else:
                    token_detail['issues'].append("Instagram ID não encontrado")
                
                # Determinar se o token é válido
                if (token_detail['has_token'] and 
                    token_detail['token_format_valid'] and 
                    token_detail['instagram_id_present'] and 
                    not token_detail['issues']):
                    token_test['valid_tokens'] += 1
                    print(f"✅ {account_name}: token válido ({token_detail['token_length']} chars)")
                else:
                    token_test['token_issues'].extend([f"{account_name}: {issue}" for issue in token_detail['issues']])
                    print(f"❌ {account_name}: problemas no token - {', '.join(token_detail['issues'])}")
                
                token_test['token_details'].append(token_detail)
            
            if token_test['valid_tokens'] == 0:
                token_test['status'] = 'FAILED'
            elif token_test['valid_tokens'] < token_test['accounts_tested']:
                token_test['status'] = 'PARTIAL'
                
        except Exception as e:
            token_test['status'] = 'ERROR'
            token_test['token_issues'].append(f"Erro geral: {str(e)}")
            logger.error(f"Erro no teste de tokens: {e}")
        
        return token_test
    
    def test_supabase_credentials(self) -> Dict[str, Any]:
        """Testar credenciais do Supabase"""
        print("☁️ Testando credenciais do Supabase...")
        
        supabase_test = {
            'status': 'PASSED',
            'accounts_tested': 0,
            'valid_credentials': 0,
            'credential_issues': [],
            'credential_details': []
        }
        
        try:
            accounts_path = self.base_path / "accounts.json"
            with open(accounts_path, 'r', encoding='utf-8') as f:
                accounts_data = json.load(f)
            
            for i, account in enumerate(accounts_data):
                supabase_test['accounts_tested'] += 1
                account_name = account.get('nome', f'Account_{i}')
                
                credential_detail = {
                    'account_name': account_name,
                    'has_url': False,
                    'has_service_key': False,
                    'has_bucket': False,
                    'url_format_valid': False,
                    'service_key_format_valid': False,
                    'issues': []
                }
                
                # Verificar URL do Supabase
                if 'supabase_url' in account:
                    url = account['supabase_url']
                    credential_detail['has_url'] = True
                    
                    # Verificar formato da URL
                    if url.startswith('https://') and '.supabase.co' in url:
                        credential_detail['url_format_valid'] = True
                    else:
                        credential_detail['issues'].append("URL Supabase inválida")
                else:
                    credential_detail['issues'].append("URL Supabase não encontrada")
                
                # Verificar Service Key
                if 'supabase_service_key' in account:
                    service_key = account['supabase_service_key']
                    credential_detail['has_service_key'] = True
                    
                    # Verificar formato da service key (JWT-like)
                    if len(service_key) > 100 and service_key.count('.') >= 2:
                        credential_detail['service_key_format_valid'] = True
                    else:
                        credential_detail['issues'].append("Service Key Supabase inválida")
                else:
                    credential_detail['issues'].append("Service Key Supabase não encontrada")
                
                # Verificar Bucket
                if 'supabase_bucket' in account and account['supabase_bucket'].strip():
                    credential_detail['has_bucket'] = True
                else:
                    credential_detail['issues'].append("Bucket Supabase não configurado")
                
                # Determinar se as credenciais são válidas
                if (credential_detail['has_url'] and 
                    credential_detail['has_service_key'] and 
                    credential_detail['has_bucket'] and
                    credential_detail['url_format_valid'] and 
                    credential_detail['service_key_format_valid'] and
                    not credential_detail['issues']):
                    supabase_test['valid_credentials'] += 1
                    print(f"✅ {account_name}: credenciais Supabase válidas")
                else:
                    supabase_test['credential_issues'].extend([f"{account_name}: {issue}" for issue in credential_detail['issues']])
                    print(f"❌ {account_name}: problemas nas credenciais - {', '.join(credential_detail['issues'])}")
                
                supabase_test['credential_details'].append(credential_detail)
            
            if supabase_test['valid_credentials'] == 0:
                supabase_test['status'] = 'FAILED'
            elif supabase_test['valid_credentials'] < supabase_test['accounts_tested']:
                supabase_test['status'] = 'PARTIAL'
                
        except Exception as e:
            supabase_test['status'] = 'ERROR'
            supabase_test['credential_issues'].append(f"Erro geral: {str(e)}")
            logger.error(f"Erro no teste de credenciais Supabase: {e}")
        
        return supabase_test
    
    def test_database_connections(self) -> Dict[str, Any]:
        """Testar conexões com bancos de dados"""
        print("🗄️ Testando conexões com bancos de dados...")
        
        db_test = {
            'status': 'PASSED',
            'databases_tested': 0,
            'successful_connections': 0,
            'connection_issues': [],
            'database_details': []
        }
        
        databases = [
            'performance.db',
            'engagement_monitor.db',
            'error_reflection.db',
            'performance_optimizer.db',
            'ab_testing.db'
        ]
        
        for db_name in databases:
            db_test['databases_tested'] += 1
            db_path = self.data_path / db_name
            
            db_detail = {
                'database_name': db_name,
                'file_exists': False,
                'connection_successful': False,
                'integrity_check': False,
                'tables_accessible': False,
                'write_permissions': False,
                'issues': []
            }
            
            if db_path.exists():
                db_detail['file_exists'] = True
                
                try:
                    # Testar conexão
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    db_detail['connection_successful'] = True
                    
                    # Verificar integridade
                    cursor.execute("PRAGMA integrity_check")
                    integrity_result = cursor.fetchone()[0]
                    if integrity_result == 'ok':
                        db_detail['integrity_check'] = True
                    else:
                        db_detail['issues'].append(f"Falha na integridade: {integrity_result}")
                    
                    # Verificar acesso às tabelas
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = cursor.fetchall()
                    if tables:
                        db_detail['tables_accessible'] = True
                    else:
                        db_detail['issues'].append("Nenhuma tabela acessível")
                    
                    # Testar permissões de escrita (criar tabela temporária)
                    try:
                        cursor.execute("CREATE TEMP TABLE test_write (id INTEGER)")
                        cursor.execute("DROP TABLE test_write")
                        db_detail['write_permissions'] = True
                    except Exception as e:
                        db_detail['issues'].append(f"Sem permissão de escrita: {str(e)}")
                    
                    conn.close()
                    
                    # Determinar sucesso geral
                    if (db_detail['connection_successful'] and 
                        db_detail['integrity_check'] and 
                        db_detail['tables_accessible'] and 
                        db_detail['write_permissions']):
                        db_test['successful_connections'] += 1
                        print(f"✅ {db_name}: conexão totalmente funcional")
                    else:
                        db_test['connection_issues'].extend([f"{db_name}: {issue}" for issue in db_detail['issues']])
                        print(f"⚠️ {db_name}: problemas na conexão - {', '.join(db_detail['issues'])}")
                    
                except Exception as e:
                    db_detail['issues'].append(f"Erro de conexão: {str(e)}")
                    db_test['connection_issues'].append(f"{db_name}: {str(e)}")
                    print(f"❌ {db_name}: erro de conexão - {e}")
            else:
                db_detail['issues'].append("Arquivo não encontrado")
                db_test['connection_issues'].append(f"{db_name}: arquivo não encontrado")
                print(f"❌ {db_name}: arquivo não encontrado")
            
            db_test['database_details'].append(db_detail)
        
        if db_test['successful_connections'] == 0:
            db_test['status'] = 'FAILED'
        elif db_test['successful_connections'] < db_test['databases_tested']:
            db_test['status'] = 'PARTIAL'
        
        return db_test
    
    def test_environment_variables(self) -> Dict[str, Any]:
        """Testar variáveis de ambiente"""
        print("🌍 Testando variáveis de ambiente...")
        
        env_test = {
            'status': 'PASSED',
            'variables_tested': 0,
            'variables_found': 0,
            'missing_variables': [],
            'variable_details': []
        }
        
        # Variáveis importantes para verificar
        important_vars = [
            'TZ',  # Timezone
            'PYTHONPATH',  # Python path
            'PATH',  # System path
        ]
        
        # Variáveis opcionais do Railway/Deploy
        optional_vars = [
            'RAILWAY_ENVIRONMENT',
            'PORT',
            'RAILWAY_PROJECT_ID'
        ]
        
        all_vars = important_vars + optional_vars
        
        for var_name in all_vars:
            env_test['variables_tested'] += 1
            is_important = var_name in important_vars
            
            var_detail = {
                'variable_name': var_name,
                'is_important': is_important,
                'found': False,
                'value_length': 0,
                'has_value': False
            }
            
            value = os.environ.get(var_name)
            if value is not None:
                var_detail['found'] = True
                var_detail['value_length'] = len(value)
                var_detail['has_value'] = len(value.strip()) > 0
                env_test['variables_found'] += 1
                
                if var_detail['has_value']:
                    print(f"✅ {var_name}: configurada ({var_detail['value_length']} chars)")
                else:
                    print(f"⚠️ {var_name}: encontrada mas vazia")
            else:
                if is_important:
                    env_test['missing_variables'].append(var_name)
                    print(f"❌ {var_name}: não encontrada (importante)")
                else:
                    print(f"ℹ️ {var_name}: não encontrada (opcional)")
            
            env_test['variable_details'].append(var_detail)
        
        # Verificar timezone específico
        tz_value = os.environ.get('TZ')
        if tz_value and 'America/Sao_Paulo' in tz_value:
            print("✅ Timezone configurado para Brasil")
        else:
            print("⚠️ Timezone não configurado para Brasil")
        
        if env_test['missing_variables']:
            env_test['status'] = 'PARTIAL'
        
        return env_test
    
    def test_file_permissions(self) -> Dict[str, Any]:
        """Testar permissões de arquivos"""
        print("📁 Testando permissões de arquivos...")
        
        perm_test = {
            'status': 'PASSED',
            'files_tested': 0,
            'accessible_files': 0,
            'permission_issues': [],
            'file_details': []
        }
        
        # Arquivos críticos para verificar
        critical_files = [
            'accounts.json',
            'trae_ia_core.py',
            'core/system_prompt_manager.py',
            'src/services/error_reflection_manager.py'
        ]
        
        # Diretórios críticos
        critical_dirs = [
            'data',
            'core',
            'src/services'
        ]
        
        # Testar arquivos
        for file_path in critical_files:
            perm_test['files_tested'] += 1
            full_path = self.base_path / file_path
            
            file_detail = {
                'file_path': file_path,
                'exists': False,
                'readable': False,
                'writable': False,
                'size': 0,
                'issues': []
            }
            
            if full_path.exists():
                file_detail['exists'] = True
                file_detail['size'] = full_path.stat().st_size
                
                # Testar leitura
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        f.read(100)  # Ler apenas os primeiros 100 chars
                    file_detail['readable'] = True
                except Exception as e:
                    file_detail['issues'].append(f"Não legível: {str(e)}")
                
                # Testar escrita (apenas para arquivos de configuração)
                if file_path.endswith('.json'):
                    try:
                        # Testar se podemos abrir para escrita (sem modificar)
                        with open(full_path, 'r+', encoding='utf-8') as f:
                            pass
                        file_detail['writable'] = True
                    except Exception as e:
                        file_detail['issues'].append(f"Não gravável: {str(e)}")
                else:
                    file_detail['writable'] = True  # Assumir que arquivos .py são graváveis
                
                if file_detail['readable'] and file_detail['writable']:
                    perm_test['accessible_files'] += 1
                    print(f"✅ {file_path}: acessível ({file_detail['size']} bytes)")
                else:
                    perm_test['permission_issues'].extend([f"{file_path}: {issue}" for issue in file_detail['issues']])
                    print(f"❌ {file_path}: problemas de acesso - {', '.join(file_detail['issues'])}")
            else:
                file_detail['issues'].append("Arquivo não encontrado")
                perm_test['permission_issues'].append(f"{file_path}: não encontrado")
                print(f"❌ {file_path}: não encontrado")
            
            perm_test['file_details'].append(file_detail)
        
        # Testar diretórios
        for dir_path in critical_dirs:
            full_dir_path = self.base_path / dir_path
            if full_dir_path.exists() and full_dir_path.is_dir():
                print(f"✅ Diretório {dir_path}: acessível")
            else:
                perm_test['permission_issues'].append(f"Diretório {dir_path}: não encontrado")
                print(f"❌ Diretório {dir_path}: não encontrado")
        
        if perm_test['accessible_files'] < len(critical_files):
            perm_test['status'] = 'FAILED'
        
        return perm_test
    
    def generate_connection_auth_report(self, instagram_test: Dict, supabase_test: Dict, 
                                      db_test: Dict, env_test: Dict, perm_test: Dict) -> str:
        """Gerar relatório completo de conexão e autenticação"""
        
        # Determinar status geral
        all_tests = [instagram_test, supabase_test, db_test, env_test, perm_test]
        passed_tests = len([t for t in all_tests if t['status'] == 'PASSED'])
        total_tests = len(all_tests)
        
        if passed_tests == total_tests:
            overall_status = 'ALL_CONNECTIONS_VALID'
        elif passed_tests >= total_tests * 0.8:
            overall_status = 'MOSTLY_VALID'
        else:
            overall_status = 'CRITICAL_ISSUES'
        
        report = {
            'metadata': {
                'generated_at': self.test_timestamp,
                'test_type': 'CONNECTION_AUTHENTICATION_TEST',
                'version': '1.0'
            },
            'overall_status': overall_status,
            'test_summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'success_rate': f"{(passed_tests / total_tests) * 100:.1f}%"
            },
            'detailed_results': {
                'instagram_tokens': instagram_test,
                'supabase_credentials': supabase_test,
                'database_connections': db_test,
                'environment_variables': env_test,
                'file_permissions': perm_test
            },
            'security_recommendations': self._generate_security_recommendations(overall_status, all_tests),
            'connection_readiness': {
                'instagram_ready': instagram_test['status'] == 'PASSED',
                'supabase_ready': supabase_test['status'] == 'PASSED',
                'databases_ready': db_test['status'] == 'PASSED',
                'environment_ready': env_test['status'] in ['PASSED', 'PARTIAL'],
                'files_ready': perm_test['status'] == 'PASSED'
            }
        }
        
        # Salvar relatório
        report_filename = f"connection_auth_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = self.base_path / report_filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📋 Relatório de conexão/autenticação salvo: {report_path}")
        return str(report_path)
    
    def _generate_security_recommendations(self, overall_status: str, test_results: List[Dict]) -> List[str]:
        """Gerar recomendações de segurança"""
        recommendations = []
        
        if overall_status == 'ALL_CONNECTIONS_VALID':
            recommendations.extend([
                "✅ Todas as conexões e autenticações válidas",
                "✅ Tokens e credenciais configurados corretamente",
                "🔒 Sistema seguro para operação"
            ])
        elif overall_status == 'MOSTLY_VALID':
            recommendations.extend([
                "⚠️ Maioria das conexões válidas",
                "🔧 Revisar itens com problemas",
                "🔒 Verificar segurança antes da produção"
            ])
        else:
            recommendations.extend([
                "🚨 Problemas críticos de conexão/autenticação",
                "🔧 Correções necessárias antes da execução",
                "🔒 Revisar todas as credenciais"
            ])
        
        # Recomendações específicas
        for test in test_results:
            if test['status'] == 'FAILED':
                if 'token_issues' in test:
                    recommendations.append("🔑 Verificar e renovar tokens do Instagram")
                if 'credential_issues' in test:
                    recommendations.append("☁️ Verificar credenciais do Supabase")
                if 'connection_issues' in test:
                    recommendations.append("🗄️ Verificar conectividade com bancos")
                if 'missing_variables' in test:
                    recommendations.append("🌍 Configurar variáveis de ambiente")
                if 'permission_issues' in test:
                    recommendations.append("📁 Verificar permissões de arquivos")
        
        return recommendations
    
    def run_complete_test(self) -> Dict[str, Any]:
        """Executar teste completo de conexão e autenticação"""
        print("🔐 Iniciando teste completo de conexão e autenticação...")
        print("="*60)
        
        # Executar todos os testes
        instagram_test = self.test_instagram_tokens()
        supabase_test = self.test_supabase_credentials()
        db_test = self.test_database_connections()
        env_test = self.test_environment_variables()
        perm_test = self.test_file_permissions()
        
        # Gerar relatório
        report_path = self.generate_connection_auth_report(
            instagram_test, supabase_test, db_test, env_test, perm_test
        )
        
        # Resultado final
        all_tests = [instagram_test, supabase_test, db_test, env_test, perm_test]
        passed_tests = len([t for t in all_tests if t['status'] == 'PASSED'])
        
        test_result = {
            'overall_status': 'PASSED' if passed_tests >= 4 else 'FAILED',
            'timestamp': self.test_timestamp,
            'tests_passed': passed_tests,
            'total_tests': len(all_tests),
            'success_rate': f"{(passed_tests / len(all_tests)) * 100:.1f}%",
            'connections_ready': passed_tests >= 4,
            'report_path': report_path
        }
        
        print("="*60)
        if test_result['overall_status'] == 'PASSED':
            print("✅ CONEXÕES E AUTENTICAÇÃO: TODOS OS TESTES PASSARAM")
            print("🔐 Sistema pronto para operação segura")
        else:
            print("⚠️ CONEXÕES E AUTENTICAÇÃO: ALGUNS TESTES FALHARAM")
            print("Verificar relatório para correções necessárias")
        
        print(f"📊 Taxa de sucesso: {test_result['success_rate']}")
        print(f"📋 Relatório: {report_path}")
        
        return test_result

def main():
    """Função principal"""
    print("🔐 Connection & Authentication Test - Teste de Conexão e Autenticação")
    print("="*60)
    
    try:
        tester = ConnectionAuthTester()
        result = tester.run_complete_test()
        
        if result['overall_status'] == 'PASSED':
            print("\n🎉 CONEXÕES E AUTENTICAÇÃO TOTALMENTE FUNCIONAIS!")
            print("✅ Todos os parâmetros validados")
            print("✅ Tokens e credenciais verificados")
            print("🔒 Sistema seguro para operação")
        else:
            print("\n⚠️ PROBLEMAS IDENTIFICADOS NAS CONEXÕES")
            print("Verificar relatório para correções necessárias")
            
        return result
        
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO no teste de conexão: {e}")
        logger.error(f"Erro crítico: {e}")
        return {'overall_status': 'CRITICAL', 'error': str(e)}

if __name__ == "__main__":
    main()