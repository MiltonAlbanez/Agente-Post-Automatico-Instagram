#!/usr/bin/env python3
"""
Teste específico para verificar o agendamento das 12h BRT
Simula o que acontecerá no Railway às 15:00 UTC (12:00 BRT)
"""

import os
import sys
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import load_config
from pipeline.generate_and_publish import generate_and_publish

def test_agendamento_12h():
    """Testa o agendamento das 12h BRT (15h UTC)"""
    
    print("🕐 TESTE AGENDAMENTO 12H BRT (15H UTC)")
    print("=" * 60)
    
    # Simular horário de Brasília
    now_utc = datetime.now(timezone.utc)
    now_brt = now_utc - timedelta(hours=3)
    
    print(f"⏰ Horário atual UTC: {now_utc.strftime('%H:%M:%S')}")
    print(f"🇧🇷 Horário atual BRT: {now_brt.strftime('%H:%M:%S')}")
    print(f"🎯 Teste simulando: 12:00 BRT (15:00 UTC)")
    print()
    
    # Carregar configuração
    cfg = load_config()
    
    # Verificar configurações essenciais
    print("🔍 VERIFICAÇÃO DE CONFIGURAÇÕES:")
    print(f"✅ Instagram ID: {cfg.get('INSTAGRAM_BUSINESS_ACCOUNT_ID', 'NÃO CONFIGURADO')}")
    print(f"✅ Instagram Token: {'CONFIGURADO' if cfg.get('INSTAGRAM_ACCESS_TOKEN') else 'NÃO CONFIGURADO'}")
    print(f"✅ OpenAI Key: {'CONFIGURADO' if cfg.get('OPENAI_API_KEY') else 'NÃO CONFIGURADO'}")
    print(f"✅ Telegram Bot: {'CONFIGURADO' if cfg.get('TELEGRAM_BOT_TOKEN') else 'NÃO CONFIGURADO'}")
    print(f"✅ Telegram Chat: {cfg.get('TELEGRAM_CHAT_ID', 'NÃO CONFIGURADO')}")
    print()
    
    # Carregar conta Milton_Albanez
    account_name = "Milton_Albanez"
    selected_account = None
    
    try:
        with open("accounts.json", "r", encoding="utf-8") as f:
            accounts = json.load(f)
        selected_account = next((a for a in accounts if a.get("nome") == account_name), None)
        
        if selected_account:
            print(f"✅ Conta encontrada: {account_name}")
            print(f"   📱 Instagram ID: {selected_account.get('instagram_id', 'Usando padrão')}")
            print(f"   🔑 Token próprio: {'SIM' if selected_account.get('instagram_access_token') else 'NÃO'}")
        else:
            print(f"⚠️ Conta {account_name} não encontrada, usando configuração padrão")
            
    except Exception as e:
        print(f"❌ Erro ao carregar accounts.json: {e}")
        return False
    
    print()
    print("🚀 INICIANDO TESTE DE PUBLICAÇÃO...")
    print("-" * 40)
    
    # Usar imagem motivacional específica para teste
    source_image_url = "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&auto=format&fit=crop&w=1080&h=1080&q=80"
    
    # Prompt específico para teste das 12h
    content_prompt = """
    Crie uma mensagem motivacional para o meio-dia, quando as pessoas estão no meio do dia de trabalho.
    Fale sobre manter o foco, a energia e a determinação mesmo nos momentos mais desafiadores.
    Use uma linguagem que inspire produtividade e perseverança.
    Inclua uma reflexão sobre como pequenas ações consistentes levam a grandes resultados.
    """
    
    try:
        # Usar credenciais específicas da conta se disponíveis
        acc_instagram_id = selected_account.get("instagram_id") if selected_account else cfg["INSTAGRAM_BUSINESS_ACCOUNT_ID"]
        acc_instagram_token = selected_account.get("instagram_access_token") if selected_account else cfg["INSTAGRAM_ACCESS_TOKEN"]
        
        print(f"📝 Gerando conteúdo para {account_name}...")
        print(f"🖼️ Imagem: Paisagem motivacional (Unsplash)")
        print(f"🎯 Tema: Motivação para meio-dia")
        print()
        
        result = generate_and_publish(
            openai_key=cfg["OPENAI_API_KEY"],
            replicate_token=cfg.get("REPLICATE_TOKEN", ""),
            instagram_business_id=acc_instagram_id,
            instagram_access_token=acc_instagram_token,
            telegram_bot_token=cfg["TELEGRAM_BOT_TOKEN"],
            telegram_chat_id=cfg["TELEGRAM_CHAT_ID"],
            source_image_url=source_image_url,
            content_prompt=content_prompt,
            caption_style="motivacional",
            account_name=account_name,
            account_config=selected_account,
            disable_replicate=True,  # Usar imagem original para teste
            publish_to_stories=False,
            use_weekly_themes=True
        )
        
        print()
        print("📊 RESULTADO DO TESTE:")
        print("=" * 40)
        
        if result.get('status') == 'PUBLISHED':
            print("🎉 SUCESSO TOTAL!")
            print("✅ Conteúdo gerado com OpenAI")
            print("✅ Imagem carregada do Unsplash")
            print("✅ Post publicado no Instagram")
            print("✅ Notificação enviada no Telegram")
            print()
            print("🔗 Detalhes da publicação:")
            print(f"   📱 Media ID: {result.get('media_id')}")
            print(f"   🆔 Creation ID: {result.get('creation_id')}")
            print(f"   📸 Imagem gerada: {result.get('generated_image_url', 'N/A')}")
            print()
            print("✅ SISTEMA PRONTO PARA AGENDAMENTO DAS 12H BRT!")
            print("🚀 Todas as soluções implementadas estão funcionando!")
            
        elif result.get('status') == 'ERROR':
            print("❌ ERRO NA PUBLICAÇÃO:")
            print(f"   Erro: {result.get('error', 'Erro desconhecido')}")
            print()
            print("🔧 AÇÕES NECESSÁRIAS:")
            print("   1. Verificar credenciais do Instagram")
            print("   2. Verificar conectividade")
            print("   3. Verificar se a imagem é válida")
            
        else:
            print(f"⚠️ STATUS INESPERADO: {result.get('status', 'UNKNOWN')}")
            print(f"   Detalhes: {result}")
        
        print()
        print("📋 CONFIGURAÇÃO PARA RAILWAY:")
        print("=" * 40)
        print("🕐 Horário BRT: 12:00 (meio-dia)")
        print("🌍 Horário UTC: 15:00")
        print("⚙️ Cron Expression: 0 15 * * *")
        print("🎯 Comando: autopost")
        print("📱 Conta: Milton_Albanez")
        
        return result.get('status') == 'PUBLISHED'
        
    except Exception as e:
        print(f"❌ ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    sucesso = test_agendamento_12h()
    
    print()
    print("🏁 CONCLUSÃO DO TESTE:")
    print("=" * 40)
    
    if sucesso:
        print("✅ SISTEMA APROVADO PARA AGENDAMENTO!")
        print("🎯 Pronto para publicar às 12h BRT")
        print("🔧 Todas as correções funcionando")
    else:
        print("❌ SISTEMA PRECISA DE AJUSTES")
        print("🔧 Revisar configurações antes do agendamento")