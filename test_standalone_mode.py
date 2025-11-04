#!/usr/bin/env python3
"""
Teste do modo standalone - funcionamento sem RapidAPI
Demonstra como o sistema pode gerar e publicar conteúdo sem depender de coleta externa
"""
import os
import sys
from dotenv import load_dotenv

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config import load_config
from pipeline.generate_and_publish import generate_and_publish

def test_standalone_mode():
    """Testa o modo standalone do sistema"""
    load_dotenv()
    
    print("🚀 TESTE DO MODO STANDALONE")
    print("=" * 60)
    print("Este teste demonstra como o sistema pode funcionar")
    print("sem depender do RapidAPI, gerando conteúdo próprio.")
    print()
    
    # Carregar configurações
    cfg = load_config()
    
    # Verificar configurações essenciais
    required_keys = [
        "INSTAGRAM_BUSINESS_ACCOUNT_ID",
        "INSTAGRAM_ACCESS_TOKEN", 
        "OPENAI_API_KEY",
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHAT_ID"
    ]
    
    missing_keys = []
    for key in required_keys:
        if not cfg.get(key):
            missing_keys.append(key)
    
    if missing_keys:
        print("❌ Configurações faltando:")
        for key in missing_keys:
            print(f"   • {key}")
        print()
        print("Configure essas variáveis no .env para continuar.")
        return False
    
    print("✅ Configurações básicas OK")
    print()
    
    # Configurações do teste
    test_configs = [
        {
            "name": "Conteúdo Motivacional",
            "content_prompt": "Crie uma mensagem motivacional sobre superação e crescimento pessoal",
            "caption_style": "motivacional",
            "source_image_url": "https://via.placeholder.com/1080x1080/4A90E2/FFFFFF?text=Motivação"
        },
        {
            "name": "Dica de Produtividade", 
            "content_prompt": "Compartilhe uma dica prática de produtividade para profissionais",
            "caption_style": "educativo",
            "source_image_url": "https://via.placeholder.com/1080x1080/50C878/FFFFFF?text=Produtividade"
        },
        {
            "name": "Sistema Temático Semanal",
            "content_prompt": None,  # Deixar o sistema temático decidir
            "caption_style": None,
            "source_image_url": "https://via.placeholder.com/1080x1080/FF6B6B/FFFFFF?text=Tema+Semanal"
        }
    ]
    
    print("🧪 TESTES DISPONÍVEIS:")
    for i, config in enumerate(test_configs, 1):
        print(f"   {i}. {config['name']}")
    print()
    
    # Escolher teste (por simplicidade, usar o primeiro)
    selected_test = test_configs[0]
    print(f"🎯 Executando teste: {selected_test['name']}")
    print("-" * 40)
    
    try:
        # Executar geração e publicação
        result = generate_and_publish(
            openai_key=cfg["OPENAI_API_KEY"],
            replicate_token=cfg.get("REPLICATE_TOKEN", ""),
            instagram_business_id=cfg["INSTAGRAM_BUSINESS_ACCOUNT_ID"],
            instagram_access_token=cfg["INSTAGRAM_ACCESS_TOKEN"],
            telegram_bot_token=cfg["TELEGRAM_BOT_TOKEN"],
            telegram_chat_id=cfg["TELEGRAM_CHAT_ID"],
            source_image_url=selected_test["source_image_url"],
            content_prompt=selected_test["content_prompt"],
            caption_style=selected_test["caption_style"],
            account_name="Milton_Albanez",
            disable_replicate=True,  # Usar imagem placeholder por enquanto
            use_weekly_themes=True
        )
        
        print()
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print(f"📊 Resultado: {result}")
        print()
        print("🎉 O sistema pode funcionar perfeitamente sem RapidAPI!")
        print("💡 Benefícios do modo standalone:")
        print("   • Não depende de APIs externas instáveis")
        print("   • Conteúdo 100% original e personalizado")
        print("   • Sistema temático semanal automático")
        print("   • Controle total sobre qualidade e estilo")
        print("   • Sem limitações de rate limit ou assinatura")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        print()
        print("🔧 Possíveis soluções:")
        print("   1. Verificar se o token do Instagram está válido")
        print("   2. Verificar se a chave da OpenAI está correta")
        print("   3. Verificar conectividade com internet")
        print("   4. Verificar configurações do Telegram")
        
        return False

def show_standalone_benefits():
    """Mostra os benefícios do modo standalone"""
    print()
    print("🌟 VANTAGENS DO MODO STANDALONE")
    print("=" * 60)
    print()
    print("✅ INDEPENDÊNCIA TOTAL:")
    print("   • Não depende de APIs de terceiros instáveis")
    print("   • Sem problemas de assinatura ou rate limits")
    print("   • Funciona 24/7 sem interrupções")
    print()
    print("🎨 CONTEÚDO ORIGINAL:")
    print("   • 100% gerado pelo sistema")
    print("   • Personalizado para sua marca")
    print("   • Consistente com sua identidade visual")
    print()
    print("🗓️ SISTEMA TEMÁTICO:")
    print("   • Conteúdo automático baseado no dia da semana")
    print("   • Horários otimizados para engajamento")
    print("   • Temas variados e relevantes")
    print()
    print("⚡ PERFORMANCE:")
    print("   • Mais rápido (sem APIs externas)")
    print("   • Mais confiável")
    print("   • Menor latência")
    print()
    print("💰 ECONOMIA:")
    print("   • Sem custos de APIs externas")
    print("   • Apenas OpenAI (que já está configurada)")
    print("   • ROI mais alto")

if __name__ == "__main__":
    success = test_standalone_mode()
    show_standalone_benefits()
    
    if success:
        print()
        print("🚀 PRÓXIMOS PASSOS:")
        print("   1. Configure o cron para execução automática")
        print("   2. Monitore a performance via dashboard")
        print("   3. Ajuste temas semanais conforme necessário")
        print("   4. Aproveite o sistema 100% funcional!")
    else:
        print()
        print("🔧 CORREÇÕES NECESSÁRIAS:")
        print("   1. Corrija as configurações indicadas acima")
        print("   2. Execute o teste novamente")
        print("   3. Verifique os logs para mais detalhes")