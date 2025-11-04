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
import requests

# Adicionar o diretório raiz e src ao path
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / "src"))

from src.config import load_config
from src.pipeline.generate_and_publish import generate_and_publish
from health_server import HealthServer
from performance_monitor import performance_monitor, monitor_execution
from notification_system import notification_system

class RailwayScheduler:
    def __init__(self):
        self.setup_logging()
        self.load_accounts()
        self._preflight_summary = []
        
        # Inicializar health server
        port = int(os.getenv('PORT', 8000))
        self.health_server = HealthServer(port=port)
        self.health_server.start()
        
    def setup_logging(self):
        """Configurar sistema de logging aprimorado para Railway"""
        # Configuração de logging com mais detalhes e rotação
        log_format = '%(asctime)s - [%(levelname)s] - %(name)s - %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.StreamHandler(),  # Railway captura stdout
                # Adicionar handler de arquivo para logs locais se necessário
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Log de inicialização do sistema
        self.logger.info("[START] Sistema de Agendamento Automático Iniciado")
        self.logger.info(f"[TIME] Data/Hora de Inicialização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        self.logger.info(f"[TZ] Timezone: UTC (Railway padrão)")
        
        # Verificar variáveis de ambiente críticas
        self._check_environment_variables()
        
    def _check_environment_variables(self):
        """Verificar variáveis de ambiente críticas na inicialização"""
        self.logger.info("[CHECK] Verificando variáveis de ambiente críticas...")
        
        # Variáveis essenciais para funcionamento
        critical_vars = {
            'OPENAI_API_KEY': 'Geração de conteúdo com IA',
            'RAPIDAPI_KEY': 'Scraping de hashtags do Instagram',
        }
        
        # Variáveis opcionais mas importantes
        optional_vars = {
            'TELEGRAM_BOT_TOKEN': 'Notificações via Telegram',
            'TELEGRAM_CHAT_ID': 'Chat de destino das notificações',
            'REPLICATE_TOKEN': 'Geração de imagens com IA',
            'DATABASE_URL': 'Banco de dados PostgreSQL'
        }
        
        missing_critical = []
        missing_optional = []
        
        # Verificar variáveis críticas
        for var, description in critical_vars.items():
            if os.getenv(var):
                self.logger.info(f"  [OK] {var} - {description}")
            else:
                missing_critical.append(f"{var} ({description})")
                
        # Verificar variáveis opcionais
        for var, description in optional_vars.items():
            if os.getenv(var):
                self.logger.info(f"  ✅ {var} - {description}")
            else:
                missing_optional.append(f"{var} ({description})")
                
        # Reportar resultados
        if missing_critical:
            self.logger.error(f"[ERROR] Variáveis críticas faltando: {missing_critical}")
            self.logger.error("[WARNING] Sistema pode não funcionar corretamente!")
        else:
            self.logger.info("[OK] Todas as variáveis críticas estão configuradas")
            
        if missing_optional:
            self.logger.warning(f"[WARNING] Variáveis opcionais faltando: {missing_optional}")
            self.logger.warning("[INFO] Algumas funcionalidades podem estar limitadas")
        else:
            self.logger.info("[OK] Todas as variáveis opcionais estão configuradas")
        
    def load_accounts(self):
        """Carregar contas do accounts.json"""
        try:
            accounts_file = Path(__file__).parent / "accounts.json"
            with open(accounts_file, 'r', encoding='utf-8') as f:
                self.accounts = json.load(f)
            self.logger.info(f"[OK] Carregado accounts.json com {len(self.accounts)} contas")
            for account in self.accounts:
                self.logger.info(f"  [ACCOUNT] Conta: {account['nome']}")
        except Exception as e:
            self.logger.error(f"[ERROR] Erro ao carregar accounts.json: {e}")
            self.accounts = []
    
    def check_environment(self):
        """Verificar se as variáveis de ambiente estão configuradas"""
        self.logger.info("[CHECK] Verificando variáveis de ambiente...")
        
        # Verificar variáveis básicas
        basic_vars = ['OPENAI_API_KEY', 'RAPIDAPI_KEY']
        missing_vars = []
        
        for var in basic_vars:
            if not os.getenv(var):
                missing_vars.append(var)
            else:
                self.logger.info(f"  [OK] {var} configurada")
        
        if missing_vars:
            self.logger.error(f"[ERROR] Variáveis faltando: {missing_vars}")
            return False 
        
        # Verificações adicionais de canais globais
        additional_vars = ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID']
        for var in additional_vars:
            if not os.getenv(var):
                self.logger.warning(f"  [WARNING] {var} não configurada (necessária para notificações)")
            else:
                self.logger.info(f"  [OK] {var} configurada")

        self.logger.info("[OK] Variáveis básicas configuradas!")
        return True

    def _verify_instagram_connectivity(self, business_account_id: str, access_token: str) -> dict:
        """Conectar ao Graph API para validar ID e token; coletar status HTTP."""
        try:
            url = f"https://graph.facebook.com/v20.0/{business_account_id}"
            params = {"fields": "id,username", "access_token": access_token}
            resp = requests.get(url, params=params, timeout=30)
            ok = resp.ok
            info = {}
            try:
                info = resp.json()
            except Exception:
                info = {"text": resp.text[:200]}
            self.logger.info(f"  🌐 Instagram API: HTTP {resp.status_code} - keys={list(info.keys())[:3]}")
            return {"ok": ok, "status": resp.status_code, "data": info}
        except Exception as e:
            self.logger.error(f"  ❌ Instagram connectivity error: {e}")
            return {"ok": False, "error": str(e)}

    def _verify_instagram_permissions(self, business_account_id: str, access_token: str) -> dict:
        """Tentar leitura de mídia para validar permissões básicas (instagram_basic)."""
        try:
            url = f"https://graph.facebook.com/v20.0/{business_account_id}/media"
            params = {"fields": "id", "limit": 1, "access_token": access_token}
            resp = requests.get(url, params=params, timeout=30)
            ok = resp.ok
            data = {}
            try:
                data = resp.json()
            except Exception:
                data = {"text": resp.text[:200]}
            self.logger.info(f"  🔐 Instagram permissions: HTTP {resp.status_code} - ok={ok}")
            return {"ok": ok, "status": resp.status_code, "data": data}
        except Exception as e:
            self.logger.error(f"  ❌ Instagram permissions check error: {e}")
            return {"ok": False, "error": str(e)}

    def _verify_telegram_connectivity(self, bot_token: str, chat_id: str) -> dict:
        """Validar bot via getMe e chat via getChat no Telegram."""
        try:
            url_me = f"https://api.telegram.org/bot{bot_token}/getMe"
            r_me = requests.get(url_me, timeout=30)
            ok_me = r_me.ok
            url_chat = f"https://api.telegram.org/bot{bot_token}/getChat"
            r_chat = requests.get(url_chat, params={"chat_id": chat_id}, timeout=30)
            ok_chat = r_chat.ok
            self.logger.info(f"  🤖 Telegram getMe: HTTP {r_me.status_code} | getChat: HTTP {r_chat.status_code}")
            return {"ok": ok_me and ok_chat, "getMe": r_me.status_code, "getChat": r_chat.status_code}
        except Exception as e:
            self.logger.error(f"  ❌ Telegram connectivity error: {e}")
            return {"ok": False, "error": str(e)}

    def _verify_content_formatting(self) -> dict:
        """Validação básica de formatação: caption tamanho e URL de imagem padrão."""
        # Regras simples: caption <= 2200 chars; URL http(s)
        default_image = "https://images.unsplash.com/photo-1506905925346-21bda4d32df4"
        sample_caption = "Teste de formatação: conteúdo com emojis ✅🔥 e hashtags #teste #midday"
        issues = []
        if len(sample_caption) > 2200:
            issues.append("Caption muito longa")
        if not default_image.startswith("http"):
            issues.append("URL de imagem inválida")
        ok = len(issues) == 0
        self.logger.info(f"  📝 Formatação de conteúdo: ok={ok} issues={issues}")
        return {"ok": ok, "issues": issues}

    def preflight_checks(self) -> bool:
        """Executa pré-verificações ampliadas para Instagram/Telegram e conteúdo."""
        self.logger.info("🧪 Executando pré-verificações dos canais e conteúdo...")
        overall_ok = True

        # Telegram (global)
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
        if bot_token and chat_id:
            tg = self._verify_telegram_connectivity(bot_token, chat_id)
            self._preflight_summary.append({"telegram": tg})
            if not tg.get("ok"):
                overall_ok = False
        else:
            self.logger.warning("  ⚠️ Telegram não configurado (sem verificação)")

        # Instagram por conta
        for account in self.accounts:
            acc_name = account.get('nome')
            bid = account.get('instagram_id')
            tok = account.get('instagram_access_token')
            if not bid or not tok:
                self.logger.warning(f"  ⚠️ Conta {acc_name}: instagram_id/token ausentes")
                overall_ok = False
                continue
            self.logger.info(f"  🔎 Conta {acc_name}: verificando Instagram API e permissões...")
            conn = self._verify_instagram_connectivity(bid, tok)
            perms = self._verify_instagram_permissions(bid, tok)
            self._preflight_summary.append({acc_name: {"connectivity": conn, "permissions": perms}})
            if not conn.get("ok") or not perms.get("ok"):
                overall_ok = False

        # Formatação de conteúdo
        fmt = self._verify_content_formatting()
        self._preflight_summary.append({"formatting": fmt})
        if not fmt.get("ok"):
            overall_ok = False

        if overall_ok:
            self.logger.info("✅ Pré-verificações concluídas com sucesso")
        else:
            self.logger.warning("⚠️ Pré-verificações concluídas com alertas/erros — verifique logs")
        return overall_ok
    
    @monitor_execution("create_post", "all_accounts")
    def create_scheduled_post(self):
        """Criar posts para todas as contas (Feed) com recuperação automática"""
        self.logger.info("🎨 === INICIANDO CRIAÇÃO DE POSTS (FEED) ===")
        
        if not self.accounts:
            self.logger.error("❌ Nenhuma conta carregada!")
            return
        
        success_count = 0
        error_count = 0
        
        for account in self.accounts:
            account_name = account['nome']
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                start_time = time.time()
                try:
                    self.logger.info(f"📱 Processando conta: {account_name} (Tentativa {retry_count + 1}/{max_retries})")
                    
                    # Configurar variáveis de ambiente específicas da conta
                    os.environ['INSTAGRAM_BUSINESS_ACCOUNT_ID'] = account['instagram_id']
                    os.environ['INSTAGRAM_ACCESS_TOKEN'] = account['instagram_access_token']
                    
                    # Chamar generate_and_publish para Feed
                    self.logger.info(f"🚀 Gerando post para {account_name} (Feed) ...")
                    result = generate_and_publish(account_name=account_name, publish_to_stories=False)
                    status = result.get("status")
                    media_id = result.get("media_id")
                    replicate_error = result.get("replicate_error")
                    
                    duration = time.time() - start_time
                    
                    self.logger.info(
                        f"📊 Resultado Feed [{account_name}] status={status} media_id={media_id} replicate_error={bool(replicate_error)} duration={duration:.2f}s"
                    )
                    
                    if replicate_error:
                        self.logger.warning(f"  ⚠️ Replicate error: {replicate_error}")
                    
                    if status == "PUBLISHED":
                        self.logger.info(f"✅ Post Feed publicado com sucesso para {account_name}")
                        performance_monitor.record_execution(
                            "create_post", account_name, "success", duration,
                            {"media_id": media_id, "retry_count": retry_count}
                        )
                        success_count += 1
                        break  # Sucesso, sair do loop de retry
                    else:
                        self.logger.warning(f"  ⚠️ Publicação Feed não concluída para {account_name}: {status}")
                        if retry_count < max_retries - 1:
                            self.logger.info(f"🔄 Tentando novamente em 30 segundos...")
                            time.sleep(30)
                        retry_count += 1
                        
                except Exception as e:
                    duration = time.time() - start_time
                    self.logger.error(f"❌ Erro ao processar conta {account_name} (Tentativa {retry_count + 1}): {e}")
                    performance_monitor.record_execution(
                        "create_post", account_name, "error", duration,
                        {"error": str(e), "retry_count": retry_count}
                    )
                    if retry_count < max_retries - 1:
                        self.logger.info(f"🔄 Tentando novamente em 60 segundos...")
                        time.sleep(60)
                    retry_count += 1
            
            # Se chegou aqui e não teve sucesso, contar como erro
            if retry_count >= max_retries:
                error_count += 1
                self.logger.error(f"❌ Falha definitiva para conta {account_name} após {max_retries} tentativas")
                # Notificar falha crítica
                try:
                    notification_system.notify_execution_failure("create_post", account_name, max_retries)
                except Exception as e:
                    self.logger.debug(f"Erro ao enviar notificação de falha: {e}")
        
        # Relatório final
        total_accounts = len(self.accounts)
        self.logger.info(f"📊 Relatório Final - Posts Feed: {success_count}/{total_accounts} sucessos, {error_count} falhas")
    
    @monitor_execution("create_stories", "all_accounts")
    def create_scheduled_stories(self):
        """Criar stories para todas as contas com recuperação automática"""
        self.logger.info("📱 === INICIANDO CRIAÇÃO DE STORIES ===")
        
        if not self.accounts:
            self.logger.error("❌ Nenhuma conta carregada!")
            return
        
        success_count = 0
        error_count = 0
        
        for account in self.accounts:
            account_name = account['nome']
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                start_time = time.time()
                try:
                    self.logger.info(f"📱 Processando conta: {account_name} (Tentativa {retry_count + 1}/{max_retries})")
                    
                    # Configurar variáveis de ambiente específicas da conta
                    os.environ['INSTAGRAM_BUSINESS_ACCOUNT_ID'] = account['instagram_id']
                    os.environ['INSTAGRAM_ACCESS_TOKEN'] = account['instagram_access_token']
                    
                    # Chamar generate_and_publish para Stories
                    self.logger.info(f"🚀 Gerando stories para {account_name} ...")
                    result = generate_and_publish(account_name=account_name, publish_to_stories=True)
                    status = result.get("status")
                    stories_info = result.get("stories", {}) if isinstance(result, dict) else {}
                    stories_published = stories_info.get("success", False)
                    
                    duration = time.time() - start_time
                    
                    self.logger.info(
                        f"📊 Resultado Stories [{account_name}] status={status} stories_published={stories_published} duration={duration:.2f}s"
                    )
                    
                    if status == "PUBLISHED" and stories_published:
                        self.logger.info(f"✅ Stories publicados com sucesso para {account_name}")
                        performance_monitor.record_execution(
                            "create_stories", account_name, "success", duration,
                            {"stories_published": stories_published, "retry_count": retry_count}
                        )
                        success_count += 1
                        break  # Sucesso, sair do loop de retry
                    else:
                        if status != "PUBLISHED":
                            self.logger.warning(f"  ⚠️ Publicação base não concluída para {account_name}: {status}")
                        if not stories_published:
                            self.logger.warning(f"  ⚠️ Stories não publicados para {account_name}")
                        
                        if retry_count < max_retries - 1:
                            self.logger.info(f"🔄 Tentando novamente em 30 segundos...")
                            time.sleep(30)
                        retry_count += 1
                        
                except Exception as e:
                    duration = time.time() - start_time
                    self.logger.error(f"❌ Erro ao processar conta {account_name} (Tentativa {retry_count + 1}): {e}")
                    performance_monitor.record_execution(
                        "create_stories", account_name, "error", duration,
                        {"error": str(e), "retry_count": retry_count}
                    )
                    if retry_count < max_retries - 1:
                        self.logger.info(f"🔄 Tentando novamente em 60 segundos...")
                        time.sleep(60)
                    retry_count += 1
            
            # Se chegou aqui e não teve sucesso, contar como erro
            if retry_count >= max_retries:
                error_count += 1
                self.logger.error(f"❌ Falha definitiva para conta {account_name} após {max_retries} tentativas")
                # Notificar falha crítica
                try:
                    notification_system.notify_execution_failure("create_stories", account_name, max_retries)
                except Exception as e:
                    self.logger.debug(f"Erro ao enviar notificação de falha: {e}")
        
        # Relatório final
        total_accounts = len(self.accounts)
        self.logger.info(f"📊 Relatório Final - Stories: {success_count}/{total_accounts} sucessos, {error_count} falhas")
    
    def setup_schedule(self):
        """Configurar agendamentos (horários em UTC para Railway)"""
        self.logger.info("📅 Configurando agendamentos...")
        
        # Horários em UTC (Railway usa UTC)
        # 6h BRT = 9h UTC, 12h BRT = 15h UTC, 18h BRT = 21h UTC, 19h BRT = 22h UTC
        # 9h BRT = 12h UTC, 15h BRT = 18h UTC, 21h BRT = 00h UTC (próximo dia)
        
        # Feed posts
        schedule.every().day.at("09:00").do(self.create_scheduled_post)  # 6h BRT
        schedule.every().day.at("15:00").do(self.create_scheduled_post)  # 12h BRT
        schedule.every().day.at("21:00").do(self.create_scheduled_post)  # 18h BRT
        schedule.every().day.at("22:00").do(self.create_scheduled_post)  # 19h BRT
        
        # Stories
        schedule.every().day.at("12:00").do(self.create_scheduled_stories)  # 9h BRT
        schedule.every().day.at("18:00").do(self.create_scheduled_stories)  # 15h BRT
        schedule.every().day.at("00:00").do(self.create_scheduled_stories)  # 21h BRT
        
        self.logger.info("✅ Agendamentos configurados:")
        self.logger.info("📝 FEED:")
        self.logger.info("  - 09:00 UTC (06:00 BRT)")
        self.logger.info("  - 15:00 UTC (12:00 BRT)")
        self.logger.info("  - 21:00 UTC (18:00 BRT)")
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

        # Pré-verificações ampliadas (canais e conteúdo)
        self.preflight_checks()
        
        # Configurar agendamentos
        self.setup_schedule()
        
        # Enviar notificação de inicialização
        try:
            notification_system.send_startup_notification()
        except Exception as e:
            self.logger.warning(f"⚠️ Erro ao enviar notificação de inicialização: {e}")
        
        # Executar teste inicial (opcional)
        # self.logger.info("🔄 Executando teste inicial...")
        # self.create_scheduled_stories()
        
        self.logger.info("🔄 Entrando no loop principal...")
        self.logger.info(f"📋 Total de jobs agendados: {len(schedule.jobs)}")
        
        # Loop principal
        loop_count = 0
        metrics_save_counter = 0
        
        while True:
            loop_count += 1
            metrics_save_counter += 1
            
            # Atualizar atividade no health server
            if hasattr(self, 'health_server'):
                self.health_server.update_activity()
            
            # Salvar métricas a cada 10 minutos (10 loops)
            if metrics_save_counter >= 10:
                try:
                    performance_monitor.save_metrics()
                    self.logger.info("💾 Métricas de performance salvas")
                    metrics_save_counter = 0
                except Exception as e:
                    self.logger.error(f"❌ Erro ao salvar métricas: {e}")
            
            # Log a cada 30 minutos
            if loop_count % 30 == 1:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
                self.logger.info(f"💓 Sistema ativo - Loop #{loop_count} - {current_time}")
                self.logger.info(f"📋 Jobs agendados: {len(schedule.jobs)}")
                if schedule.jobs:
                    self.logger.info(f"⏰ Próxima execução: {schedule.next_run()}")
                
                # Log de resumo de performance a cada 30 minutos
                try:
                    summary = performance_monitor.get_performance_summary(1)  # Última hora
                    if summary.get("total_executions", 0) > 0:
                        success_rate = summary.get("success_rate", 0)
                        total_exec = summary.get("total_executions", 0)
                        self.logger.info(f"📊 Performance (1h): {total_exec} execuções, {success_rate:.1f}% sucesso")
                    
                    # Verificar alertas de sistema a cada 30 minutos
                    system_metrics = performance_monitor.get_system_metrics()
                    notification_system.monitor_and_alert(system_metrics, summary)
                    
                except Exception as e:
                    self.logger.debug(f"Erro ao obter resumo de performance: {e}")
            
            # Enviar relatório diário às 06:00 UTC (03:00 BRT)
            current_hour = datetime.now().hour
            if current_hour == 6 and loop_count % 60 == 1:  # Uma vez por hora, apenas no minuto 1
                try:
                    summary_24h = performance_monitor.get_performance_summary(24)
                    notification_system.send_daily_report(summary_24h)
                except Exception as e:
                    self.logger.error(f"❌ Erro ao enviar relatório diário: {e}")
            
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