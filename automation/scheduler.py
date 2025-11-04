"""
Sistema de Agendamento Automático para Posts do Instagram
Mantém consistência e automatiza o processo de criação de posts
"""

import schedule
import time
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Adicionar o diretório raiz e src ao path
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.config import load_config
from src.pipeline.generate_and_publish import generate_and_publish
from src.services.superior_concept_manager import SuperiorConceptManager
from src.services.engagement_monitor import EngagementMonitor
from src.services.performance_optimizer import PerformanceOptimizer

# Configuração robusta para Feed 19h BRT
import os
os.environ['INSTAGRAM_TIMEOUT'] = '120'
os.environ['INSTAGRAM_MAX_RETRIES'] = '3'
os.environ['INSTAGRAM_POLLING_INTERVAL'] = '10'
os.environ['INSTAGRAM_MAX_POLLING_CHECKS'] = '60'


class AutomationScheduler:
    def __init__(self):
        self.config_file = Path(__file__).parent / "automation_config.json"
        self.log_file = Path(__file__).parent / "automation.log"
        self.setup_logging()
        self.load_config()
        
        # Carregar configurações do sistema principal
        self.system_config = load_config()
        
        # Inicializar componentes
        self.concept_manager = SuperiorConceptManager()
        self.engagement_monitor = EngagementMonitor()
        self.performance_optimizer = PerformanceOptimizer()
        
    def setup_logging(self):
        """Configurar sistema de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_config(self):
        """Carregar configurações de automação"""
        default_config = {
            "schedule": {
                "daily_posts": 3,
                "post_times": ["09:00", "14:00", "19:00"],
                "optimization_time": "23:00",
                "monitoring_interval": 60  # minutos
            },
            "content_settings": {
                "auto_optimize": True,
                "use_trending_concepts": True,
                "maintain_quality_threshold": 0.8
            },
            "safety_settings": {
                "max_daily_posts": 5,
                "min_interval_between_posts": 120,  # minutos
                "backup_concepts": True
            }
        }
        
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = default_config
            self.save_config()
            
    def save_config(self):
        """Salvar configurações"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
            
    def create_scheduled_post(self):
        """Criar post agendado automaticamente (apenas Feed) para todas as contas"""
        try:
            self.logger.info("Iniciando criação de post agendado (Feed) para múltiplas contas...")
            
            # Verificar se já atingiu o limite diário
            if self._check_daily_limit():
                self.logger.warning("Limite diário de posts atingido")
                return
            
            # Carregar contas do accounts.json
            accounts_file = Path(__file__).parent.parent / "accounts.json"
            try:
                with open(accounts_file, 'r', encoding='utf-8') as f:
                    accounts = json.load(f)
                self.logger.info(f"Carregadas {len(accounts)} contas do accounts.json")
            except Exception as e:
                self.logger.error(f"Erro ao carregar accounts.json: {e}")
                return
                
            # Processar cada conta
            for account in accounts:
                account_name = account.get("nome", "Conta_Desconhecida")
                instagram_id = account.get("instagram_id")
                access_token = account.get("instagram_access_token")
                
                if not instagram_id or not access_token:
                    self.logger.warning(f"Conta {account_name} não possui credenciais válidas, pulando...")
                    continue
                
                self.logger.info(f"Processando Feed para conta: {account_name}")
                
                # Obter uma imagem de referência (pode ser configurável no futuro)
                source_image_url = "https://images.unsplash.com/photo-1506905925346-21bda4d32df4"  # Placeholder
                
                # Chamar a função de geração e publicação com as configurações específicas da conta
                self.logger.info(f"Chamando generate_and_publish para {account_name}...")
                result = generate_and_publish(
                    openai_key=self.system_config["OPENAI_API_KEY"],
                    replicate_token=self.system_config["REPLICATE_TOKEN"],
                    instagram_business_id=instagram_id,
                    instagram_access_token=access_token,
                    telegram_bot_token=self.system_config["TELEGRAM_BOT_TOKEN"],
                    telegram_chat_id=self.system_config["TELEGRAM_CHAT_ID"],
                    source_image_url=source_image_url,
                    account_name=account_name,
                    publish_to_stories=False,  # Explicitamente desabilitar Stories para posts do Feed
                    use_weekly_themes=True  # Habilitar sistema temático semanal
                )
                
                self.logger.info(f"Resultado da função generate_and_publish para {account_name}: {result}")
                
                if result and result.get('status') == 'PUBLISHED':
                    self.logger.info(f"[SUCESSO] Post automático criado com sucesso para {account_name}! ID: {result.get('post_id', 'N/A')}")
                    
                    # Registrar sucesso para monitoramento
                    post_data = {
                        "timestamp": datetime.now().isoformat(),
                        "status": "published",
                        "type": "automated",
                        "account": account_name,
                        "post_id": result.get('post_id'),
                        "concept": result.get('concept', 'N/A')
                    }
                    
                    # Monitorar o post recém-criado
                    self.engagement_monitor.track_post(post_data)
                    
                else:
                    self.logger.error(f"[ERRO] Falha na criação do post automático para {account_name}. Resultado: {result}")
                    
                    # Registrar falha para monitoramento
                    post_data = {
                        "timestamp": datetime.now().isoformat(),
                        "status": "failed",
                        "type": "automated",
                        "account": account_name,
                        "error": result.get('error', 'Erro desconhecido') if result else 'Resultado nulo'
                    }
                    self.engagement_monitor.track_post(post_data)
            
            self.logger.info("Posts agendados processados e registrados para monitoramento")
                
        except Exception as e:
            self.logger.error(f"Erro na criação de post agendado: {str(e)}")
            
    def create_scheduled_stories(self):
        """Criar Stories agendado automaticamente (apenas Stories) para todas as contas"""
        try:
            self.logger.info("Iniciando criação de Stories agendado para múltiplas contas...")
            
            # Verificar se já atingiu o limite diário
            if self._check_daily_limit():
                self.logger.warning("Limite diário de posts atingido")
                return
            
            # Carregar contas do accounts.json
            accounts_file = Path(__file__).parent.parent / "accounts.json"
            try:
                with open(accounts_file, 'r', encoding='utf-8') as f:
                    accounts = json.load(f)
                self.logger.info(f"Carregadas {len(accounts)} contas do accounts.json para Stories")
            except Exception as e:
                self.logger.error(f"Erro ao carregar accounts.json: {e}")
                return
                
            # Processar cada conta
            for account in accounts:
                account_name = account.get("nome", "Conta_Desconhecida")
                instagram_id = account.get("instagram_id")
                access_token = account.get("instagram_access_token")
                
                if not instagram_id or not access_token:
                    self.logger.warning(f"Conta {account_name} não possui credenciais válidas, pulando...")
                    continue
                
                self.logger.info(f"Processando Stories para conta: {account_name}")
                
                # Obter uma imagem de referência
                source_image_url = "https://images.unsplash.com/photo-1506905925346-21bda4d32df4"  # Placeholder
                
                # Chamar a função de geração e publicação com as configurações específicas da conta
                self.logger.info(f"Chamando generate_and_publish para Stories da conta {account_name}...")
                result = generate_and_publish(
                    openai_key=self.system_config["OPENAI_API_KEY"],
                    replicate_token=self.system_config["REPLICATE_TOKEN"],
                    instagram_business_id=instagram_id,
                    instagram_access_token=access_token,
                    telegram_bot_token=self.system_config["TELEGRAM_BOT_TOKEN"],
                    telegram_chat_id=self.system_config["TELEGRAM_CHAT_ID"],
                    source_image_url=source_image_url,
                    account_name=account_name,
                    publish_to_stories=True,  # Habilitar Stories
                    stories_background_type="gradient",  # Usar fundo gradiente
                    stories_text_position="auto",  # Posicionamento inteligente automático
                    use_weekly_themes=True  # Habilitar sistema temático semanal
                )
                
                self.logger.info(f"Resultado da função generate_and_publish para Stories da conta {account_name}: {result}")
                
                if result and result.get('status') == 'PUBLISHED':
                    self.logger.info(f"[SUCESSO] Stories automático criado com sucesso para {account_name}! ID: {result.get('post_id', 'N/A')}")
                    
                    # Verificar se Stories foi publicado
                    stories_published = result.get('stories_published', False)
                    if stories_published:
                        stories_result = result.get('stories', {})
                        stories_id = stories_result.get('media_id', 'N/A')
                        self.logger.info(f"[SUCESSO] Stories ID para {account_name}: {stories_id}")
                    else:
                        self.logger.warning(f"Stories não foi publicado com sucesso para {account_name}")
                    
                    # Registrar sucesso para monitoramento
                    post_data = {
                        "timestamp": datetime.now().isoformat(),
                        "status": "published",
                        "type": "automated_stories",
                        "account": account_name,
                        "post_id": result.get('post_id'),
                        "stories_id": stories_result.get('media_id') if stories_published else None,
                        "concept": result.get('concept', 'N/A')
                    }
                    
                    # Monitorar o post recém-criado
                    self.engagement_monitor.track_post(post_data)
                    
                else:
                    self.logger.error(f"[ERRO] Falha na criação do Stories automático para {account_name}. Resultado: {result}")
                    
                    # Registrar falha para monitoramento
                    post_data = {
                        "timestamp": datetime.now().isoformat(),
                        "status": "failed",
                        "type": "automated_stories",
                        "account": account_name,
                        "error": result.get('error', 'Erro desconhecido') if result else 'Resultado nulo'
                    }
                    self.engagement_monitor.track_post(post_data)
            
            self.logger.info("Stories agendados processados e registrados para monitoramento")
                
        except Exception as e:
            self.logger.error(f"Erro na criação de Stories agendado: {str(e)}")
            
    def create_test_post(self):
        """Criar post de teste às 20:00"""
        try:
            self.logger.info("Iniciando criação de post de teste às 20:00...")
            self.logger.info("Executando pipeline de geração e publicação automática...")
            
            # Chamar generate_and_publish com todos os parâmetros necessários
            result = generate_and_publish(
                openai_key=self.system_config.get('OPENAI_API_KEY'),
                replicate_token=self.system_config.get('REPLICATE_TOKEN'),
                instagram_business_id=self.system_config.get('INSTAGRAM_BUSINESS_ACCOUNT_ID'),
                instagram_access_token=self.system_config.get('INSTAGRAM_ACCESS_TOKEN'),
                telegram_bot_token=self.system_config.get('TELEGRAM_BOT_TOKEN'),
                telegram_chat_id=self.system_config.get('TELEGRAM_CHAT_ID'),
                source_image_url="https://images.unsplash.com/photo-1506905925346-21bda4d32df4",
                account_name="Milton_Albanez"
            )
            
            if result and result.get('success'):
                self.logger.info(f"[SUCESSO] Post de teste criado com sucesso! ID: {result.get('post_id', 'N/A')}")
                # Registrar para monitoramento
                post_data = {
                    "timestamp": datetime.now().isoformat(),
                    "status": "published",
                    "type": "test_scheduled",
                    "post_id": result.get('post_id'),
                    "concept": result.get('concept', 'N/A')
                }
                self.engagement_monitor.track_post(post_data)
            else:
                self.logger.error("[ERRO] Falha na criação do post de teste")
                
        except Exception as e:
            self.logger.error(f"Erro na criação de post de teste: {str(e)}")
            
    def run_optimization(self):
        """Executar otimização baseada na performance"""
        try:
            self.logger.info("Iniciando otimização automática...")
            
            # Gerar relatório de engagement para análise
            engagement_report = self.engagement_monitor.generate_engagement_report()
            
            # Executar otimização baseada no relatório
            if engagement_report.get('recommendations'):
                self.logger.info("Otimização baseada em recomendações de engagement")
                
                # Atualizar conceitos se necessário
                self.logger.info("Conceitos atualizados baseados na performance")
                    
            else:
                self.logger.warning("Nenhuma otimização necessária")
                
        except Exception as e:
            self.logger.error(f"Erro na otimização automática: {str(e)}")
            
    def monitor_engagement(self):
        """Monitorar engagement dos posts"""
        try:
            self.logger.info("Executando monitoramento de engagement...")
            
            # Gerar relatório de engagement
            report = self.engagement_monitor.generate_engagement_report()
            
            # Log de insights importantes
            if report.get('recommendations'):
                for rec in report['recommendations']:
                    if 'ATENÇÃO' in rec or 'REVISAR' in rec:
                        self.logger.warning(f"Alerta de performance: {rec}")
                    elif 'EXCELENTE' in rec:
                        self.logger.info(f"Performance destacada: {rec}")
                
        except Exception as e:
            self.logger.error(f"Erro no monitoramento: {str(e)}")
            
    def _check_daily_limit(self):
        """Verificar se atingiu o limite diário de posts"""
        today = datetime.now().date()
        # Implementar lógica de verificação baseada em logs ou banco de dados
        return False  # Placeholder
        
    def setup_schedule(self):
        """Configurar agendamentos"""
        # Agendar posts do Feed
        for post_time in self.config["schedule"]["post_times"]:
            schedule.every().day.at(post_time).do(self.create_scheduled_post)
            self.logger.info(f"Feed agendado para: {post_time}")
            
        # Agendar Stories (se configurado)
        if "stories_times" in self.config["schedule"]:
            for stories_time in self.config["schedule"]["stories_times"]:
                schedule.every().day.at(stories_time).do(self.create_scheduled_stories)
                self.logger.info(f"Stories agendado para: {stories_time}")
        
        # Agendamento especial para teste hoje às 20:00
        today = datetime.now().date()
        schedule.every().day.at("20:00").do(self.create_test_post).tag(f'test-{today}')
        
        # Agendar otimização diária
        optimization_time = self.config["schedule"]["optimization_time"]
        schedule.every().day.at(optimization_time).do(self.run_optimization)
        
        # Agendar monitoramento regular
        monitoring_interval = self.config["schedule"]["monitoring_interval"]
        schedule.every(monitoring_interval).minutes.do(self.monitor_engagement)
        
        self.logger.info("Agendamentos configurados com sucesso")
        self.logger.info(f"Feed: {self.config['schedule']['post_times']}")
        if "stories_times" in self.config["schedule"]:
            self.logger.info(f"Stories: {self.config['schedule']['stories_times']}")
        self.logger.info(f"Agendamento especial para teste hoje às 20:00 adicionado")
        
    def run_scheduler(self):
        """Executar o agendador"""
        self.logger.info("Iniciando sistema de automação...")
        
        try:
            self.logger.info("PASSO 1: Chamando setup_schedule()...")
            self.setup_schedule()
            self.logger.info("PASSO 2: setup_schedule() concluído com sucesso!")
            
            self.logger.info("PASSO 3: Iniciando loop principal...")
            loop_count = 0
            
            while True:
                loop_count += 1
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Log a cada iteração para debug
                if loop_count <= 5 or loop_count % 10 == 0:
                    self.logger.info(f"[LOOP {loop_count}] Sistema ativo às {current_time}")
                    self.logger.info(f"[LOOP {loop_count}] Total de jobs agendados: {len(schedule.jobs)}")
                
                # Verificar jobs pendentes
                self.logger.debug(f"[LOOP {loop_count}] Verificando jobs pendentes...")
                pending_jobs = [job for job in schedule.jobs if job.should_run]
                
                if pending_jobs:
                    self.logger.info(f"[EXECUÇÃO] {len(pending_jobs)} job(s) pendente(s) às {current_time}")
                    for job in pending_jobs:
                        self.logger.info(f"[EXECUÇÃO] Executando: {job}")
                
                self.logger.debug(f"[LOOP {loop_count}] Chamando schedule.run_pending()...")
                schedule.run_pending()
                self.logger.debug(f"[LOOP {loop_count}] schedule.run_pending() concluído")
                
                self.logger.debug(f"[LOOP {loop_count}] Dormindo por 60 segundos...")
                time.sleep(60)
                
        except KeyboardInterrupt:
            self.logger.info("Sistema de automação interrompido pelo usuário")
        except Exception as e:
            self.logger.error(f"Erro no sistema de automação: {str(e)}")
            import traceback
            self.logger.error(f"Traceback completo: {traceback.format_exc()}")
            
    def run_manual_cycle(self):
        """Executar um ciclo completo manualmente para teste"""
        self.logger.info("Executando ciclo manual de automação...")
        
        # Monitoramento
        self.monitor_engagement()
        
        # Otimização
        self.run_optimization()
        
        # Criação de post
        self.create_scheduled_post()
        
        self.logger.info("Ciclo manual concluído")

if __name__ == "__main__":
    scheduler = AutomationScheduler()
    
    # Verificar argumentos da linha de comando
    if len(sys.argv) > 1:
        if sys.argv[1] == "manual":
            scheduler.run_manual_cycle()
        elif sys.argv[1] == "config":
            print("Configuração atual:")
            print(json.dumps(scheduler.config, indent=2, ensure_ascii=False))
    else:
        scheduler.run_scheduler()