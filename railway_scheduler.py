#!/usr/bin/env python3
"""
Sistema de Agendamento Automático para Railway
Versão completa com múltiplas contas para funcionamento 24/7 na nuvem
"""

import os
import time
import schedule
import json
import logging
from datetime import datetime
from pathlib import Path
import sys

# Adicionar o diretório raiz e src ao path
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / "src"))

from src.config import load_config
from src.pipeline.generate_and_publish import generate_and_publish

class RailwayScheduler:
    def __init__(self):
        self.setup_logging()
        self.load_accounts()
        
    def setup_logging(self):
        """Configurar sistema de logging para Railway"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]  # Railway captura stdout
        )
        self.logger = logging.getLogger(__name__)
        
    def load_accounts(self):
        """Carregar contas do accounts.json"""
        try:
            accounts_file = Path(__file__).parent / "accounts.json"
            with open(accounts_file, 'r', encoding='utf-8') as f:
                self.accounts = json.load(f)
            self.logger.info(f"✅ Carregado accounts.json com {len(self.accounts)} contas")
            for account in self.accounts:
                self.logger.info(f"  📱 Conta: {account['nome']}")
        except Exception as e:
            self.logger.error(f"❌ Erro ao carregar accounts.json: {e}")
            self.accounts = []
    
    def check_environment(self):
        """Verificar se as variáveis de ambiente estão configuradas"""
        self.logger.info("🔍 Verificando variáveis de ambiente...")
        
        # Verificar variáveis básicas
        basic_vars = ['OPENAI_API_KEY', 'RAPIDAPI_KEY']
        missing_vars = []
        
        for var in basic_vars:
            if not os.getenv(var):
                missing_vars.append(var)
            else:
                self.logger.info(f"  ✅ {var} configurada")
        
        if missing_vars:
            self.logger.error(f"❌ Variáveis faltando: {missing_vars}")
            return False
        
        self.logger.info("✅ Variáveis básicas configuradas!")
        return True
    
    def create_scheduled_post(self):
        """Criar posts para todas as contas (Feed)"""
        self.logger.info("🎨 === INICIANDO CRIAÇÃO DE POSTS (FEED) ===")
        
        if not self.accounts:
            self.logger.error("❌ Nenhuma conta carregada!")
            return
        
        for account in self.accounts:
            try:
                account_name = account['nome']
                self.logger.info(f"📱 Processando conta: {account_name}")
                
                # Configurar variáveis de ambiente específicas da conta
                os.environ['INSTAGRAM_BUSINESS_ACCOUNT_ID'] = account['instagram_id']
                os.environ['INSTAGRAM_ACCESS_TOKEN'] = account['instagram_access_token']
                
                # Chamar generate_and_publish para Feed
                self.logger.info(f"🚀 Gerando post para {account_name}...")
                generate_and_publish(account_name=account_name, mode='feed')
                
                self.logger.info(f"✅ Post criado com sucesso para {account_name}")
                
            except Exception as e:
                self.logger.error(f"❌ Erro ao processar conta {account_name}: {e}")
    
    def create_scheduled_stories(self):
        """Criar stories para todas as contas"""
        self.logger.info("📱 === INICIANDO CRIAÇÃO DE STORIES ===")
        
        if not self.accounts:
            self.logger.error("❌ Nenhuma conta carregada!")
            return
        
        for account in self.accounts:
            try:
                account_name = account['nome']
                self.logger.info(f"📱 Processando conta: {account_name}")
                
                # Configurar variáveis de ambiente específicas da conta
                os.environ['INSTAGRAM_BUSINESS_ACCOUNT_ID'] = account['instagram_id']
                os.environ['INSTAGRAM_ACCESS_TOKEN'] = account['instagram_access_token']
                
                # Chamar generate_and_publish para Stories
                self.logger.info(f"🚀 Gerando stories para {account_name}...")
                generate_and_publish(account_name=account_name, mode='stories')
                
                self.logger.info(f"✅ Stories criado com sucesso para {account_name}")
                
            except Exception as e:
                self.logger.error(f"❌ Erro ao processar conta {account_name}: {e}")
    
    def setup_schedule(self):
        """Configurar agendamentos (horários em UTC para Railway)"""
        self.logger.info("📅 Configurando agendamentos...")
        
        # Horários em UTC (Railway usa UTC)
        # 6h BRT = 9h UTC, 12h BRT = 15h UTC, 19h BRT = 22h UTC
        # 9h BRT = 12h UTC, 15h BRT = 18h UTC, 21h BRT = 00h UTC (próximo dia)
        
        # Feed posts
        schedule.every().day.at("09:00").do(self.create_scheduled_post)  # 6h BRT
        schedule.every().day.at("15:00").do(self.create_scheduled_post)  # 12h BRT
        schedule.every().day.at("22:00").do(self.create_scheduled_post)  # 19h BRT
        
        # Stories
        schedule.every().day.at("12:00").do(self.create_scheduled_stories)  # 9h BRT
        schedule.every().day.at("18:00").do(self.create_scheduled_stories)  # 15h BRT
        schedule.every().day.at("00:00").do(self.create_scheduled_stories)  # 21h BRT
        
        self.logger.info("✅ Agendamentos configurados:")
        self.logger.info("📝 FEED:")
        self.logger.info("  - 09:00 UTC (06:00 BRT)")
        self.logger.info("  - 15:00 UTC (12:00 BRT)")
        self.logger.info("  - 22:00 UTC (19:00 BRT)")
        self.logger.info("📱 STORIES:")
        self.logger.info("  - 12:00 UTC (09:00 BRT)")
        self.logger.info("  - 18:00 UTC (15:00 BRT)")
        self.logger.info("  - 00:00 UTC (21:00 BRT)")
        
    def run(self):
        """Executar o agendador"""
        self.logger.info("🤖 RAILWAY SCHEDULER - Iniciando...")
        self.logger.info(f"🌍 Ambiente: {os.getenv('RAILWAY_ENVIRONMENT', 'railway')}")
        self.logger.info(f"⏰ Horário de início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        # Verificar ambiente
        if not self.check_environment():
            self.logger.error("❌ Ambiente não configurado corretamente")
            return
        
        # Configurar agendamentos
        self.setup_schedule()
        
        # Executar teste inicial (opcional)
        # self.logger.info("🔄 Executando teste inicial...")
        # self.create_scheduled_stories()
        
        self.logger.info("🔄 Entrando no loop principal...")
        self.logger.info(f"📋 Total de jobs agendados: {len(schedule.jobs)}")
        
        # Loop principal
        loop_count = 0
        while True:
            loop_count += 1
            
            # Log a cada 30 minutos
            if loop_count % 30 == 1:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
                self.logger.info(f"💓 Sistema ativo - Loop #{loop_count} - {current_time}")
                self.logger.info(f"📋 Jobs agendados: {len(schedule.jobs)}")
                if schedule.jobs:
                    self.logger.info(f"⏰ Próxima execução: {schedule.next_run()}")
            
            # Executar tarefas pendentes
            schedule.run_pending()
            
            # Aguardar 1 minuto
            time.sleep(60)

def main():
    """Função principal"""
    scheduler = RailwayScheduler()
    scheduler.run()

if __name__ == "__main__":
    main()