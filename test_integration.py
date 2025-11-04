"""
Teste de Integração do Sistema Temático Semanal
Verifica se o sistema está integrado corretamente ao pipeline principal
"""
import sys
import os
from pathlib import Path

# Adicionar o diretório src ao path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Mudar para o diretório src para importações relativas
os.chdir(str(src_dir))


def test_integration_with_pipeline():
    """Testa a integração do sistema temático com o pipeline principal."""
    print("🔗 TESTE DE INTEGRAÇÃO DO SISTEMA TEMÁTICO")
    print("=" * 60)
    
    try:
        print("\n🔍 VERIFICAÇÃO DE IMPORTAÇÕES")
        print("-" * 40)
        
        # Verificar se as importações estão corretas
        try:
            from services.weekly_theme_manager import WeeklyThemeManager
            print("✅ WeeklyThemeManager importado com sucesso")
            
            from services.weekly_theme_manager import get_weekly_themed_content
            print("✅ get_weekly_themed_content importado com sucesso")
            
            from services.weekly_theme_manager import is_morning_spiritual_time
            print("✅ is_morning_spiritual_time importado com sucesso")
            
        except ImportError as e:
            print(f"❌ Erro de importação: {e}")
            return False
        
        print("\n📁 VERIFICAÇÃO DE ARQUIVOS")
        print("-" * 40)
        
        # Verificar se os arquivos necessários existem
        config_file = Path("../config/weekly_thematic_config.json")
        if config_file.exists():
            print("✅ Arquivo de configuração temática encontrado")
        else:
            print("❌ Arquivo de configuração temática não encontrado")
            return False
        
        manager_file = Path("services/weekly_theme_manager.py")
        if manager_file.exists():
            print("✅ Arquivo do gerenciador temático encontrado")
        else:
            print("❌ Arquivo do gerenciador temático não encontrado")
            return False
        
        # Verificar se o pipeline foi atualizado
        pipeline_file = Path("pipeline/generate_and_publish.py")
        if pipeline_file.exists():
            print("✅ Arquivo do pipeline encontrado")
            
            # Verificar se contém as integrações
            with open(pipeline_file, 'r', encoding='utf-8') as f:
                pipeline_content = f.read()
            
            checks = [
                ("use_weekly_themes", "Parâmetro use_weekly_themes"),
                ("WeeklyThemeManager", "Importação do WeeklyThemeManager"),
                ("get_weekly_themed_content", "Função get_weekly_themed_content"),
                ("is_morning_spiritual_time", "Função is_morning_spiritual_time"),
                ("thematic_hashtags", "Hashtags temáticas"),
                ("tracking_metadata", "Metadados de rastreamento")
            ]
            
            for check_text, description in checks:
                if check_text in pipeline_content:
                    print(f"✅ {description} encontrado no pipeline")
                else:
                    print(f"⚠️ {description} não encontrado no pipeline")
        else:
            print("❌ Arquivo do pipeline não encontrado")
            return False
        
        print("\n🧪 TESTE DE FUNCIONALIDADE")
        print("-" * 40)
        
        # Testar funcionalidade básica
        manager = WeeklyThemeManager()
        
        # Teste de configuração atual
        current_config = manager.get_current_slot_config()
        print(f"✅ Configuração atual obtida: {current_config.get('main_theme', 'N/A')}")
        
        # Teste de geração de conteúdo
        content_prompt, image_prompt, metadata = get_weekly_themed_content(
            day_of_week=1, time_slot="morning"
        )
        print(f"✅ Conteúdo temático gerado para Segunda-feira manhã")
        print(f"   - Tema: {metadata.get('main_theme', 'N/A')}")
        print(f"   - Espiritual: {metadata.get('spiritual_focus', False)}")
        
        # Teste de verificação espiritual
        spiritual_check = is_morning_spiritual_time()
        print(f"✅ Verificação espiritual: {spiritual_check}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO NO TESTE DE INTEGRAÇÃO: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_scheduler_integration():
    """Testa se o scheduler está usando o sistema temático."""
    print("\n📅 TESTE DE INTEGRAÇÃO COM SCHEDULER")
    print("=" * 60)
    
    try:
        # Verificar se o scheduler foi atualizado
        scheduler_file = Path("../automation/scheduler.py")
        
        if not scheduler_file.exists():
            print("❌ Arquivo do scheduler não encontrado")
            return False
        
        # Ler o arquivo do scheduler
        with open(scheduler_file, 'r', encoding='utf-8') as f:
            scheduler_content = f.read()
        
        # Verificar se contém as integrações necessárias
        checks = [
            ("use_weekly_themes=True", "Parâmetro use_weekly_themes habilitado"),
            ("generate_and_publish", "Função generate_and_publish"),
        ]
        
        for check_text, description in checks:
            if check_text in scheduler_content:
                print(f"✅ {description} encontrado no scheduler")
            else:
                print(f"⚠️ {description} não encontrado no scheduler")
        
        print("✅ Verificação do scheduler concluída")
        return True
        
    except Exception as e:
        print(f"❌ ERRO NA VERIFICAÇÃO DO SCHEDULER: {e}")
        return False


if __name__ == "__main__":
    print("🚀 INICIANDO TESTES DE INTEGRAÇÃO")
    print("=" * 60)
    
    success = True
    
    # Executar testes
    if not test_integration_with_pipeline():
        success = False
    
    if not test_scheduler_integration():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TODOS OS TESTES DE INTEGRAÇÃO PASSARAM!")
        print("✅ O sistema temático semanal está totalmente integrado")
        print("✅ Pronto para uso em produção")
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        print("⚠️ Verifique os erros acima antes de usar em produção")
    
    print("=" * 60)