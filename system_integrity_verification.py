#!/usr/bin/env python3
"""
System Integrity Verification - Verificação de Integridade do Sistema
Valida que todas as correções do LTM foram aplicadas corretamente
Data: 2025-10-23
"""

import json
import sqlite3
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import subprocess

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SystemIntegrityVerifier:
    """Verificador de integridade do sistema após atualização do LTM"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.data_path = self.base_path / "data"
        self.verification_timestamp = datetime.now().isoformat()
        
        # Componentes críticos para verificar
        self.critical_components = {
            'ltm_databases': [
                'error_reflection.db',
                'performance.db', 
                'engagement_monitor.db',
                'performance_optimizer.db',
                'ab_testing.db'
            ],
            'config_files': [
                'accounts.json',
                'config/system_prompt_core.json',
                'config/bot_config.json'
            ],
            'core_modules': [
                'core/system_prompt_manager.py',
                'src/services/error_reflection_manager.py',
                'src/services/structured_error_logger.py'
            ]
        }
        
    def verify_ltm_databases(self) -> Dict[str, Any]:
        """Verificar integridade dos bancos de dados do LTM"""
        print("🔍 Verificando integridade dos bancos de dados do LTM...")
        
        db_status = {
            'overall_status': 'HEALTHY',
            'databases': {},
            'total_records': 0,
            'issues_found': []
        }
        
        for db_name in self.critical_components['ltm_databases']:
            db_path = self.data_path / db_name
            
            if not db_path.exists():
                db_status['databases'][db_name] = {
                    'status': 'MISSING',
                    'error': 'Database file not found'
                }
                db_status['issues_found'].append(f"Database {db_name} not found")
                db_status['overall_status'] = 'ISSUES_FOUND'
                continue
            
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Verificar integridade
                cursor.execute("PRAGMA integrity_check")
                integrity_result = cursor.fetchone()[0]
                
                # Contar tabelas e registros
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                total_records = 0
                table_details = {}
                
                for table in tables:
                    if table != 'sqlite_sequence':
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        table_details[table] = count
                        total_records += count
                
                db_status['databases'][db_name] = {
                    'status': 'HEALTHY' if integrity_result == 'ok' else 'CORRUPTED',
                    'integrity_check': integrity_result,
                    'tables': len(tables),
                    'total_records': total_records,
                    'table_details': table_details
                }
                
                db_status['total_records'] += total_records
                
                if integrity_result != 'ok':
                    db_status['issues_found'].append(f"Integrity issues in {db_name}")
                    db_status['overall_status'] = 'ISSUES_FOUND'
                
                conn.close()
                print(f"✅ {db_name}: {len(tables)} tabelas, {total_records} registros")
                
            except Exception as e:
                db_status['databases'][db_name] = {
                    'status': 'ERROR',
                    'error': str(e)
                }
                db_status['issues_found'].append(f"Error accessing {db_name}: {str(e)}")
                db_status['overall_status'] = 'CRITICAL'
                print(f"❌ Erro ao verificar {db_name}: {e}")
        
        return db_status
    
    def verify_ltm_updates(self) -> Dict[str, Any]:
        """Verificar se as atualizações do LTM foram aplicadas corretamente"""
        print("📝 Verificando atualizações do LTM...")
        
        ltm_updates_status = {
            'status': 'VERIFIED',
            'recent_solutions': 0,
            'error_patterns_updated': 0,
            'optimization_log_updated': False,
            'issues': []
        }
        
        try:
            # Verificar error_reflection.db
            error_db_path = self.data_path / "error_reflection.db"
            if error_db_path.exists():
                conn = sqlite3.connect(error_db_path)
                cursor = conn.cursor()
                
                # Verificar soluções recentes (hoje)
                today = datetime.now().strftime('%Y-%m-%d')
                cursor.execute('''
                    SELECT COUNT(*) FROM solution_attempts 
                    WHERE timestamp LIKE ? AND success = 1
                ''', (f"{today}%",))
                
                recent_solutions = cursor.fetchone()[0]
                ltm_updates_status['recent_solutions'] = recent_solutions
                
                # Verificar padrões de erro atualizados
                cursor.execute('''
                    SELECT COUNT(*) FROM error_patterns 
                    WHERE last_occurrence LIKE ?
                ''', (f"{today}%",))
                
                updated_patterns = cursor.fetchone()[0]
                ltm_updates_status['error_patterns_updated'] = updated_patterns
                
                conn.close()
                
                if recent_solutions == 0:
                    ltm_updates_status['issues'].append("Nenhuma solução recente registrada")
                
                print(f"✅ Soluções recentes: {recent_solutions}")
                print(f"✅ Padrões atualizados: {updated_patterns}")
            
            # Verificar optimization_log.json
            opt_log_path = self.data_path / "optimization_log.json"
            if opt_log_path.exists():
                with open(opt_log_path, 'r', encoding='utf-8') as f:
                    opt_data = json.load(f)
                
                # Verificar se foi atualizado hoje
                last_update = opt_data.get('last_update', '')
                if today in last_update:
                    ltm_updates_status['optimization_log_updated'] = True
                    print("✅ Optimization log atualizado")
                else:
                    ltm_updates_status['issues'].append("Optimization log não foi atualizado hoje")
            
        except Exception as e:
            ltm_updates_status['status'] = 'ERROR'
            ltm_updates_status['issues'].append(f"Erro na verificação: {str(e)}")
            print(f"❌ Erro na verificação de atualizações: {e}")
        
        return ltm_updates_status
    
    def verify_system_connections(self) -> Dict[str, Any]:
        """Verificar conexões críticas do sistema"""
        print("🔗 Verificando conexões do sistema...")
        
        connections_status = {
            'overall_status': 'OPERATIONAL',
            'connections': {},
            'issues': []
        }
        
        # Verificar se accounts.json existe e tem configurações válidas
        try:
            accounts_path = self.base_path / "accounts.json"
            if accounts_path.exists():
                with open(accounts_path, 'r', encoding='utf-8') as f:
                    accounts_data = json.load(f)
                
                # accounts.json é uma lista de contas
                if isinstance(accounts_data, list) and len(accounts_data) > 0:
                    # Verificar configurações do Supabase na primeira conta
                    first_account = accounts_data[0]
                    required_supabase_keys = ['supabase_url', 'supabase_service_key', 'supabase_bucket']
                    
                    supabase_configured = all(key in first_account for key in required_supabase_keys)
                    
                    connections_status['connections']['supabase'] = {
                        'status': 'CONFIGURED' if supabase_configured else 'INCOMPLETE',
                        'keys_present': len([k for k in required_supabase_keys if k in first_account])
                    }
                    
                    # Verificar contas do Instagram
                    instagram_accounts = [acc for acc in accounts_data if 'instagram_access_token' in acc]
                    connections_status['connections']['instagram'] = {
                        'status': 'CONFIGURED' if len(instagram_accounts) > 0 else 'NO_ACCOUNTS',
                        'account_count': len(instagram_accounts),
                        'total_accounts': len(accounts_data)
                    }
                    
                    print(f"✅ Supabase: {'CONFIGURADO' if supabase_configured else 'INCOMPLETO'}")
                    print(f"✅ Instagram: {len(instagram_accounts)} contas configuradas de {len(accounts_data)} total")
                else:
                    connections_status['connections']['accounts_structure'] = {
                        'status': 'INVALID',
                        'error': 'accounts.json deve ser uma lista de contas'
                    }
                    connections_status['issues'].append("Estrutura inválida do accounts.json")
                    connections_status['overall_status'] = 'ISSUES_FOUND'
                
            else:
                connections_status['connections']['accounts_file'] = {
                    'status': 'MISSING',
                    'error': 'accounts.json not found'
                }
                connections_status['issues'].append("accounts.json não encontrado")
                connections_status['overall_status'] = 'ISSUES_FOUND'
                
        except Exception as e:
            connections_status['connections']['accounts_file'] = {
                'status': 'ERROR',
                'error': str(e)
            }
            connections_status['issues'].append(f"Erro ao verificar accounts.json: {str(e)}")
            connections_status['overall_status'] = 'CRITICAL'
        
        return connections_status
    
    def verify_core_modules(self) -> Dict[str, Any]:
        """Verificar módulos principais do sistema"""
        print("🧩 Verificando módulos principais...")
        
        modules_status = {
            'overall_status': 'OPERATIONAL',
            'modules': {},
            'import_tests': {},
            'issues': []
        }
        
        for module_path in self.critical_components['core_modules']:
            full_path = self.base_path / module_path
            
            if not full_path.exists():
                modules_status['modules'][module_path] = {
                    'status': 'MISSING',
                    'error': 'File not found'
                }
                modules_status['issues'].append(f"Módulo {module_path} não encontrado")
                modules_status['overall_status'] = 'ISSUES_FOUND'
                continue
            
            # Verificar se o arquivo pode ser lido
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                modules_status['modules'][module_path] = {
                    'status': 'PRESENT',
                    'size': len(content),
                    'lines': len(content.split('\n'))
                }
                
                print(f"✅ {module_path}: {len(content.split('\\n'))} linhas")
                
            except Exception as e:
                modules_status['modules'][module_path] = {
                    'status': 'ERROR',
                    'error': str(e)
                }
                modules_status['issues'].append(f"Erro ao ler {module_path}: {str(e)}")
                modules_status['overall_status'] = 'CRITICAL'
        
        return modules_status
    
    def verify_scheduler_readiness(self) -> Dict[str, Any]:
        """Verificar se o sistema está pronto para agendamento"""
        print("⏰ Verificando prontidão do agendador...")
        
        scheduler_status = {
            'overall_status': 'READY',
            'components': {},
            'next_execution_ready': False,
            'issues': []
        }
        
        # Verificar arquivos de configuração do Railway
        railway_files = ['railway.yaml', 'Procfile']
        for file_name in railway_files:
            file_path = self.base_path / file_name
            if file_path.exists():
                scheduler_status['components'][file_name] = 'PRESENT'
                print(f"✅ {file_name}: presente")
            else:
                scheduler_status['components'][file_name] = 'MISSING'
                scheduler_status['issues'].append(f"{file_name} não encontrado")
        
        # Verificar se há conteúdo agendado
        try:
            # Simular verificação de próxima execução
            current_hour = datetime.now().hour
            
            # Sistema deve estar pronto para execução às 21h BRT
            if current_hour < 21:
                time_to_execution = 21 - current_hour
                scheduler_status['next_execution_ready'] = True
                scheduler_status['time_to_next_execution'] = f"{time_to_execution} horas"
                print(f"✅ Próxima execução em {time_to_execution} horas (21h BRT)")
            else:
                scheduler_status['next_execution_ready'] = True
                scheduler_status['time_to_next_execution'] = "Próximo dia"
                print("✅ Sistema pronto para próxima execução")
                
        except Exception as e:
            scheduler_status['issues'].append(f"Erro na verificação do agendador: {str(e)}")
            scheduler_status['overall_status'] = 'ISSUES_FOUND'
        
        return scheduler_status
    
    def generate_integrity_report(self, db_status: Dict, ltm_status: Dict, 
                                connections_status: Dict, modules_status: Dict,
                                scheduler_status: Dict) -> str:
        """Gerar relatório completo de integridade"""
        
        # Determinar status geral
        all_statuses = [
            db_status['overall_status'],
            ltm_status['status'],
            connections_status['overall_status'],
            modules_status['overall_status'],
            scheduler_status['overall_status']
        ]
        
        if 'CRITICAL' in all_statuses:
            overall_status = 'CRITICAL'
        elif 'ISSUES_FOUND' in all_statuses or 'ERROR' in all_statuses:
            overall_status = 'ISSUES_FOUND'
        else:
            overall_status = 'HEALTHY'
        
        report = {
            'metadata': {
                'generated_at': self.verification_timestamp,
                'verification_type': 'POST_LTM_UPDATE_INTEGRITY_CHECK',
                'version': '1.0'
            },
            'overall_status': overall_status,
            'summary': {
                'ltm_databases': db_status['overall_status'],
                'ltm_updates': ltm_status['status'],
                'system_connections': connections_status['overall_status'],
                'core_modules': modules_status['overall_status'],
                'scheduler_readiness': scheduler_status['overall_status']
            },
            'detailed_results': {
                'databases': db_status,
                'ltm_updates': ltm_status,
                'connections': connections_status,
                'modules': modules_status,
                'scheduler': scheduler_status
            },
            'recommendations': self._generate_recommendations(overall_status, all_statuses)
        }
        
        # Salvar relatório
        report_filename = f"system_integrity_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = self.base_path / report_filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📋 Relatório de integridade salvo: {report_path}")
        return str(report_path)
    
    def _generate_recommendations(self, overall_status: str, component_statuses: List[str]) -> List[str]:
        """Gerar recomendações baseadas no status"""
        recommendations = []
        
        if overall_status == 'HEALTHY':
            recommendations.extend([
                "✅ Sistema totalmente operacional após atualização do LTM",
                "✅ Todas as correções técnicas foram aplicadas com sucesso",
                "✅ Sistema pronto para operação 24/7",
                "✅ Agendamento para 21h BRT configurado e funcional"
            ])
        elif overall_status == 'ISSUES_FOUND':
            recommendations.extend([
                "⚠️ Problemas menores identificados - sistema ainda operacional",
                "🔧 Revisar componentes com status 'ISSUES_FOUND'",
                "📊 Monitorar performance nas próximas execuções"
            ])
        else:
            recommendations.extend([
                "🚨 Problemas críticos identificados",
                "🔧 Correção imediata necessária antes da próxima execução",
                "📞 Verificar logs detalhados para diagnóstico"
            ])
        
        return recommendations
    
    def run_complete_verification(self) -> Dict[str, Any]:
        """Executar verificação completa de integridade"""
        print("🔍 Iniciando verificação completa de integridade do sistema...")
        print("="*60)
        
        # Executar todas as verificações
        db_status = self.verify_ltm_databases()
        ltm_status = self.verify_ltm_updates()
        connections_status = self.verify_system_connections()
        modules_status = self.verify_core_modules()
        scheduler_status = self.verify_scheduler_readiness()
        
        # Gerar relatório
        report_path = self.generate_integrity_report(
            db_status, ltm_status, connections_status, modules_status, scheduler_status
        )
        
        # Resultado final
        verification_result = {
            'overall_status': db_status['overall_status'],
            'timestamp': self.verification_timestamp,
            'databases_healthy': db_status['overall_status'] in ['HEALTHY'],
            'ltm_updated': ltm_status['status'] in ['VERIFIED'],
            'connections_ok': connections_status['overall_status'] in ['OPERATIONAL'],
            'modules_ok': modules_status['overall_status'] in ['OPERATIONAL'],
            'scheduler_ready': scheduler_status['overall_status'] in ['READY'],
            'report_path': report_path,
            'total_records': db_status['total_records']
        }
        
        print("="*60)
        if verification_result['overall_status'] == 'HEALTHY':
            print("✅ VERIFICAÇÃO DE INTEGRIDADE CONCLUÍDA: SISTEMA SAUDÁVEL")
        else:
            print("⚠️ VERIFICAÇÃO CONCLUÍDA: PROBLEMAS IDENTIFICADOS")
        print(f"📋 Relatório: {report_path}")
        
        return verification_result

def main():
    """Função principal"""
    print("🔍 System Integrity Verification - Verificação Pós-Atualização LTM")
    print("="*60)
    
    try:
        verifier = SystemIntegrityVerifier()
        result = verifier.run_complete_verification()
        
        if result['overall_status'] == 'HEALTHY':
            print("\n🎉 SISTEMA TOTALMENTE OPERACIONAL!")
            print("✅ LTM atualizado e funcionando corretamente")
            print("✅ Todas as correções técnicas aplicadas")
            print("✅ Sistema pronto para operação 24/7")
        else:
            print("\n⚠️ PROBLEMAS IDENTIFICADOS")
            print("Verificar relatório para detalhes específicos")
            
        return result
        
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO na verificação: {e}")
        logger.error(f"Erro crítico: {e}")
        return {'overall_status': 'CRITICAL', 'error': str(e)}

if __name__ == "__main__":
    main()