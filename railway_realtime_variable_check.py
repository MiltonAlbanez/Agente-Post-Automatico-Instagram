#!/usr/bin/env python3
"""
Verificação em Tempo Real das Variáveis Railway
Script para executar no Railway e verificar carregamento de variáveis
"""

import os
import json
import sys
from datetime import datetime

def check_railway_variables():
    """Verificar variáveis no ambiente Railway"""
    
    print("🔍 VERIFICAÇÃO EM TEMPO REAL - RAILWAY VARIABLES")
    print("=" * 60)
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print(f"🌍 Ambiente: {os.getenv('RAILWAY_ENVIRONMENT', 'unknown')}")
    print(f"🐍 Python: {sys.version}")
    print("=" * 60)
    
    # Variáveis críticas que o código espera (baseado na busca)
    critical_variables = [
        "INSTAGRAM_BUSINESS_ACCOUNT_ID",
        "INSTAGRAM_ACCESS_TOKEN", 
        "TELEGRAM_CHAT_ID",
        "TELEGRAM_BOT_TOKEN",
        "RAPIDAPI_KEY",
        "RAPIDAPI_HOST",
        "OPENAI_API_KEY",
        "DATABASE_URL",
        "SUPABASE_URL",
        "SUPABASE_SERVICE_KEY"
    ]
    
    # Variáveis que podem estar configuradas em português (baseado nas imagens)
    portuguese_variables = [
        "TOKEN_DE_ACESSO_DO_INSTAGRAM",
        "ID_DA_CONTA_COMERCIAL_DO_INSTAGRAM", 
        "VERIFICAÇÕES_DE_ENQUETE_MÁXIMO",
        "INTERVALO_DE_ENQUETE_DO_INSTAGRAM",
        "TEMPO_LIMITE_DO_INSTAGRAM",
        "AUTOCMD"
    ]
    
    # Outras variáveis possíveis
    other_variables = [
        "RAPIDAPI_ALT_HOSTS",
        "REPLICATE_TOKEN",
        "SUPABASE_BUCKET",
        "SUPABASE_ANON_KEY",
        "POSTGRES_DSN",
        "DATABASE_PUBLIC_URL"
    ]
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv('RAILWAY_ENVIRONMENT', 'unknown'),
        "critical_variables": {},
        "portuguese_variables": {},
        "other_variables": {},
        "all_env_variables": {},
        "summary": {}
    }
    
    print("\n🎯 VARIÁVEIS CRÍTICAS (esperadas pelo código):")
    print("-" * 50)
    critical_found = 0
    for var in critical_variables:
        value = os.getenv(var)
        exists = value is not None
        masked_value = "***PRESENTE***" if exists and value else "❌ AUSENTE"
        
        print(f"  {var:<35} | {masked_value}")
        
        results["critical_variables"][var] = {
            "exists": exists,
            "has_value": bool(value) if exists else False,
            "length": len(value) if value else 0
        }
        
        if exists and value:
            critical_found += 1
    
    print(f"\n✅ Variáveis críticas encontradas: {critical_found}/{len(critical_variables)}")
    
    print("\n🇧🇷 VARIÁVEIS EM PORTUGUÊS (vistas nas imagens):")
    print("-" * 50)
    portuguese_found = 0
    for var in portuguese_variables:
        value = os.getenv(var)
        exists = value is not None
        masked_value = "***PRESENTE***" if exists and value else "❌ AUSENTE"
        
        print(f"  {var:<35} | {masked_value}")
        
        results["portuguese_variables"][var] = {
            "exists": exists,
            "has_value": bool(value) if exists else False,
            "length": len(value) if value else 0
        }
        
        if exists and value:
            portuguese_found += 1
    
    print(f"\n🇧🇷 Variáveis em português encontradas: {portuguese_found}/{len(portuguese_variables)}")
    
    print("\n🔧 OUTRAS VARIÁVEIS:")
    print("-" * 50)
    other_found = 0
    for var in other_variables:
        value = os.getenv(var)
        exists = value is not None
        masked_value = "***PRESENTE***" if exists and value else "❌ AUSENTE"
        
        print(f"  {var:<35} | {masked_value}")
        
        results["other_variables"][var] = {
            "exists": exists,
            "has_value": bool(value) if exists else False,
            "length": len(value) if value else 0
        }
        
        if exists and value:
            other_found += 1
    
    print(f"\n🔧 Outras variáveis encontradas: {other_found}/{len(other_variables)}")
    
    # Listar TODAS as variáveis de ambiente
    print("\n🌍 TODAS AS VARIÁVEIS DE AMBIENTE:")
    print("-" * 50)
    all_vars = dict(os.environ)
    
    # Filtrar variáveis do sistema que não são relevantes
    relevant_vars = {}
    system_prefixes = ['PYTHON', 'PATH', 'HOME', 'USER', 'SHELL', 'TERM', 'PWD', 'OLDPWD', 'SHLVL', '_']
    
    for key, value in all_vars.items():
        # Incluir se não começa com prefixos do sistema OU se contém palavras-chave relevantes
        if not any(key.startswith(prefix) for prefix in system_prefixes) or \
           any(keyword in key.upper() for keyword in ['INSTAGRAM', 'TELEGRAM', 'RAPID', 'OPENAI', 'DATABASE', 'SUPABASE']):
            relevant_vars[key] = value
            
            # Mascarar valores sensíveis
            if len(value) > 10:
                masked = f"{value[:3]}...{value[-3:]} (len:{len(value)})"
            else:
                masked = "***" if value else "EMPTY"
            
            print(f"  {key:<35} | {masked}")
    
    results["all_env_variables"] = {k: {"length": len(v), "has_value": bool(v)} for k, v in relevant_vars.items()}
    
    # Resumo da análise
    total_critical = len(critical_variables)
    total_portuguese = len(portuguese_variables)
    total_other = len(other_variables)
    total_all = len(relevant_vars)
    
    results["summary"] = {
        "critical_variables_found": critical_found,
        "critical_variables_total": total_critical,
        "critical_variables_percentage": round((critical_found / total_critical) * 100, 1),
        "portuguese_variables_found": portuguese_found,
        "portuguese_variables_total": total_portuguese,
        "portuguese_variables_percentage": round((portuguese_found / total_portuguese) * 100, 1),
        "other_variables_found": other_found,
        "other_variables_total": total_other,
        "total_relevant_variables": total_all,
        "environment_status": "RAILWAY" if os.getenv('RAILWAY_ENVIRONMENT') else "LOCAL"
    }
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DA ANÁLISE:")
    print("=" * 60)
    print(f"🎯 Variáveis críticas: {critical_found}/{total_critical} ({results['summary']['critical_variables_percentage']}%)")
    print(f"🇧🇷 Variáveis português: {portuguese_found}/{total_portuguese} ({results['summary']['portuguese_variables_percentage']}%)")
    print(f"🔧 Outras variáveis: {other_found}/{total_other}")
    print(f"🌍 Total relevantes: {total_all}")
    print(f"📍 Ambiente: {results['summary']['environment_status']}")
    
    # Diagnóstico
    print("\n🔍 DIAGNÓSTICO:")
    print("-" * 30)
    
    if critical_found == 0:
        print("🚨 CRÍTICO: Nenhuma variável crítica encontrada!")
        print("   → Sistema não pode funcionar")
        print("   → Verificar configuração no Railway")
    elif critical_found < total_critical:
        print(f"⚠️  PARCIAL: {total_critical - critical_found} variáveis críticas ausentes")
        print("   → Sistema pode falhar em algumas funcionalidades")
    else:
        print("✅ SUCESSO: Todas as variáveis críticas presentes")
    
    if portuguese_found > 0:
        print(f"🇧🇷 ATENÇÃO: {portuguese_found} variáveis em português encontradas")
        print("   → Código espera nomes em inglês")
        print("   → Pode causar incompatibilidade")
    
    # Salvar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"railway_realtime_check_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Resultados salvos: {filename}")
    except Exception as e:
        print(f"\n❌ Erro ao salvar: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 VERIFICAÇÃO CONCLUÍDA")
    print("=" * 60)
    
    return results

def test_specific_variables():
    """Testar variáveis específicas mencionadas nas imagens"""
    print("\n🧪 TESTE ESPECÍFICO - VARIÁVEIS DAS IMAGENS")
    print("=" * 60)
    
    # Mapear variáveis português → inglês
    variable_mapping = {
        "TOKEN_DE_ACESSO_DO_INSTAGRAM": "INSTAGRAM_ACCESS_TOKEN",
        "ID_DA_CONTA_COMERCIAL_DO_INSTAGRAM": "INSTAGRAM_BUSINESS_ACCOUNT_ID"
    }
    
    for pt_var, en_var in variable_mapping.items():
        pt_value = os.getenv(pt_var)
        en_value = os.getenv(en_var)
        
        print(f"\n🔄 Mapeamento: {pt_var} → {en_var}")
        print(f"   🇧🇷 Português: {'✅ PRESENTE' if pt_value else '❌ AUSENTE'}")
        print(f"   🇺🇸 Inglês:    {'✅ PRESENTE' if en_value else '❌ AUSENTE'}")
        
        if pt_value and not en_value:
            print(f"   ⚠️  PROBLEMA: Variável existe em português mas não em inglês!")
        elif en_value and not pt_value:
            print(f"   ✅ OK: Variável correta em inglês")
        elif pt_value and en_value:
            print(f"   🤔 DUPLICADA: Existe em ambos os idiomas")
        else:
            print(f"   ❌ AUSENTE: Não existe em nenhum idioma")

def main():
    """Função principal"""
    try:
        # Verificação principal
        results = check_railway_variables()
        
        # Teste específico
        test_specific_variables()
        
        # Status final
        critical_percentage = results["summary"]["critical_variables_percentage"]
        
        if critical_percentage == 100:
            print("\n🎉 STATUS: SISTEMA PRONTO PARA FUNCIONAR")
            exit_code = 0
        elif critical_percentage >= 50:
            print("\n⚠️  STATUS: SISTEMA PARCIALMENTE CONFIGURADO")
            exit_code = 1
        else:
            print("\n🚨 STATUS: SISTEMA NÃO PODE FUNCIONAR")
            exit_code = 2
        
        return exit_code
        
    except Exception as e:
        print(f"\n❌ ERRO DURANTE VERIFICAÇÃO: {e}")
        import traceback
        traceback.print_exc()
        return 3

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)