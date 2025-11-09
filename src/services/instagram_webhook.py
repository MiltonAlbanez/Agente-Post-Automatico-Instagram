#!/usr/bin/env python3
"""
Instagram Webhook Service
Coleta automática de métricas de engagement via webhook do Instagram
"""

import json
import hmac
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify
from pathlib import Path

from .performance_tracker import PerformanceTracker
from .notification_manager import NotificationManager

class InstagramWebhookService:
    """
    Serviço de webhook para receber atualizações automáticas do Instagram
    """
    
    def __init__(self, config_path: str = "config/webhook_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.performance_tracker = PerformanceTracker()
        self.notification_manager = NotificationManager()
        self.app = Flask(__name__)
        self._setup_routes()
    
    def _load_config(self) -> Dict:
        """Carrega configurações do webhook"""
        default_config = {
            "webhook": {
                "verify_token": "seu_verify_token_aqui",
                "app_secret": "seu_app_secret_aqui",
                "port": 5000,
                "host": "0.0.0.0",
                "debug": False
            },
            "instagram": {
                "subscribed_fields": [
                    "comments",
                    "likes",
                    "story_insights",
                    "media"
                ]
            },
            "processing": {
                "auto_update_metrics": True,
                "send_notifications": True,
                "log_all_events": True
            }
        }
        
        config_file = Path(self.config_path)
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                default_config.update(loaded_config)
        else:
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
        
        return default_config
    
    def _setup_routes(self):
        """Configura as rotas do Flask"""
        
        @self.app.route('/webhook', methods=['GET'])
        def verify_webhook():
            """Verificação do webhook (challenge do Facebook)"""
            verify_token = self.config["webhook"]["verify_token"]
            
            if request.args.get('hub.verify_token') == verify_token:
                return request.args.get('hub.challenge')
            else:
                return 'Verification failed', 403
        
        @self.app.route('/webhook', methods=['POST'])
        def handle_webhook():
            """Processa eventos do webhook"""
            try:
                # Verificar assinatura
                if not self._verify_signature(request.data, request.headers.get('X-Hub-Signature-256')):
                    return 'Invalid signature', 403
                
                data = request.get_json()
                
                if data and 'entry' in data:
                    for entry in data['entry']:
                        self._process_entry(entry)
                
                return 'OK', 200
                
            except Exception as e:
                print(f"❌ Erro no webhook: {e}")
                self.notification_manager.send_error_alert(f"Erro no webhook: {str(e)}")
                return 'Error', 500
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Verificação de saúde do serviço"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'service': 'Instagram Webhook'
            })
    
    def _verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verifica a assinatura do webhook"""
        if not signature:
            return False
        
        try:
            app_secret = self.config["webhook"]["app_secret"]
            expected_signature = hmac.new(
                app_secret.encode('utf-8'),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            # Remove o prefixo 'sha256='
            signature = signature.replace('sha256=', '')
            
            return hmac.compare_digest(expected_signature, signature)
            
        except Exception as e:
            print(f"❌ Erro ao verificar assinatura: {e}")
            return False
    
    def _process_entry(self, entry: Dict[str, Any]) -> None:
        """Processa uma entrada do webhook"""
        try:
            if 'changes' in entry:
                for change in entry['changes']:
                    self._process_change(change)
                    
        except Exception as e:
            print(f"❌ Erro ao processar entrada: {e}")
    
    def _process_change(self, change: Dict[str, Any]) -> None:
        """Processa uma mudança específica"""
        try:
            field = change.get('field')
            value = change.get('value', {})
            
            if field == 'comments':
                self._handle_comment_event(value)
            elif field == 'likes':
                self._handle_like_event(value)
            elif field == 'media':
                self._handle_media_event(value)
            elif field == 'story_insights':
                self._handle_story_event(value)
            
            if self.config["processing"]["log_all_events"]:
                self._log_event(field, value)
                
        except Exception as e:
            print(f"❌ Erro ao processar mudança: {e}")
    
    def _handle_comment_event(self, value: Dict[str, Any]) -> None:
        """Processa evento de comentário"""
        try:
            media_id = value.get('media_id')
            comment_id = value.get('id')
            
            if media_id and self.config["processing"]["auto_update_metrics"]:
                # Buscar informações da conta associada ao media_id
                account_name = self._get_account_from_media_id(media_id)
                
                if account_name:
                    # Atualizar métricas
                    self.performance_tracker.update_metrics(
                        post_id=media_id,
                        likes=None,  # Não alterado
                        comments=1,  # Incrementar comentários
                        shares=None,
                        saves=None
                    )
                    
                    print(f"📝 Novo comentário registrado para {account_name}")
                    
        except Exception as e:
            print(f"❌ Erro ao processar comentário: {e}")
    
    def _handle_like_event(self, value: Dict[str, Any]) -> None:
        """Processa evento de curtida"""
        try:
            media_id = value.get('media_id')
            
            if media_id and self.config["processing"]["auto_update_metrics"]:
                account_name = self._get_account_from_media_id(media_id)
                
                if account_name:
                    # Atualizar métricas
                    self.performance_tracker.update_metrics(
                        post_id=media_id,
                        likes=1,  # Incrementar curtidas
                        comments=None,
                        shares=None,
                        saves=None
                    )
                    
                    print(f"❤️ Nova curtida registrada para {account_name}")
                    
        except Exception as e:
            print(f"❌ Erro ao processar curtida: {e}")
    
    def _handle_media_event(self, value: Dict[str, Any]) -> None:
        """Processa evento de mídia (novo post)"""
        try:
            media_id = value.get('id')
            media_type = value.get('media_type')
            
            if media_id:
                account_name = self._get_account_from_media_id(media_id)
                
                if account_name:
                    # Registrar novo post
                    self.performance_tracker.log_post(
                        post_id=media_id,
                        content_type=media_type or "image",
                        concept="webhook_auto",
                        hashtags=[]
                    )
                    
                    print(f"📸 Novo post detectado para {account_name}: {media_id}")
                    
                    if self.config["processing"]["send_notifications"]:
                        self.notification_manager.send_telegram_message(
                            f"📸 Novo post detectado!\n\nID: {media_id}\nTipo: {media_type}",
                            account_name
                        )
                    
        except Exception as e:
            print(f"❌ Erro ao processar mídia: {e}")
    
    def _handle_story_event(self, value: Dict[str, Any]) -> None:
        """Processa evento de story"""
        try:
            story_id = value.get('id')
            
            if story_id:
                account_name = self._get_account_from_media_id(story_id)
                
                if account_name:
                    print(f"📱 Story detectado para {account_name}: {story_id}")
                    
        except Exception as e:
            print(f"❌ Erro ao processar story: {e}")
    
    def _get_account_from_media_id(self, media_id: str) -> Optional[str]:
        """
        Obtém o nome da conta baseado no media_id
        Implementação simplificada - em produção, usar API do Instagram
        """
        try:
            # Carregar contas configuradas
            accounts_file = Path("accounts.json")
            if accounts_file.exists():
                with open(accounts_file, 'r', encoding='utf-8') as f:
                    accounts = json.load(f)
                
                # Para este exemplo, retornar a primeira conta
                # Em produção, fazer chamada à API para identificar a conta
                if accounts and len(accounts) > 0:
                    return accounts[0].get('nome', 'Conta Desconhecida')
            
            return None
            
        except Exception as e:
            print(f"❌ Erro ao identificar conta: {e}")
            return None
    
    def _log_event(self, field: str, value: Dict[str, Any]) -> None:
        """Registra evento em log"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'field': field,
                'value': value
            }
            
            log_file = Path("logs/webhook_events.log")
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
                
        except Exception as e:
            print(f"❌ Erro ao registrar log: {e}")
    
    def run(self) -> None:
        """Inicia o servidor webhook"""
        webhook_config = self.config["webhook"]
        
        print(f"🚀 Iniciando Instagram Webhook Service...")
        print(f"📡 Porta: {webhook_config['port']}")
        print(f"🔗 URL: http://{webhook_config['host']}:{webhook_config['port']}/webhook")
        print(f"❤️ Health Check: http://{webhook_config['host']}:{webhook_config['port']}/health")
        
        self.app.run(
            host=webhook_config["host"],
            port=webhook_config["port"],
            debug=webhook_config["debug"]
        )

def create_webhook_service() -> InstagramWebhookService:
    """Factory function para criar o serviço de webhook"""
    return InstagramWebhookService()

if __name__ == "__main__":
    # Executar o serviço de webhook
    webhook_service = create_webhook_service()
    webhook_service.run()