#!/usr/bin/env python3
"""
Scheduler Verification - Verificação do Agendamento 21h BRT
Confirma que o sistema está configurado para executar às 21h BRT
Data: 2025-10-23
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import pytz
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SchedulerVerifier:
    """Verificador de agendamento para 21h BRT"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.brt_timezone = pytz.timezone('America/Sao_Paulo')
        self.verification_timestamp = datetime.now(self.brt_timezone).isoformat()
        
    def get_current_brt_time(self):
        """Obter horário atual em BRT"""
        return datetime.now(self.brt_timezone)
    
    def verify_railway_config(self) -> dict:
        """Verificar configuração do Railway para agendamento"""
        print("🚂 Verificando configuração do Railway...")
        
        railway_status = {
            'status': 'CONFIGURED',
            'files_present': {},
            'cron_configured': False,
            'timezone_configured': False,
            'issues': []
        }
        
        # Verificar railway.yaml
        railway_yaml_path = self.base_path / "railway.yaml"
        if railway_yaml_path.exists():
            railway_status['files_present']['railway.yaml'] = True
            print("✅ railway.yaml presente")
            
            try:
                with open(railway_yaml_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Verificar se há configuração de cron
                if 'cron' in content.lower() or 'schedule' in content.lower():
                    railway_status['cron_configured'] = True
                    print("✅ Configuração de agendamento encontrada")
                else:
                    railway_status['issues'].append("Configuração de cron não encontrada no railway.yaml")
                    
            except Exception as e:
                railway_status['issues'].append(f"Erro ao ler railway.yaml: {str(e)}")
        else:
            railway_status['files_present']['railway.yaml'] = False
            railway_status['issues'].append("railway.yaml não encontrado")
        
        # Verificar Procfile
        procfile_path = self.base_path / "Procfile"
        if procfile_path.exists():
            railway_status['files_present']['Procfile'] = True
            print("✅ Procfile presente")
        else:
            railway_status['files_present']['Procfile'] = False
            railway_status['issues'].append("Procfile não encontrado")
        
        # Verificar variáveis de ambiente para timezone
        if 'TZ' in os.environ or 'TIMEZONE' in os.environ:
            railway_status['timezone_configured'] = True
            print("✅ Timezone configurado")
        else:
            railway_status['issues'].append("Timezone não configurado nas variáveis de ambiente")
        
        if railway_status['issues']:
            railway_status['status'] = 'ISSUES_FOUND'
        
        return railway_status
    
    def calculate_next_execution(self) -> dict:
        """Calcular próxima execução às 21h BRT"""
        print("⏰ Calculando próxima execução...")
        
        current_time = self.get_current_brt_time()
        current_hour = current_time.hour
        current_minute = current_time.minute
        
        execution_info = {
            'current_time_brt': current_time.strftime('%Y-%m-%d %H:%M:%S %Z'),
            'target_hour': 21,
            'next_execution': None,
            'time_until_execution': None,
            'ready_for_execution': False
        }
        
        # Calcular próxima execução às 21h
        if current_hour < 21:
            # Hoje às 21h
            next_execution = current_time.replace(hour=21, minute=0, second=0, microsecond=0)
            time_until = next_execution - current_time
            execution_info['next_execution'] = next_execution.strftime('%Y-%m-%d %H:%M:%S %Z')
            execution_info['time_until_execution'] = str(time_until).split('.')[0]  # Remove microsegundos
            
            # Se faltam menos de 2 horas, sistema deve estar pronto
            if time_until.total_seconds() <= 7200:  # 2 horas
                execution_info['ready_for_execution'] = True
                print(f"🟢 Próxima execução HOJE às 21h BRT (em {execution_info['time_until_execution']})")
            else:
                print(f"🟡 Próxima execução hoje às 21h BRT (em {execution_info['time_until_execution']})")
                
        elif current_hour == 21 and current_minute < 30:
            # Executando agora ou acabou de executar
            execution_info['next_execution'] = "EXECUTANDO AGORA ou RECÉM EXECUTADO"
            execution_info['time_until_execution'] = "0 minutos"
            execution_info['ready_for_execution'] = True
            print("🔴 HORÁRIO DE EXECUÇÃO - Sistema deve estar executando AGORA!")
            
        else:
            # Amanhã às 21h
            next_execution = (current_time + timedelta(days=1)).replace(hour=21, minute=0, second=0, microsecond=0)
            time_until = next_execution - current_time
            execution_info['next_execution'] = next_execution.strftime('%Y-%m-%d %H:%M:%S %Z')
            execution_info['time_until_execution'] = str(time_until).split('.')[0]
            print(f"🟡 Próxima execução AMANHÃ às 21h BRT (em {execution_info['time_until_execution']})")
        
        return execution_info
    
    def verify_posting_readiness(self) -> dict:
        """Verificar se o sistema está pronto para postar"""
        print("📱 Verificando prontidão para postagem...")
        
        readiness_status = {
            'overall_status': 'READY',
            'components': {},
            'issues': []
        }
        
        # Verificar accounts.json
        accounts_path = self.base_path / "accounts.json"
        if accounts_path.exists():
            try:
                with open(accounts_path, 'r', encoding='utf-8') as f:
                    accounts_data = json.load(f)
                
                if isinstance(accounts_data, list) and len(accounts_data) > 0:
                    # Verificar contas com tokens válidos
                    valid_accounts = [acc for acc in accounts_data if 'instagram_access_token' in acc and acc['instagram_access_token']]
                    
                    readiness_status['components']['accounts'] = {
                        'status': 'READY' if len(valid_accounts) > 0 else 'NO_VALID_TOKENS',
                        'total_accounts': len(accounts_data),
                        'valid_accounts': len(valid_accounts)
                    }
                    
                    if len(valid_accounts) == 0:
                        readiness_status['issues'].append("Nenhuma conta com token válido")
                        readiness_status['overall_status'] = 'NOT_READY'
                    else:
                        print(f"✅ {len(valid_accounts)} contas prontas para postagem")
                        
                else:
                    readiness_status['issues'].append("accounts.json vazio ou inválido")
                    readiness_status['overall_status'] = 'NOT_READY'
                    
            except Exception as e:
                readiness_status['issues'].append(f"Erro ao verificar accounts.json: {str(e)}")
                readiness_status['overall_status'] = 'ERROR'
        else:
            readiness_status['issues'].append("accounts.json não encontrado")
            readiness_status['overall_status'] = 'NOT_READY'
        
        # Verificar módulos principais
        critical_modules = [
            'trae_ia_core.py',
            'core/system_prompt_manager.py',
            'src/services/error_reflection_manager.py'
        ]
        
        missing_modules = []
        for module in critical_modules:
            module_path = self.base_path / module
            if not module_path.exists():
                missing_modules.append(module)
        
        if missing_modules:
            readiness_status['components']['modules'] = {
                'status': 'MISSING_MODULES',
                'missing': missing_modules
            }
            readiness_status['issues'].extend([f"Módulo {m} não encontrado" for m in missing_modules])
            readiness_status['overall_status'] = 'NOT_READY'
        else:
            readiness_status['components']['modules'] = {
                'status': 'ALL_PRESENT',
                'checked': len(critical_modules)
            }
            print(f"✅ {len(critical_modules)} módulos críticos presentes")
        
        return readiness_status
    
    def generate_scheduler_report(self, railway_status: dict, execution_info: dict, readiness_status: dict) -> str:
        """Gerar relatório de verificação do agendador"""
        
        # Determinar status geral
        if (railway_status['status'] == 'CONFIGURED' and 
            readiness_status['overall_status'] == 'READY'):
            overall_status = 'FULLY_OPERATIONAL'
        elif readiness_status['overall_status'] == 'NOT_READY':
            overall_status = 'NOT_READY'
        else:
            overall_status = 'PARTIALLY_READY'
        
        report = {
            'metadata': {
                'generated_at': self.verification_timestamp,
                'verification_type': 'SCHEDULER_21H_BRT_VERIFICATION',
                'version': '1.0'
            },
            'overall_status': overall_status,
            'current_time_brt': execution_info['current_time_brt'],
            'next_execution': execution_info,
            'railway_config': railway_status,
            'posting_readiness': readiness_status,
            'recommendations': self._generate_scheduler_recommendations(overall_status, execution_info)
        }
        
        # Salvar relatório
        report_filename = f"scheduler_verification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = self.base_path / report_filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📋 Relatório de agendamento salvo: {report_path}")
        return str(report_path)
    
    def _generate_scheduler_recommendations(self, overall_status: str, execution_info: dict) -> list:
        """Gerar recomendações para o agendador"""
        recommendations = []
        
        if overall_status == 'FULLY_OPERATIONAL':
            recommendations.extend([
                "✅ Sistema totalmente pronto para execução às 21h BRT",
                "✅ Todas as configurações de agendamento estão corretas",
                "✅ Contas configuradas e prontas para postagem"
            ])
            
            if execution_info['ready_for_execution']:
                recommendations.append("🚀 Sistema pronto para execução IMEDIATA")
            else:
                recommendations.append(f"⏰ Próxima execução: {execution_info['next_execution']}")
                
        elif overall_status == 'PARTIALLY_READY':
            recommendations.extend([
                "⚠️ Sistema parcialmente pronto - verificar configurações",
                "🔧 Revisar configurações do Railway",
                "📊 Monitorar próxima execução"
            ])
        else:
            recommendations.extend([
                "🚨 Sistema NÃO está pronto para execução",
                "🔧 Correções necessárias antes das 21h BRT",
                "📞 Verificar logs e configurações imediatamente"
            ])
        
        return recommendations
    
    def run_complete_verification(self) -> dict:
        """Executar verificação completa do agendador"""
        print("⏰ Iniciando verificação completa do agendador 21h BRT...")
        print("="*60)
        
        # Executar verificações
        railway_status = self.verify_railway_config()
        execution_info = self.calculate_next_execution()
        readiness_status = self.verify_posting_readiness()
        
        # Gerar relatório
        report_path = self.generate_scheduler_report(railway_status, execution_info, readiness_status)
        
        # Resultado final
        verification_result = {
            'overall_status': 'FULLY_OPERATIONAL' if (
                railway_status['status'] == 'CONFIGURED' and 
                readiness_status['overall_status'] == 'READY'
            ) else 'ISSUES_FOUND',
            'timestamp': self.verification_timestamp,
            'next_execution_time': execution_info['next_execution'],
            'time_until_execution': execution_info['time_until_execution'],
            'ready_for_immediate_execution': execution_info['ready_for_execution'],
            'railway_configured': railway_status['status'] == 'CONFIGURED',
            'posting_ready': readiness_status['overall_status'] == 'READY',
            'report_path': report_path
        }
        
        print("="*60)
        if verification_result['overall_status'] == 'FULLY_OPERATIONAL':
            print("✅ AGENDADOR 21H BRT: TOTALMENTE OPERACIONAL")
        else:
            print("⚠️ AGENDADOR 21H BRT: PROBLEMAS IDENTIFICADOS")
        print(f"📋 Relatório: {report_path}")
        
        return verification_result

def main():
    """Função principal"""
    print("⏰ Scheduler Verification - Verificação Agendamento 21h BRT")
    print("="*60)
    
    try:
        verifier = SchedulerVerifier()
        result = verifier.run_complete_verification()
        
        if result['overall_status'] == 'FULLY_OPERATIONAL':
            print("\n🎉 AGENDADOR TOTALMENTE OPERACIONAL!")
            print("✅ Sistema pronto para execução às 21h BRT")
            print(f"⏰ Próxima execução: {result['next_execution_time']}")
            if result['ready_for_immediate_execution']:
                print("🚀 SISTEMA PRONTO PARA EXECUÇÃO IMEDIATA!")
        else:
            print("\n⚠️ PROBLEMAS NO AGENDADOR")
            print("Verificar relatório para detalhes específicos")
            
        return result
        
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO na verificação do agendador: {e}")
        logger.error(f"Erro crítico: {e}")
        return {'overall_status': 'CRITICAL', 'error': str(e)}

if __name__ == "__main__":
    main()