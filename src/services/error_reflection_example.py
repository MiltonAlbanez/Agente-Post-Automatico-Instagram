"""
Exemplo de Integração do Sistema de Reflexão de Erros
Demonstra como aplicar o sistema nas funções existentes.
"""

from .error_reflection_integration import (
    smart_error_handler, 
    with_error_reflection, 
    error_reflection_context,
    analyze_error,
    get_function_health
)


# Exemplo 1: Decorator simples
@with_error_reflection(critical=True, retry_attempts=2)
def upload_media_to_instagram(file_path: str, caption: str):
    """
    Exemplo de função crítica com retry automático.
    """
    # Simulação de upload que pode falhar
    import random
    if random.random() < 0.3:  # 30% chance de falha
        raise ConnectionError("Falha na conexão com Instagram")
    
    print(f"Upload realizado: {file_path}")
    return {"status": "success", "media_id": "123456"}


# Exemplo 2: Decorator avançado com fallback
def fallback_upload(file_path: str, caption: str):
    """Função de fallback para upload."""
    print(f"Usando método alternativo para upload: {file_path}")
    return {"status": "fallback_success", "media_id": "fallback_123"}


@smart_error_handler(
    function_name="instagram_upload_with_fallback",
    critical=True,
    retry_attempts=1,
    fallback_function=fallback_upload,
    auto_generate_plan=True
)
def upload_with_fallback(file_path: str, caption: str):
    """
    Upload com fallback automático.
    """
    # Simulação de falha
    raise Exception("API Instagram indisponível")


# Exemplo 3: Context manager para blocos de código
def process_multiple_uploads(file_list: list):
    """
    Processa múltiplos uploads usando context manager.
    """
    with error_reflection_context("batch_upload_process", critical=True) as ctx:
        results = []
        
        for file_path in file_list:
            try:
                result = upload_media_to_instagram(file_path, "Caption automática")
                results.append(result)
            except Exception as e:
                print(f"Erro no upload de {file_path}: {e}")
                # Erro já foi registrado pelo decorator
                continue
        
        return results


# Exemplo 4: Análise manual de erro
def analyze_specific_error():
    """
    Exemplo de análise manual de um erro específico.
    """
    # Simula um erro conhecido
    error_hash = "abc123def456"  # Hash de um erro real
    
    analysis = analyze_error(error_hash)
    
    print("=== ANÁLISE DETALHADA DO ERRO ===")
    print(f"Hash: {analysis['error_hash']}")
    print(f"Status: {analysis['context_analysis'].get('status', 'unknown')}")
    print(f"Nível de Risco: {analysis['risk_assessment']['risk_level']}")
    
    print("\nPróximos Passos:")
    for step in analysis['next_steps']:
        print(f"  • {step}")
    
    return analysis


# Exemplo 5: Relatório de saúde das funções
def generate_health_report():
    """
    Gera relatório de saúde das funções monitoradas.
    """
    # Relatório geral
    general_report = get_function_health()
    
    print("=== RELATÓRIO DE SAÚDE GERAL ===")
    print(f"Total de funções monitoradas: {general_report['total_functions']}")
    
    for func_name, stats in general_report['functions'].items():
        print(f"\n{func_name}:")
        print(f"  • Taxa de sucesso: {stats['success_rate']}%")
        print(f"  • Status: {stats['health_status']}")
        print(f"  • Total de chamadas: {stats['total_calls']}")
    
    # Relatório específico de uma função
    specific_report = get_function_health("upload_media_to_instagram")
    if specific_report:
        print(f"\n=== DETALHES: {specific_report['function_name']} ===")
        print(f"Taxa de sucesso: {specific_report['success_rate']}%")
        print(f"Tentativas de retry: {specific_report['retry_count']}")
        print(f"Status de saúde: {specific_report['health_status']}")
    
    return general_report


# Exemplo 6: Integração com RapidAPI (baseado no problema anterior)
@with_error_reflection(critical=False, retry_attempts=1)
def collect_hashtags_with_reflection(query: str):
    """
    Coleta hashtags com sistema de reflexão integrado.
    """
    try:
        # Simulação de chamada RapidAPI
        import random
        if random.random() < 0.4:  # 40% chance de erro 403
            raise Exception("403 Forbidden - RapidAPI quota exceeded")
        
        return ["#hashtag1", "#hashtag2", "#hashtag3"]
        
    except Exception as e:
        # O sistema de reflexão já registrou o erro
        # Aqui implementamos o fallback conhecido
        if "403" in str(e) or "Forbidden" in str(e):
            print("Ativando fallback para RapidAPI...")
            return ["#fallback", "#hashtag", "#tema"]
        
        # Re-levanta outros erros
        raise


# Exemplo 7: Função para demonstrar o sistema completo
def demonstrate_error_reflection_system():
    """
    Demonstra o sistema completo de reflexão de erros.
    """
    print("=== DEMONSTRAÇÃO DO SISTEMA DE REFLEXÃO DE ERROS ===\n")
    
    # 1. Testa função com retry
    print("1. Testando função com retry automático...")
    try:
        result = upload_media_to_instagram("test.jpg", "Teste")
        print(f"Sucesso: {result}")
    except Exception as e:
        print(f"Falha final: {e}")
    
    print("\n" + "-" * 50 + "\n")
    
    # 2. Testa função com fallback
    print("2. Testando função com fallback...")
    try:
        result = upload_with_fallback("test2.jpg", "Teste com fallback")
        print(f"Resultado: {result}")
    except Exception as e:
        print(f"Falha: {e}")
    
    print("\n" + "-" * 50 + "\n")
    
    # 3. Testa context manager
    print("3. Testando context manager...")
    files = ["file1.jpg", "file2.jpg", "file3.jpg"]
    results = process_multiple_uploads(files)
    print(f"Resultados do batch: {len(results)} sucessos")
    
    print("\n" + "-" * 50 + "\n")
    
    # 4. Testa coleta de hashtags com reflexão
    print("4. Testando coleta de hashtags...")
    try:
        hashtags = collect_hashtags_with_reflection("motivação")
        print(f"Hashtags coletadas: {hashtags}")
    except Exception as e:
        print(f"Erro na coleta: {e}")
    
    print("\n" + "-" * 50 + "\n")
    
    # 5. Gera relatório de saúde
    print("5. Gerando relatório de saúde...")
    generate_health_report()
    
    print("\n=== DEMONSTRAÇÃO CONCLUÍDA ===")


if __name__ == "__main__":
    # Executa demonstração
    demonstrate_error_reflection_system()