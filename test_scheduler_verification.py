#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 TESTE DE VERIFICAÇÃO DO AGENDADOR
Verifica se o agendador está configurado corretamente para todos os horários
"""

import os
import sys
import json
import time
from datetime import datetime, timezone, timedelta
import logging

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def print_header():
    logger.info("=" * 60)
    logger.info("🔍 TESTE DE VERIFICAÇÃO DO AGENDADOR")
    logger.info("=" * 60)
    
    # Horário atual
    utc_now = datetime.now(timezone.utc)
    brt_now = utc_now - timedelta(hours=3)  # UTC-3 = BRT
    
    logger.info(f"🕐 Horário atual: {brt_now.strftime('%H:%M:%S')} BRT")
    logger.info(f"🌍 UTC: {utc_now.strftime('%H:%M:%S')}")
    logger.info(f"📅 Data: {brt_now.strftime('%d/%m/%Y')}")
    logger.info("")

def test_stories_configuration():
    """Testa se a configuração de stories está correta"""
    logger.info("📱 TESTANDO CONFIGURAÇÃO DE STORIES...")
    
    try:
        # Importar o agendador
        from railway_scheduler import RailwayScheduler
        
        # Criar instância do agendador
        scheduler = RailwayScheduler()
        
        # Verificar se a função create_scheduled_stories está usando publish_to_stories=True
        logger.info("✅ Verificando função create_scheduled_stories...")
        
        # Testar a função create_scheduled_stories com uma conta de teste
        test_account = {
            'nome': 'Conta_Teste',
            'instagram_id': 'test_id',
            'instagram_access_token': 'test_token'
        }
        
        # Salvar a função original
        original_generate_and_publish = sys.modules.get('__main__').__dict__.get('generate_and_publish', None)
        
        # Criar uma função mock para generate_and_publish
        def mock_generate_and_publish(**kwargs):
            logger.info(f"Mock generate_and_publish chamado com: {kwargs}")
            # Verificar se publish_to_stories está presente e é True
            assert kwargs.get('publish_to_stories') is True, "publish_to_stories deve ser True para stories"
            return {"status": "MOCK_SUCCESS"}
        
        # Substituir a função original pela mock
        sys.modules['__main__'].__dict__['generate_and_publish'] = mock_generate_and_publish
        
        # Testar a função
        scheduler.accounts = [test_account]
        scheduler.create_scheduled_stories()
        
        logger.info("✅ Função create_scheduled_stories está configurada corretamente!")
        
        # Restaurar a função original
        if original_generate_and_publish:
            sys.modules['__main__'].__dict__['generate_and_publish'] = original_generate_and_publish
        
    except Exception as e:
        logger.error(f"❌ Erro ao testar configuração de stories: {e}")
        return False
    
    return True

def test_feed_configuration():
    """Testa se a configuração de feed está correta"""
    logger.info("📝 TESTANDO CONFIGURAÇÃO DE FEED...")
    
    try:
        # Importar o agendador
        from railway_scheduler import RailwayScheduler
        
        # Criar instância do agendador
        scheduler = RailwayScheduler()
        
        # Verificar se a função create_scheduled_post está usando publish_to_stories=False
        logger.info("✅ Verificando função create_scheduled_post...")
        
        # Testar a função create_scheduled_post com uma conta de teste
        test_account = {
            'nome': 'Conta_Teste',
            'instagram_id': 'test_id',
            'instagram_access_token': 'test_token'
        }
        
        # Salvar a função original
        original_generate_and_publish = sys.modules.get('__main__').__dict__.get('generate_and_publish', None)
        
        # Criar uma função mock para generate_and_publish
        def mock_generate_and_publish(**kwargs):
            logger.info(f"Mock generate_and_publish chamado com: {kwargs}")
            # Verificar se publish_to_stories está presente e é False
            assert kwargs.get('publish_to_stories') is False, "publish_to_stories deve ser False para feed"
            return {"status": "MOCK_SUCCESS"}
        
        # Substituir a função original pela mock
        sys.modules['__main__'].__dict__['generate_and_publish'] = mock_generate_and_publish
        
        # Testar a função
        scheduler.accounts = [test_account]
        scheduler.create_scheduled_post()
        
        logger.info("✅ Função create_scheduled_post está configurada corretamente!")
        
        # Restaurar a função original
        if original_generate_and_publish:
            sys.modules['__main__'].__dict__['generate_and_publish'] = original_generate_and_publish
        
    except Exception as e:
        logger.error(f"❌ Erro ao testar configuração de feed: {e}")
        return False
    
    return True

def test_railway_configuration():
    """Testa se a configuração do Railway está correta"""
    logger.info("🚂 TESTANDO CONFIGURAÇÃO DO RAILWAY...")
    
    try:
        import os
        from pathlib import Path
        
        # Verificar se o arquivo railway.yaml existe
        railway_yaml = Path(__file__).parent / "railway.yaml"
        railway_yaml_backup = Path(__file__).parent / "railway.yaml.backup"
        
        if railway_yaml.exists():
            with open(railway_yaml, 'r', encoding='utf-8') as f:
                railway_content = f.read()
        elif railway_yaml_backup.exists():
            with open(railway_yaml_backup, 'r', encoding='utf-8') as f:
                railway_content = f.read()
        else:
            logger.warning("⚠️ Arquivo railway.yaml não encontrado!")
            return False
        
        # Verificar se os horários de stories estão configurados corretamente
        stories_schedules = [
            "0 12 * * *",  # 09:00 BRT
            "0 18 * * *",  # 15:00 BRT
            "0 0 * * *"    # 21:00 BRT
        ]
        
        stories_commands = [
            "python src/main.py multirun --limit 1 --stories"
        ]
        
        all_stories_schedules_found = all(schedule in railway_content for schedule in stories_schedules)
        all_stories_commands_found = all(command in railway_content for command in stories_commands)
        
        if all_stories_schedules_found and all_stories_commands_found:
            logger.info("✅ Configuração de stories no Railway está correta!")
        else:
            logger.warning("⚠️ Configuração de stories no Railway pode estar incompleta!")
            return False
        
    except Exception as e:
        logger.error(f"❌ Erro ao testar configuração do Railway: {e}")
        return False
    
    return True

def generate_report(stories_ok, feed_ok, railway_ok):
    """Gera um relatório com os resultados dos testes"""
    logger.info("📊 GERANDO RELATÓRIO...")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "tests": {
            "stories_configuration": stories_ok,
            "feed_configuration": feed_ok,
            "railway_configuration": railway_ok
        },
        "overall_status": all([stories_ok, feed_ok, railway_ok]),
        "recommendations": []
    }
    
    if not stories_ok:
        report["recommendations"].append("Corrigir a função create_scheduled_stories para usar publish_to_stories=True")
    
    if not feed_ok:
        report["recommendations"].append("Corrigir a função create_scheduled_post para usar publish_to_stories=False")
    
    if not railway_ok:
        report["recommendations"].append("Verificar a configuração do Railway para garantir que todos os horários estejam configurados corretamente")
    
    # Salvar o relatório
    report_filename = f"scheduler_verification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    logger.info(f"📋 Relatório salvo em: {report_filename}")
    
    return report

def main():
    """Função principal"""
    print_header()
    
    # Testar configuração de stories
    stories_ok = test_stories_configuration()
    
    # Testar configuração de feed
    feed_ok = test_feed_configuration()
    
    # Testar configuração do Railway
    railway_ok = test_railway_configuration()
    
    # Gerar relatório
    report = generate_report(stories_ok, feed_ok, railway_ok)
    
    # Exibir resultado final
    if report["overall_status"]:
        logger.info("✅ TODOS OS TESTES PASSARAM! O sistema está configurado corretamente.")
    else:
        logger.warning("⚠️ ALGUNS TESTES FALHARAM! Verifique o relatório para mais detalhes.")
    
    return report["overall_status"]

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)