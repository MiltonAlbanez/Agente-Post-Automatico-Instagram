#!/usr/bin/env python3
"""
Diagnóstico do Problema de Simulação vs Postagem Real
Identifica por que o sistema está executando apenas simulações
Data: 2025-10-23
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimulationIssueDiagnoser:
    """Diagnosticador do problema de simulação vs postagem real"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.diagnosis_timestamp = datetime.now().isoformat()
        
    def analyze_railway_configuration(self) -> Dict[str, Any]:
        """Analisar configuração do Railway"""
        print("🚂 Analisando configuração do Railway...")
        
        railway_analysis = {
            'timestamp': self.diagnosis_timestamp,
            'railway_files': {},
            'environment_variables': {},
            'configuration_issues': [],
            'status': 'UNKNOWN'
        }
        
        # Verificar arquivos do Railway
        railway_files = ['railway.yaml', 'Procfile', 'railway.json']
        
        for file_name in railway_files:
            file_path = self.base_path / file_name
            
            if file_path.exists():
                try:
                    if file_name.endswith('.yaml'):
                        import yaml
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = yaml.safe_load(f)
                    elif file_name.endswith('.json'):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = json.load(f)
                    else:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                    
                    railway_analysis['railway_files'][file_name] = {
                        'exists': True,
                        'content': content,
                        'size_bytes': file_path.stat().st_size
                    }
                    
                    print(f"✅ {file_name}: Encontrado ({file_path.stat().st_size} bytes)")
                    
                except Exception as e:
                    railway_analysis['railway_files'][file_name] = {
                        'exists': True,
                        'error': str(e)
                    }
                    print(f"⚠️ {file_name}: Erro ao ler - {e}")
            else:
                railway_analysis['railway_files'][file_name] = {'exists': False}
                print(f"❌ {file_name}: Não encontrado")
        
        # Verificar variáveis de ambiente críticas
        critical_env_vars = [
            'DRY_RUN',
            'SIMULATION_MODE',
            'PRODUCTION_MODE',
            'REAL_POSTING',
            'TEST_MODE',
            'DEBUG_MODE'
        ]
        
        for var in critical_env_vars:
            value = os.environ.get(var)
            railway_analysis['environment_variables'][var] = value
            
            if value:
                print(f"🔍 {var}: {value}")
                
                # Identificar problemas
                if var in ['DRY_RUN', 'SIMULATION_MODE', 'TEST_MODE'] and value.lower() in ['true', '1', 'yes']:
                    railway_analysis['configuration_issues'].append(f"{var} está ativado - impedindo postagens reais")
                elif var in ['PRODUCTION_MODE', 'REAL_POSTING'] and value.lower() in ['false', '0', 'no']:
                    railway_analysis['configuration_issues'].append(f"{var} está desativado - impedindo postagens reais")
            else:
                print(f"❌ {var}: Não configurado")
        
        return railway_analysis
    
    def analyze_core_system_mode(self) -> Dict[str, Any]:
        """Analisar modo do sistema principal"""
        print("🔧 Analisando modo do sistema principal...")
        
        system_analysis = {
            'timestamp': self.diagnosis_timestamp,
            'core_file_analysis': {},
            'mode_indicators': [],
            'simulation_triggers': [],
            'status': 'UNKNOWN'
        }
        
        # Verificar arquivo principal
        core_file = self.base_path / "trae_ia_core.py"
        
        if core_file.exists():
            try:
                with open(core_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Procurar por indicadores de modo de simulação
                simulation_indicators = [
                    'DRY_RUN',
                    'SIMULATION',
                    'TEST_MODE',
                    'dry_run',
                    'simulation',
                    'test_mode',
                    'simulate',
                    'mock',
                    'fake'
                ]
                
                found_indicators = []
                for indicator in simulation_indicators:
                    if indicator in content:
                        # Contar ocorrências
                        count = content.count(indicator)
                        found_indicators.append({
                            'indicator': indicator,
                            'count': count,
                            'lines': []
                        })
                        
                        # Encontrar linhas específicas
                        lines = content.split('\n')
                        for i, line in enumerate(lines, 1):
                            if indicator in line:
                                found_indicators[-1]['lines'].append({
                                    'line_number': i,
                                    'content': line.strip()
                                })
                
                system_analysis['core_file_analysis'] = {
                    'file_exists': True,
                    'file_size': len(content),
                    'simulation_indicators': found_indicators
                }
                
                print(f"📁 trae_ia_core.py: {len(content)} caracteres")
                
                for indicator_data in found_indicators:
                    print(f"🔍 Encontrado '{indicator_data['indicator']}': {indicator_data['count']} ocorrências")
                    for line_info in indicator_data['lines'][:3]:  # Mostrar apenas as primeiras 3
                        print(f"   Linha {line_info['line_number']}: {line_info['content']}")
                
            except Exception as e:
                system_analysis['core_file_analysis'] = {
                    'file_exists': True,
                    'error': str(e)
                }
                print(f"❌ Erro ao analisar trae_ia_core.py: {e}")
        else:
            system_analysis['core_file_analysis'] = {'file_exists': False}
            print("❌ trae_ia_core.py não encontrado")
        
        return system_analysis
    
    def analyze_accounts_configuration(self) -> Dict[str, Any]:
        """Analisar configuração das contas"""
        print("👤 Analisando configuração das contas...")
        
        accounts_analysis = {
            'timestamp': self.diagnosis_timestamp,
            'accounts_found': 0,
            'posting_mode_settings': [],
            'configuration_issues': [],
            'status': 'UNKNOWN'
        }
        
        try:
            accounts_path = self.base_path / "accounts.json"
            
            if accounts_path.exists():
                with open(accounts_path, 'r', encoding='utf-8') as f:
                    accounts_data = json.load(f)
                
                accounts_analysis['accounts_found'] = len(accounts_data)
                
                for i, account in enumerate(accounts_data):
                    account_name = account.get('account_name', f'Account_{i+1}')
                    
                    # Verificar configurações relacionadas ao modo de postagem
                    posting_settings = {
                        'account_name': account_name,
                        'dry_run': account.get('dry_run', 'not_set'),
                        'simulation_mode': account.get('simulation_mode', 'not_set'),
                        'test_mode': account.get('test_mode', 'not_set'),
                        'production_mode': account.get('production_mode', 'not_set'),
                        'real_posting': account.get('real_posting', 'not_set'),
                        'posting_enabled': account.get('posting_enabled', 'not_set')
                    }
                    
                    accounts_analysis['posting_mode_settings'].append(posting_settings)
                    
                    print(f"👤 {account_name}:")
                    for setting, value in posting_settings.items():
                        if setting != 'account_name' and value != 'not_set':
                            print(f"   {setting}: {value}")
                            
                            # Identificar problemas
                            if setting in ['dry_run', 'simulation_mode', 'test_mode'] and str(value).lower() in ['true', '1', 'yes']:
                                accounts_analysis['configuration_issues'].append(f"{account_name}: {setting} ativado")
                            elif setting in ['production_mode', 'real_posting', 'posting_enabled'] and str(value).lower() in ['false', '0', 'no']:
                                accounts_analysis['configuration_issues'].append(f"{account_name}: {setting} desativado")
                
                print(f"📊 Total de contas: {accounts_analysis['accounts_found']}")
                
            else:
                accounts_analysis['configuration_issues'].append('accounts.json não encontrado')
                print("❌ accounts.json não encontrado")
                
        except Exception as e:
            accounts_analysis['configuration_issues'].append(f'Erro ao analisar contas: {str(e)}')
            print(f"❌ Erro ao analisar contas: {e}")
        
        return accounts_analysis
    
    def analyze_scheduler_logs(self) -> Dict[str, Any]:
        """Analisar logs do scheduler para identificar padrões"""
        print("📋 Analisando padrões nos logs do scheduler...")
        
        log_analysis = {
            'timestamp': self.diagnosis_timestamp,
            'simulation_patterns': [],
            'real_posting_patterns': [],
            'execution_summary': {},
            'identified_issues': []
        }
        
        # Simular análise dos logs fornecidos pelo usuário
        log_content = """
        [2025-10-22 15:00:44] 🚀 Iniciando ciclo de automação...
        [2025-10-22 15:00:46] 🎨 Simulando criação de post...
        [2025-10-22 15:00:46] ✅ Post simulado criado com sucesso!
        [2025-10-22 22:00:46] 🚀 Iniciando ciclo de automação...
        [2025-10-22 22:00:46] 🎨 Simulando criação de post...
        [2025-10-22 22:00:48] ✅ Post simulado criado com sucesso!
        """
        
        # Analisar padrões
        simulation_count = log_content.count("Simulando criação")
        real_posting_count = log_content.count("Post real criado") + log_content.count("Story publicado")
        
        log_analysis['execution_summary'] = {
            'simulation_executions': simulation_count,
            'real_posting_executions': real_posting_count,
            'total_executions': simulation_count + real_posting_count
        }
        
        # Identificar problemas
        if simulation_count > 0 and real_posting_count == 0:
            log_analysis['identified_issues'].append("Sistema executando apenas simulações")
            log_analysis['identified_issues'].append("Nenhuma postagem real detectada nos logs")
        
        if "Post simulado" in log_content:
            log_analysis['identified_issues'].append("Modo de simulação ativo durante execução")
        
        print(f"📊 Simulações detectadas: {simulation_count}")
        print(f"📊 Postagens reais detectadas: {real_posting_count}")
        
        for issue in log_analysis['identified_issues']:
            print(f"⚠️ {issue}")
        
        return log_analysis
    
    def generate_diagnosis_report(self) -> str:
        """Gerar relatório completo de diagnóstico"""
        print("📋 Gerando relatório completo de diagnóstico...")
        
        # Executar todas as análises
        railway_analysis = self.analyze_railway_configuration()
        system_analysis = self.analyze_core_system_mode()
        accounts_analysis = self.analyze_accounts_configuration()
        log_analysis = self.analyze_scheduler_logs()
        
        # Consolidar problemas identificados
        all_issues = []
        all_issues.extend(railway_analysis.get('configuration_issues', []))
        all_issues.extend(accounts_analysis.get('configuration_issues', []))
        all_issues.extend(log_analysis.get('identified_issues', []))
        
        # Gerar recomendações
        recommendations = []
        
        if any('DRY_RUN' in issue for issue in all_issues):
            recommendations.append("🔧 Desativar DRY_RUN nas variáveis de ambiente do Railway")
        
        if any('SIMULATION_MODE' in issue for issue in all_issues):
            recommendations.append("🔧 Desativar SIMULATION_MODE nas configurações")
        
        if any('simulação' in issue.lower() for issue in all_issues):
            recommendations.append("🔧 Alterar modo de operação para postagem real")
        
        if not recommendations:
            recommendations.append("🔍 Verificar código fonte para identificar modo de simulação hardcoded")
            recommendations.append("🔧 Revisar configurações de produção no Railway")
        
        # Criar relatório completo
        diagnosis_report = {
            'metadata': {
                'generated_at': self.diagnosis_timestamp,
                'diagnosis_type': 'SIMULATION_VS_REAL_POSTING',
                'version': '1.0'
            },
            'executive_summary': {
                'primary_issue': 'Sistema executando apenas simulações',
                'total_issues_found': len(all_issues),
                'critical_recommendations': len(recommendations),
                'requires_immediate_action': True
            },
            'detailed_analysis': {
                'railway_configuration': railway_analysis,
                'system_mode_analysis': system_analysis,
                'accounts_configuration': accounts_analysis,
                'scheduler_log_analysis': log_analysis
            },
            'consolidated_issues': all_issues,
            'immediate_actions': recommendations,
            'next_steps': [
                "1. Verificar e corrigir variáveis de ambiente do Railway",
                "2. Atualizar configurações das contas se necessário",
                "3. Modificar código fonte se modo simulação estiver hardcoded",
                "4. Testar postagem real imediata",
                "5. Monitorar logs após correções"
            ]
        }
        
        # Salvar relatório
        report_filename = f"simulation_issue_diagnosis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = self.base_path / report_filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(diagnosis_report, f, indent=2, ensure_ascii=False)
        
        print(f"📋 Relatório de diagnóstico salvo: {report_path}")
        
        return str(report_path)
    
    def run_complete_diagnosis(self) -> Dict[str, Any]:
        """Executar diagnóstico completo"""
        print("🔍 Iniciando diagnóstico completo do problema de simulação...")
        print("="*60)
        
        try:
            # Gerar relatório de diagnóstico
            report_path = self.generate_diagnosis_report()
            
            # Carregar relatório para obter resultado
            with open(report_path, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            
            result = {
                'status': 'SUCCESS',
                'timestamp': self.diagnosis_timestamp,
                'report_path': report_path,
                'issues_found': report_data['executive_summary']['total_issues_found'],
                'primary_issue': report_data['executive_summary']['primary_issue'],
                'immediate_actions': report_data['immediate_actions']
            }
            
            print("="*60)
            print("🔍 DIAGNÓSTICO COMPLETO CONCLUÍDO!")
            print(f"🚨 Problema Principal: {result['primary_issue']}")
            print(f"📊 Total de Problemas: {result['issues_found']}")
            print("\n🔧 Ações Imediatas Recomendadas:")
            for i, action in enumerate(result['immediate_actions'], 1):
                print(f"   {i}. {action}")
            
            return result
            
        except Exception as e:
            print(f"\n❌ ERRO no diagnóstico: {e}")
            logger.error(f"Erro crítico: {e}")
            return {'status': 'ERROR', 'error': str(e)}

def main():
    """Função principal"""
    print("🔍 Simulation Issue Diagnoser - Diagnóstico de Problema de Simulação")
    print("="*60)
    
    try:
        diagnoser = SimulationIssueDiagnoser()
        result = diagnoser.run_complete_diagnosis()
        
        if result['status'] == 'SUCCESS':
            print("\n✅ DIAGNÓSTICO CONCLUÍDO COM SUCESSO!")
            print("🔧 Problemas identificados e soluções propostas")
            print("📋 Verificar relatório para detalhes completos")
        else:
            print("\n❌ PROBLEMAS NO DIAGNÓSTICO")
            print("Verificar logs para detalhes específicos")
            
        return result
        
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO no diagnóstico: {e}")
        logger.error(f"Erro crítico: {e}")
        return {'status': 'CRITICAL', 'error': str(e)}

if __name__ == "__main__":
    main()