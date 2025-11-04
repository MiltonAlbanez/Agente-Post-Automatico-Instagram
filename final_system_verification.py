#!/usr/bin/env python3
"""
Final System Verification - Verificação Final Completa do Sistema
Validação final antes da operação em produção
Data: 2025-10-23
"""

import json
import os
import sys
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinalSystemVerifier:
    """Verificador final completo do sistema"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.data_path = self.base_path / "data"
        self.verification_timestamp = datetime.now().isoformat()
        
    def verify_core_system_files(self) -> Dict[str, Any]:
        """Verificar arquivos principais do sistema"""
        print("📁 Verificando arquivos principais do sistema...")
        
        core_files = {
            'accounts.json': 'Configuração das contas',
            'trae_ia_core.py': 'Módulo principal do sistema',
            'railway.yaml': 'Configuração do Railway',
            'Procfile': 'Configuração de processo',
            'requirements.txt': 'Dependências Python'
        }
        
        verification_result = {
            'timestamp': self.verification_timestamp,
            'files_checked': len(core_files),
            'files_found': 0,
            'missing_files': [],
            'file_details': {},
            'status': 'UNKNOWN'
        }
        
        for file_name, description in core_files.items():
            file_path = self.base_path / file_name
            
            if file_path.exists():
                verification_result['files_found'] += 1
                file_size = file_path.stat().st_size
                
                verification_result['file_details'][file_name] = {
                    'exists': True,
                    'size_bytes': file_size,
                    'description': description,
                    'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                }
                
                print(f"✅ {file_name}: {file_size} bytes")
            else:
                verification_result['missing_files'].append(file_name)
                verification_result['file_details'][file_name] = {
                    'exists': False,
                    'description': description
                }
                print(f"❌ {file_name}: AUSENTE")
        
        # Determinar status
        if verification_result['files_found'] == verification_result['files_checked']:
            verification_result['status'] = 'ALL_FILES_PRESENT'
        elif verification_result['files_found'] >= 4:
            verification_result['status'] = 'MOSTLY_COMPLETE'
        else:
            verification_result['status'] = 'CRITICAL_FILES_MISSING'
        
        return verification_result
    
    def verify_database_integrity(self) -> Dict[str, Any]:
        """Verificar integridade completa dos bancos"""
        print("🗄️ Verificando integridade completa dos bancos...")
        
        databases = [
            'performance.db',
            'engagement_monitor.db', 
            'error_reflection.db',
            'performance_optimizer.db',
            'ab_testing.db'
        ]
        
        integrity_result = {
            'timestamp': self.verification_timestamp,
            'databases_checked': len(databases),
            'databases_healthy': 0,
            'total_records': 0,
            'database_status': {},
            'overall_status': 'UNKNOWN'
        }
        
        for db_name in databases:
            db_path = self.data_path / db_name
            
            if db_path.exists():
                try:
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    # Verificar integridade
                    cursor.execute("PRAGMA integrity_check")
                    integrity_check = cursor.fetchone()[0]
                    
                    # Contar registros
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = [row[0] for row in cursor.fetchall()]
                    
                    total_records = 0
                    table_info = {}
                    
                    for table in tables:
                        if table != 'sqlite_sequence':
                            cursor.execute(f"SELECT COUNT(*) FROM {table}")
                            count = cursor.fetchone()[0]
                            total_records += count
                            table_info[table] = count
                    
                    integrity_result['database_status'][db_name] = {
                        'healthy': integrity_check == 'ok',
                        'total_records': total_records,
                        'tables': table_info,
                        'file_size_mb': round(db_path.stat().st_size / (1024 * 1024), 3)
                    }
                    
                    if integrity_check == 'ok':
                        integrity_result['databases_healthy'] += 1
                        print(f"✅ {db_name}: {total_records} registros, integridade OK")
                    else:
                        print(f"⚠️ {db_name}: Problemas de integridade")
                    
                    integrity_result['total_records'] += total_records
                    conn.close()
                    
                except Exception as e:
                    integrity_result['database_status'][db_name] = {
                        'healthy': False,
                        'error': str(e)
                    }
                    print(f"❌ {db_name}: Erro - {e}")
            else:
                integrity_result['database_status'][db_name] = {
                    'healthy': False,
                    'error': 'Arquivo não encontrado'
                }
                print(f"❌ {db_name}: Arquivo não encontrado")
        
        # Status geral
        if integrity_result['databases_healthy'] == integrity_result['databases_checked']:
            integrity_result['overall_status'] = 'ALL_DATABASES_HEALTHY'
        elif integrity_result['databases_healthy'] >= 3:
            integrity_result['overall_status'] = 'MOSTLY_HEALTHY'
        else:
            integrity_result['overall_status'] = 'CRITICAL_DATABASE_ISSUES'
        
        return integrity_result
    
    def verify_account_configuration(self) -> Dict[str, Any]:
        """Verificar configuração completa das contas"""
        print("👤 Verificando configuração completa das contas...")
        
        config_result = {
            'timestamp': self.verification_timestamp,
            'accounts_found': 0,
            'valid_accounts': 0,
            'account_details': [],
            'configuration_issues': [],
            'status': 'UNKNOWN'
        }
        
        try:
            accounts_path = self.base_path / "accounts.json"
            
            if not accounts_path.exists():
                config_result['configuration_issues'].append('accounts.json não encontrado')
                config_result['status'] = 'CRITICAL_ERROR'
                return config_result
            
            with open(accounts_path, 'r', encoding='utf-8') as f:
                accounts_data = json.load(f)
            
            config_result['accounts_found'] = len(accounts_data)
            
            required_fields = [
                'instagram_access_token',
                'instagram_id',
                'supabase_url',
                'supabase_service_key',
                'hashtags_pesquisa',
                'usernames'
            ]
            
            for i, account in enumerate(accounts_data):
                account_name = account.get('account_name', f'Account_{i+1}')
                
                account_detail = {
                    'account_name': account_name,
                    'has_all_required_fields': True,
                    'missing_fields': [],
                    'field_status': {}
                }
                
                for field in required_fields:
                    if field in account and account[field]:
                        account_detail['field_status'][field] = 'PRESENT'
                    else:
                        account_detail['has_all_required_fields'] = False
                        account_detail['missing_fields'].append(field)
                        account_detail['field_status'][field] = 'MISSING'
                
                # Verificações específicas
                if 'hashtags_pesquisa' in account:
                    hashtags_count = len(account['hashtags_pesquisa'])
                    account_detail['hashtags_count'] = hashtags_count
                    if hashtags_count == 0:
                        account_detail['configuration_issues'] = account_detail.get('configuration_issues', [])
                        account_detail['configuration_issues'].append('Nenhuma hashtag configurada')
                
                if 'usernames' in account:
                    usernames_count = len(account['usernames'])
                    account_detail['usernames_count'] = usernames_count
                    if usernames_count == 0:
                        account_detail['configuration_issues'] = account_detail.get('configuration_issues', [])
                        account_detail['configuration_issues'].append('Nenhum username configurado')
                
                if account_detail['has_all_required_fields']:
                    config_result['valid_accounts'] += 1
                    print(f"✅ {account_name}: Configuração completa")
                else:
                    print(f"⚠️ {account_name}: Campos ausentes - {', '.join(account_detail['missing_fields'])}")
                
                config_result['account_details'].append(account_detail)
            
            # Status geral
            if config_result['valid_accounts'] == config_result['accounts_found'] and config_result['accounts_found'] >= 2:
                config_result['status'] = 'ALL_ACCOUNTS_VALID'
            elif config_result['valid_accounts'] >= 1:
                config_result['status'] = 'PARTIAL_CONFIGURATION'
            else:
                config_result['status'] = 'NO_VALID_ACCOUNTS'
                
        except Exception as e:
            config_result['configuration_issues'].append(f'Erro ao carregar configuração: {str(e)}')
            config_result['status'] = 'CRITICAL_ERROR'
            print(f"❌ Erro na verificação de contas: {e}")
        
        return config_result
    
    def verify_production_readiness(self) -> Dict[str, Any]:
        """Verificar prontidão para produção"""
        print("🚀 Verificando prontidão para produção...")
        
        readiness_result = {
            'timestamp': self.verification_timestamp,
            'production_ready': False,
            'readiness_score': 0,
            'critical_checks': {},
            'recommendations': [],
            'deployment_status': 'NOT_READY'
        }
        
        # Verificações críticas
        critical_checks = {
            'core_files': self.verify_core_system_files(),
            'database_integrity': self.verify_database_integrity(),
            'account_configuration': self.verify_account_configuration()
        }
        
        readiness_result['critical_checks'] = critical_checks
        
        # Calcular score de prontidão
        score_weights = {
            'core_files': 30,
            'database_integrity': 35,
            'account_configuration': 35
        }
        
        total_score = 0
        
        for check_name, check_result in critical_checks.items():
            check_score = 0
            
            if check_name == 'core_files':
                if check_result['status'] == 'ALL_FILES_PRESENT':
                    check_score = 100
                elif check_result['status'] == 'MOSTLY_COMPLETE':
                    check_score = 70
                else:
                    check_score = 30
            
            elif check_name == 'database_integrity':
                if check_result['overall_status'] == 'ALL_DATABASES_HEALTHY':
                    check_score = 100
                elif check_result['overall_status'] == 'MOSTLY_HEALTHY':
                    check_score = 75
                else:
                    check_score = 25
            
            elif check_name == 'account_configuration':
                if check_result['status'] == 'ALL_ACCOUNTS_VALID':
                    check_score = 100
                elif check_result['status'] == 'PARTIAL_CONFIGURATION':
                    check_score = 60
                else:
                    check_score = 20
            
            weighted_score = (check_score * score_weights[check_name]) / 100
            total_score += weighted_score
            
            print(f"📊 {check_name}: {check_score}% (peso: {score_weights[check_name]}%)")
        
        readiness_result['readiness_score'] = round(total_score, 1)
        
        # Determinar status de deployment
        if total_score >= 90:
            readiness_result['deployment_status'] = 'PRODUCTION_READY'
            readiness_result['production_ready'] = True
            readiness_result['recommendations'] = [
                "✅ Sistema pronto para produção",
                "🚀 Pode iniciar operação automática",
                "📊 Monitorar métricas após deploy"
            ]
        elif total_score >= 75:
            readiness_result['deployment_status'] = 'READY_WITH_MINOR_ISSUES'
            readiness_result['recommendations'] = [
                "⚠️ Sistema quase pronto - corrigir problemas menores",
                "🔧 Revisar configurações pendentes",
                "📋 Testar em ambiente controlado"
            ]
        elif total_score >= 50:
            readiness_result['deployment_status'] = 'NEEDS_IMPROVEMENTS'
            readiness_result['recommendations'] = [
                "🚨 Sistema precisa de melhorias",
                "🔧 Corrigir problemas identificados",
                "📞 Revisar configurações críticas"
            ]
        else:
            readiness_result['deployment_status'] = 'NOT_READY'
            readiness_result['recommendations'] = [
                "❌ Sistema não pronto para produção",
                "🚨 Problemas críticos identificados",
                "🔧 Correções urgentes necessárias"
            ]
        
        print(f"📊 Score de Prontidão: {readiness_result['readiness_score']}%")
        print(f"🎯 Status: {readiness_result['deployment_status']}")
        
        return readiness_result
    
    def generate_final_report(self) -> str:
        """Gerar relatório final completo"""
        print("📋 Gerando relatório final completo...")
        
        # Executar verificação completa
        production_readiness = self.verify_production_readiness()
        
        # Criar relatório final
        final_report = {
            'metadata': {
                'generated_at': self.verification_timestamp,
                'verification_type': 'FINAL_SYSTEM_VERIFICATION',
                'version': '1.0'
            },
            'executive_summary': {
                'production_ready': production_readiness['production_ready'],
                'readiness_score': production_readiness['readiness_score'],
                'deployment_status': production_readiness['deployment_status'],
                'critical_issues_count': len([
                    check for check in production_readiness['critical_checks'].values()
                    if check.get('status', '').endswith('ERROR') or check.get('overall_status', '').startswith('CRITICAL')
                ])
            },
            'detailed_verification': production_readiness,
            'final_recommendations': production_readiness['recommendations'],
            'next_steps': [
                "📊 Monitorar sistema após deploy",
                "🔄 Manter backups regulares",
                "📈 Acompanhar métricas de performance",
                "🔧 Realizar manutenção preventiva"
            ]
        }
        
        # Salvar relatório
        report_filename = f"final_system_verification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = self.base_path / report_filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(final_report, f, indent=2, ensure_ascii=False)
        
        print(f"📋 Relatório final salvo: {report_path}")
        
        return str(report_path)
    
    def run_final_verification(self) -> Dict[str, Any]:
        """Executar verificação final completa"""
        print("🔍 Iniciando verificação final completa do sistema...")
        print("="*60)
        
        try:
            # Gerar relatório final
            report_path = self.generate_final_report()
            
            # Carregar relatório para obter resultado
            with open(report_path, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            
            result = {
                'status': 'SUCCESS',
                'timestamp': self.verification_timestamp,
                'report_path': report_path,
                'production_ready': report_data['executive_summary']['production_ready'],
                'readiness_score': report_data['executive_summary']['readiness_score'],
                'deployment_status': report_data['executive_summary']['deployment_status']
            }
            
            print("="*60)
            if result['production_ready']:
                print("✅ SISTEMA PRONTO PARA PRODUÇÃO!")
                print(f"🎯 Score de Prontidão: {result['readiness_score']}%")
                print(f"🚀 Status: {result['deployment_status']}")
                print("📊 Todas as verificações críticas passaram")
                print("🎉 Sistema pode ser colocado em operação")
            else:
                print("⚠️ SISTEMA PRECISA DE AJUSTES")
                print(f"📊 Score de Prontidão: {result['readiness_score']}%")
                print(f"🔧 Status: {result['deployment_status']}")
                print("📋 Verificar relatório para detalhes")
            
            return result
            
        except Exception as e:
            print(f"\n❌ ERRO na verificação final: {e}")
            logger.error(f"Erro crítico: {e}")
            return {'status': 'ERROR', 'error': str(e)}

def main():
    """Função principal"""
    print("🔍 Final System Verification - Verificação Final Completa")
    print("="*60)
    
    try:
        verifier = FinalSystemVerifier()
        result = verifier.run_final_verification()
        
        if result['status'] == 'SUCCESS':
            if result['production_ready']:
                print("\n🎉 VERIFICAÇÃO FINAL CONCLUÍDA COM SUCESSO!")
                print("✅ Sistema totalmente pronto para operação")
                print("🚀 Pode iniciar postagens automáticas")
                print("📊 Monitoramento contínuo recomendado")
            else:
                print("\n⚠️ VERIFICAÇÃO CONCLUÍDA - AJUSTES NECESSÁRIOS")
                print("🔧 Revisar problemas identificados")
                print("📋 Implementar correções recomendadas")
        else:
            print("\n❌ PROBLEMAS NA VERIFICAÇÃO FINAL")
            print("Verificar logs para detalhes específicos")
            
        return result
        
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO na verificação: {e}")
        logger.error(f"Erro crítico: {e}")
        return {'status': 'CRITICAL', 'error': str(e)}

if __name__ == "__main__":
    main()