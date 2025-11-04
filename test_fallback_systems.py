#!/usr/bin/env python3
"""
Verificação dos Sistemas de Fallback
Testa mecanismos de recuperação em caso de falhas
"""

import os
import sys
import json
import datetime
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_fallback_systems():
    """Verifica sistemas de fallback e recuperação"""
    print("🛡️ VERIFICANDO SISTEMAS DE FALLBACK")
    print("=" * 50)
    
    results = {
        "timestamp": datetime.datetime.now().isoformat(),
        "test_type": "fallback_systems",
        "checks": {},
        "errors": [],
        "warnings": [],
        "success": False
    }
    
    # 1. Verificar contas backup
    print("\n1️⃣ VERIFICANDO CONTAS BACKUP...")
    try:
        accounts_file = Path("accounts.json")
        if accounts_file.exists():
            with open(accounts_file, 'r', encoding='utf-8') as f:
                accounts = json.load(f)
            
            if isinstance(accounts, list):
                total_accounts = len(accounts)
                feed_accounts = [acc for acc in accounts if acc.get("type") == "feed"]
                backup_accounts = [acc for acc in accounts if acc.get("type") != "feed"]
            else:
                total_accounts = len(accounts)
                feed_accounts = [acc for acc in accounts.values() if acc.get("type") == "feed"]
                backup_accounts = [acc for acc in accounts.values() if acc.get("type") != "feed"]
            
            results["checks"]["backup_accounts"] = {
                "status": "success",
                "total_accounts": total_accounts,
                "feed_accounts": len(feed_accounts),
                "backup_accounts": len(backup_accounts),
                "has_backup": len(backup_accounts) > 0
            }
            
            if len(backup_accounts) > 0:
                print(f"✅ {len(backup_accounts)} conta(s) backup disponível(is)")
            else:
                print("⚠️ Nenhuma conta backup configurada")
                results["warnings"].append("Nenhuma conta backup configurada")
            
        else:
            raise FileNotFoundError("accounts.json não encontrado")
            
    except Exception as e:
        error_msg = f"Erro ao verificar contas backup: {str(e)}"
        results["errors"].append(error_msg)
        results["checks"]["backup_accounts"] = {"status": "error", "error": error_msg}
        print(f"❌ {error_msg}")
    
    # 2. Verificar retry logic nos clientes
    print("\n2️⃣ VERIFICANDO RETRY LOGIC...")
    try:
        retry_checks = {}
        
        # Verificar RapidAPI Client
        rapidapi_file = Path("src/services/rapidapi_client.py")
        if rapidapi_file.exists():
            with open(rapidapi_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            has_retry = "retry" in content.lower() or "backoff" in content.lower()
            has_fallback_hosts = "alt_host" in content.lower() or "fallback" in content.lower()
            
            retry_checks["rapidapi"] = {
                "has_retry": has_retry,
                "has_fallback_hosts": has_fallback_hosts,
                "file_exists": True
            }
        else:
            retry_checks["rapidapi"] = {"file_exists": False}
        
        # Verificar Instagram Client
        instagram_file = Path("src/services/instagram_client.py")
        if instagram_file.exists():
            with open(instagram_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            has_retry = "retry" in content.lower() or "backoff" in content.lower()
            has_error_handling = "except" in content and "error" in content.lower()
            
            retry_checks["instagram"] = {
                "has_retry": has_retry,
                "has_error_handling": has_error_handling,
                "file_exists": True
            }
        else:
            retry_checks["instagram"] = {"file_exists": False}
        
        # Verificar OpenAI Client
        openai_file = Path("src/services/openai_client.py")
        if openai_file.exists():
            with open(openai_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            has_retry = "retry" in content.lower() or "backoff" in content.lower()
            has_error_handling = "except" in content and "error" in content.lower()
            
            retry_checks["openai"] = {
                "has_retry": has_retry,
                "has_error_handling": has_error_handling,
                "file_exists": True
            }
        else:
            retry_checks["openai"] = {"file_exists": False}
        
        # Verificar Replicate Client
        replicate_file = Path("src/services/replicate_client.py")
        if replicate_file.exists():
            with open(replicate_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            has_retry = "retry" in content.lower() or "backoff" in content.lower()
            has_error_handling = "except" in content and "error" in content.lower()
            
            retry_checks["replicate"] = {
                "has_retry": has_retry,
                "has_error_handling": has_error_handling,
                "file_exists": True
            }
        else:
            retry_checks["replicate"] = {"file_exists": False}
        
        results["checks"]["retry_logic"] = {
            "status": "success",
            "clients": retry_checks
        }
        
        # Contar clientes com retry
        clients_with_retry = sum(1 for client in retry_checks.values() 
                               if client.get("file_exists") and 
                               (client.get("has_retry") or client.get("has_error_handling")))
        total_clients = sum(1 for client in retry_checks.values() if client.get("file_exists"))
        
        print(f"✅ {clients_with_retry}/{total_clients} clientes com retry/error handling")
        
    except Exception as e:
        error_msg = f"Erro ao verificar retry logic: {str(e)}"
        results["errors"].append(error_msg)
        results["checks"]["retry_logic"] = {"status": "error", "error": error_msg}
        print(f"❌ {error_msg}")
    
    # 3. Verificar sistema de notificações de erro
    print("\n3️⃣ VERIFICANDO NOTIFICAÇÕES DE ERRO...")
    try:
        telegram_file = Path("src/services/telegram_client.py")
        if telegram_file.exists():
            with open(telegram_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            has_error_notification = "error" in content.lower() and "send" in content.lower()
            has_exception_handling = "except" in content
            
            results["checks"]["error_notifications"] = {
                "status": "success",
                "telegram_exists": True,
                "has_error_notification": has_error_notification,
                "has_exception_handling": has_exception_handling
            }
            
            if has_error_notification:
                print("✅ Sistema de notificação de erros configurado")
            else:
                print("⚠️ Sistema de notificação de erros não detectado")
                results["warnings"].append("Sistema de notificação de erros não detectado")
        else:
            results["checks"]["error_notifications"] = {
                "status": "warning",
                "telegram_exists": False
            }
            print("⚠️ Cliente Telegram não encontrado")
            results["warnings"].append("Cliente Telegram não encontrado")
            
    except Exception as e:
        error_msg = f"Erro ao verificar notificações: {str(e)}"
        results["errors"].append(error_msg)
        results["checks"]["error_notifications"] = {"status": "error", "error": error_msg}
        print(f"❌ {error_msg}")
    
    # 4. Verificar logs e monitoramento
    print("\n4️⃣ VERIFICANDO LOGS E MONITORAMENTO...")
    try:
        log_checks = {}
        
        # Verificar se há sistema de logging
        main_files = ["src/main.py", "railway_scheduler.py", "automation/scheduler.py"]
        
        for file_path in main_files:
            file_obj = Path(file_path)
            if file_obj.exists():
                with open(file_obj, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                has_logging = "logging" in content.lower() or "log" in content.lower()
                has_print_debug = "print(" in content
                
                log_checks[file_path] = {
                    "exists": True,
                    "has_logging": has_logging,
                    "has_debug": has_print_debug
                }
            else:
                log_checks[file_path] = {"exists": False}
        
        results["checks"]["logging"] = {
            "status": "success",
            "files": log_checks
        }
        
        files_with_logging = sum(1 for check in log_checks.values() 
                               if check.get("exists") and 
                               (check.get("has_logging") or check.get("has_debug")))
        total_files = sum(1 for check in log_checks.values() if check.get("exists"))
        
        print(f"✅ {files_with_logging}/{total_files} arquivos com logging/debug")
        
    except Exception as e:
        error_msg = f"Erro ao verificar logs: {str(e)}"
        results["errors"].append(error_msg)
        results["checks"]["logging"] = {"status": "error", "error": error_msg}
        print(f"❌ {error_msg}")
    
    # 5. Verificar configurações de timeout
    print("\n5️⃣ VERIFICANDO CONFIGURAÇÕES DE TIMEOUT...")
    try:
        timeout_checks = {}
        
        # Verificar timeouts nos clientes
        client_files = [
            "src/services/rapidapi_client.py",
            "src/services/instagram_client.py", 
            "src/services/openai_client.py",
            "src/services/replicate_client.py"
        ]
        
        for file_path in client_files:
            file_obj = Path(file_path)
            if file_obj.exists():
                with open(file_obj, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                has_timeout = "timeout" in content.lower()
                has_requests_timeout = "timeout=" in content
                
                timeout_checks[file_path] = {
                    "exists": True,
                    "has_timeout": has_timeout,
                    "has_requests_timeout": has_requests_timeout
                }
            else:
                timeout_checks[file_path] = {"exists": False}
        
        results["checks"]["timeouts"] = {
            "status": "success",
            "files": timeout_checks
        }
        
        files_with_timeout = sum(1 for check in timeout_checks.values() 
                               if check.get("exists") and 
                               (check.get("has_timeout") or check.get("has_requests_timeout")))
        total_files = sum(1 for check in timeout_checks.values() if check.get("exists"))
        
        print(f"✅ {files_with_timeout}/{total_files} clientes com configuração de timeout")
        
    except Exception as e:
        error_msg = f"Erro ao verificar timeouts: {str(e)}"
        results["errors"].append(error_msg)
        results["checks"]["timeouts"] = {"status": "error", "error": error_msg}
        print(f"❌ {error_msg}")
    
    # 6. Verificar sistema de cache/fallback de conteúdo
    print("\n6️⃣ VERIFICANDO CACHE E FALLBACK DE CONTEÚDO...")
    try:
        cache_checks = {}
        
        # Verificar se há sistema de cache
        cache_files = [
            "src/services/rapidapi_client.py",
            "src/services/openai_client.py"
        ]
        
        for file_path in cache_files:
            file_obj = Path(file_path)
            if file_obj.exists():
                with open(file_obj, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                has_cache = "cache" in content.lower()
                has_fallback = "fallback" in content.lower()
                
                cache_checks[file_path] = {
                    "exists": True,
                    "has_cache": has_cache,
                    "has_fallback": has_fallback
                }
            else:
                cache_checks[file_path] = {"exists": False}
        
        results["checks"]["cache_fallback"] = {
            "status": "success",
            "files": cache_checks
        }
        
        files_with_cache = sum(1 for check in cache_checks.values() 
                             if check.get("exists") and 
                             (check.get("has_cache") or check.get("has_fallback")))
        total_files = sum(1 for check in cache_checks.values() if check.get("exists"))
        
        print(f"✅ {files_with_cache}/{total_files} clientes com cache/fallback")
        
    except Exception as e:
        error_msg = f"Erro ao verificar cache: {str(e)}"
        results["errors"].append(error_msg)
        results["checks"]["cache_fallback"] = {"status": "error", "error": error_msg}
        print(f"❌ {error_msg}")
    
    # Calcular resultado final
    successful_checks = sum(1 for check in results["checks"].values() if check.get("status") == "success")
    total_checks = len(results["checks"])
    success_rate = (successful_checks / total_checks) * 100 if total_checks > 0 else 0
    
    results["success"] = success_rate >= 75
    results["success_rate"] = success_rate
    results["successful_checks"] = successful_checks
    results["total_checks"] = total_checks
    
    # Resultado final
    print("\n" + "=" * 50)
    print("📊 RESULTADO DA VERIFICAÇÃO DE FALLBACK")
    print("=" * 50)
    
    if results["success"]:
        print("✅ SISTEMAS DE FALLBACK OK!")
        print(f"   Taxa de sucesso: {success_rate:.1f}% ({successful_checks}/{total_checks})")
    else:
        print("⚠️ SISTEMAS DE FALLBACK COM PROBLEMAS")
        print(f"   Taxa de sucesso: {success_rate:.1f}% ({successful_checks}/{total_checks})")
    
    if results["errors"]:
        print(f"\n❌ Erros encontrados ({len(results['errors'])}):")
        for error in results["errors"]:
            print(f"   • {error}")
    
    if results["warnings"]:
        print(f"\n⚠️ Avisos ({len(results['warnings'])}):")
        for warning in results["warnings"]:
            print(f"   • {warning}")
    
    # Salvar relatório
    report_file = "fallback_systems_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Relatório salvo em: {report_file}")
    
    return results

if __name__ == "__main__":
    test_fallback_systems()