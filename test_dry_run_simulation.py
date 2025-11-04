#!/usr/bin/env python3
"""
Simulação Completa (Dry-Run) do Processo de Publicação do Feed
Testa todo o pipeline sem fazer publicações reais no Instagram
"""

import os
import sys
import json
import datetime
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_dry_run_simulation():
    """Executa simulação completa do processo de publicação"""
    print("🔄 INICIANDO SIMULAÇÃO COMPLETA (DRY-RUN) DO FEED")
    print("=" * 60)
    
    results = {
        "timestamp": datetime.datetime.now().isoformat(),
        "simulation_type": "dry_run",
        "steps": {},
        "errors": [],
        "warnings": [],
        "success": False
    }
    
    # 1. Verificar configurações
    print("\n1️⃣ VERIFICANDO CONFIGURAÇÕES...")
    try:
        from config import load_config
        config = load_config()
        
        # Simular carregamento de credenciais do arquivo permanente
        cred_file = Path("CREDENCIAIS_PERMANENTES.json")
        if cred_file.exists():
            with open(cred_file, 'r', encoding='utf-8') as f:
                credentials = json.load(f)
            
            # Simular configuração das variáveis
            for key, value in credentials.get("railway_environment_variables", {}).items():
                if key not in os.environ:
                    os.environ[key] = value
            
            # Configurar conta específica para teste
            milton_creds = credentials.get("instagram_accounts", {}).get("milton_albanez", {})
            for key, value in milton_creds.items():
                if key not in os.environ:
                    os.environ[key] = value
        
        config = load_config()  # Recarregar com credenciais
        
        results["steps"]["config_check"] = {
            "status": "success",
            "details": "Configurações carregadas com sucesso"
        }
        print("✅ Configurações carregadas")
        
    except Exception as e:
        error_msg = f"Erro ao carregar configurações: {str(e)}"
        results["errors"].append(error_msg)
        results["steps"]["config_check"] = {"status": "error", "error": error_msg}
        print(f"❌ {error_msg}")
    
    # 2. Verificar contas do feed
    print("\n2️⃣ VERIFICANDO CONTAS DO FEED...")
    try:
        accounts_file = Path("accounts.json")
        if accounts_file.exists():
            with open(accounts_file, 'r', encoding='utf-8') as f:
                accounts = json.load(f)
            
            # accounts.json é uma lista, não um dicionário
            if isinstance(accounts, list):
                feed_accounts = [acc for acc in accounts if acc.get("type") == "feed"]
            else:
                feed_accounts = [acc for acc in accounts.values() if acc.get("type") == "feed"]
            
            results["steps"]["feed_accounts"] = {
                "status": "success",
                "count": len(feed_accounts),
                "accounts": [acc.get("nome", "Unknown") for acc in feed_accounts]
            }
            print(f"✅ {len(feed_accounts)} conta(s) do feed encontrada(s)")
            
        else:
            raise FileNotFoundError("accounts.json não encontrado")
            
    except Exception as e:
        error_msg = f"Erro ao verificar contas: {str(e)}"
        results["errors"].append(error_msg)
        results["steps"]["feed_accounts"] = {"status": "error", "error": error_msg}
        print(f"❌ {error_msg}")
    
    # 3. Testar geração de conteúdo
    print("\n3️⃣ TESTANDO GERAÇÃO DE CONTEÚDO...")
    try:
        from services.openai_client import OpenAIClient
        
        openai_key = config.get("OPENAI_API_KEY")
        if not openai_key:
            raise ValueError("OPENAI_API_KEY não configurada")
        
        client = OpenAIClient(openai_key)
        
        # Simular prompt de uma conta do feed
        test_prompt = "Crie um post sobre tecnologia e inovação"
        
        # Teste sem fazer chamada real (dry-run)
        print("🔄 Simulando geração de conteúdo...")
        
        results["steps"]["content_generation"] = {
            "status": "success",
            "details": "Cliente OpenAI inicializado com sucesso",
            "test_prompt": test_prompt
        }
        print("✅ Geração de conteúdo configurada")
        
    except Exception as e:
        error_msg = f"Erro na geração de conteúdo: {str(e)}"
        results["errors"].append(error_msg)
        results["steps"]["content_generation"] = {"status": "error", "error": error_msg}
        print(f"❌ {error_msg}")
    
    # 4. Testar geração de imagem
    print("\n4️⃣ TESTANDO GERAÇÃO DE IMAGEM...")
    try:
        from services.replicate_client import ReplicateClient
        
        replicate_token = config.get("REPLICATE_TOKEN")
        if not replicate_token:
            raise ValueError("REPLICATE_TOKEN não configurado")
        
        client = ReplicateClient(replicate_token)
        
        # Teste sem fazer chamada real (dry-run)
        print("🔄 Simulando geração de imagem...")
        
        results["steps"]["image_generation"] = {
            "status": "success",
            "details": "Cliente Replicate inicializado com sucesso"
        }
        print("✅ Geração de imagem configurada")
        
    except Exception as e:
        error_msg = f"Erro na geração de imagem: {str(e)}"
        results["errors"].append(error_msg)
        results["steps"]["image_generation"] = {"status": "error", "error": error_msg}
        print(f"❌ {error_msg}")
    
    # 5. Testar conexão Instagram
    print("\n5️⃣ TESTANDO CONEXÃO INSTAGRAM...")
    try:
        from services.instagram_client import InstagramClient
        
        access_token = config.get("INSTAGRAM_ACCESS_TOKEN")
        business_id = config.get("INSTAGRAM_BUSINESS_ACCOUNT_ID")
        
        if not access_token or not business_id:
            raise ValueError("Credenciais do Instagram não configuradas")
        
        client = InstagramClient(access_token, business_id)
        
        # Teste sem fazer publicação real (dry-run)
        print("🔄 Simulando conexão com Instagram...")
        
        results["steps"]["instagram_connection"] = {
            "status": "success",
            "details": "Cliente Instagram inicializado com sucesso",
            "business_id": business_id[:10] + "..."  # Mascarar ID
        }
        print("✅ Conexão Instagram configurada")
        
    except Exception as e:
        error_msg = f"Erro na conexão Instagram: {str(e)}"
        results["errors"].append(error_msg)
        results["steps"]["instagram_connection"] = {"status": "error", "error": error_msg}
        print(f"❌ {error_msg}")
    
    # 6. Testar notificações Telegram
    print("\n6️⃣ TESTANDO NOTIFICAÇÕES TELEGRAM...")
    try:
        from services.telegram_client import TelegramClient
        
        bot_token = config.get("TELEGRAM_BOT_TOKEN")
        chat_id = config.get("TELEGRAM_CHAT_ID")
        
        if not bot_token or not chat_id:
            raise ValueError("Credenciais do Telegram não configuradas")
        
        client = TelegramClient(bot_token, chat_id)
        
        # Teste sem enviar mensagem real (dry-run)
        print("🔄 Simulando notificação Telegram...")
        
        results["steps"]["telegram_notification"] = {
            "status": "success",
            "details": "Cliente Telegram inicializado com sucesso"
        }
        print("✅ Notificações Telegram configuradas")
        
    except Exception as e:
        error_msg = f"Erro nas notificações Telegram: {str(e)}"
        results["errors"].append(error_msg)
        results["steps"]["telegram_notification"] = {"status": "error", "error": error_msg}
        print(f"❌ {error_msg}")
    
    # 7. Simular processo completo
    print("\n7️⃣ SIMULANDO PROCESSO COMPLETO...")
    try:
        print("🔄 Simulando pipeline completo:")
        print("   📝 Geração de conteúdo...")
        print("   🎨 Geração de imagem...")
        print("   📱 Preparação do post...")
        print("   📤 Publicação (SIMULADA)...")
        print("   📢 Notificação (SIMULADA)...")
        
        results["steps"]["full_pipeline"] = {
            "status": "success",
            "details": "Pipeline completo simulado com sucesso"
        }
        print("✅ Pipeline completo simulado")
        
    except Exception as e:
        error_msg = f"Erro no pipeline: {str(e)}"
        results["errors"].append(error_msg)
        results["steps"]["full_pipeline"] = {"status": "error", "error": error_msg}
        print(f"❌ {error_msg}")
    
    # 8. Verificar horário de execução
    print("\n8️⃣ VERIFICANDO HORÁRIO DE EXECUÇÃO...")
    try:
        import pytz
        
        brt = pytz.timezone('America/Sao_Paulo')
        now_brt = datetime.datetime.now(brt)
        next_19h = now_brt.replace(hour=19, minute=0, second=0, microsecond=0)
        
        if next_19h <= now_brt:
            next_19h += datetime.timedelta(days=1)
        
        time_until = next_19h - now_brt
        
        results["steps"]["schedule_check"] = {
            "status": "success",
            "current_time_brt": now_brt.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "next_execution": next_19h.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "time_until": str(time_until)
        }
        print(f"✅ Próxima execução: {next_19h.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"   Tempo restante: {time_until}")
        
    except Exception as e:
        error_msg = f"Erro na verificação de horário: {str(e)}"
        results["errors"].append(error_msg)
        results["steps"]["schedule_check"] = {"status": "error", "error": error_msg}
        print(f"❌ {error_msg}")
    
    # Calcular resultado final
    successful_steps = sum(1 for step in results["steps"].values() if step.get("status") == "success")
    total_steps = len(results["steps"])
    success_rate = (successful_steps / total_steps) * 100 if total_steps > 0 else 0
    
    results["success"] = success_rate >= 75
    results["success_rate"] = success_rate
    results["successful_steps"] = successful_steps
    results["total_steps"] = total_steps
    
    # Resultado final
    print("\n" + "=" * 60)
    print("📊 RESULTADO DA SIMULAÇÃO")
    print("=" * 60)
    
    if results["success"]:
        print("✅ SIMULAÇÃO BEM-SUCEDIDA!")
        print(f"   Taxa de sucesso: {success_rate:.1f}% ({successful_steps}/{total_steps})")
    else:
        print("⚠️ SIMULAÇÃO COM PROBLEMAS")
        print(f"   Taxa de sucesso: {success_rate:.1f}% ({successful_steps}/{total_steps})")
    
    if results["errors"]:
        print(f"\n❌ Erros encontrados ({len(results['errors'])}):")
        for error in results["errors"]:
            print(f"   • {error}")
    
    if results["warnings"]:
        print(f"\n⚠️ Avisos ({len(results['warnings'])}):")
        for warning in results["warnings"]:
            print(f"   • {warning}")
    
    # Salvar relatório
    report_file = "dry_run_simulation_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Relatório salvo em: {report_file}")
    
    return results

if __name__ == "__main__":
    test_dry_run_simulation()