#!/usr/bin/env python3
"""
Correção Automática do Ambiente Telegram
Corrige o carregamento das variáveis de ambiente do Telegram
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TelegramEnvironmentFixer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.fixes_applied = []
        
    def load_credentials_from_files(self):
        """Carregar credenciais dos arquivos de configuração"""
        logger.info("🔍 Carregando credenciais dos arquivos de configuração...")
        
        credentials = {
            "bot_token": None,
            "chat_id": None,
            "source": None
        }
        
        # 1. Tentar carregar do railway_env_commands.txt
        railway_env_path = self.project_root / "railway_env_commands.txt"
        if railway_env_path.exists():
            try:
                with open(railway_env_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Procurar por variáveis do Telegram
                bot_token_match = re.search(r'TELEGRAM_BOT_TOKEN[=\s]+"([^"]+)"', content)
                chat_id_match = re.search(r'TELEGRAM_CHAT_ID[=\s]+"([^"]+)"', content)
                
                if bot_token_match and chat_id_match:
                    credentials["bot_token"] = bot_token_match.group(1)
                    credentials["chat_id"] = chat_id_match.group(1)
                    credentials["source"] = "railway_env_commands.txt"
                    logger.info("✅ Credenciais encontradas em railway_env_commands.txt")
                    return credentials
                    
            except Exception as e:
                logger.warning(f"⚠️ Erro ao ler railway_env_commands.txt: {str(e)}")
                
        # 2. Tentar carregar do CREDENCIAIS_PERMANENTES.json
        credentials_path = self.project_root / "CREDENCIAIS_PERMANENTES.json"
        if credentials_path.exists():
            try:
                with open(credentials_path, 'r', encoding='utf-8') as f:
                    creds_data = json.load(f)
                
                if creds_data.get("TELEGRAM_BOT_TOKEN") and creds_data.get("TELEGRAM_CHAT_ID"):
                    credentials["bot_token"] = creds_data["TELEGRAM_BOT_TOKEN"]
                    credentials["chat_id"] = creds_data["TELEGRAM_CHAT_ID"]
                    credentials["source"] = "CREDENCIAIS_PERMANENTES.json"
                    logger.info("✅ Credenciais encontradas em CREDENCIAIS_PERMANENTES.json")
                    return credentials
                    
            except Exception as e:
                logger.warning(f"⚠️ Erro ao ler CREDENCIAIS_PERMANENTES.json: {str(e)}")
                
        # 3. Tentar carregar do config/notification_config.json
        notification_config_path = self.project_root / "config" / "notification_config.json"
        if notification_config_path.exists():
            try:
                with open(notification_config_path, 'r', encoding='utf-8') as f:
                    notification_config = json.load(f)
                
                telegram_config = notification_config.get("telegram", {})
                if telegram_config.get("bot_token") and telegram_config.get("chat_id"):
                    credentials["bot_token"] = telegram_config["bot_token"]
                    credentials["chat_id"] = telegram_config["chat_id"]
                    credentials["source"] = "config/notification_config.json"
                    logger.info("✅ Credenciais encontradas em config/notification_config.json")
                    return credentials
                    
            except Exception as e:
                logger.warning(f"⚠️ Erro ao ler config/notification_config.json: {str(e)}")
                
        logger.error("❌ Nenhuma credencial válida encontrada nos arquivos de configuração")
        return credentials
        
    def create_env_file(self, credentials):
        """Criar arquivo .env com as credenciais"""
        logger.info("📝 Criando arquivo .env...")
        
        env_path = self.project_root / ".env"
        
        # Ler .env existente se houver
        existing_env = {}
        if env_path.exists():
            try:
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            existing_env[key.strip()] = value.strip()
            except Exception as e:
                logger.warning(f"⚠️ Erro ao ler .env existente: {str(e)}")
                
        # Atualizar com credenciais do Telegram
        existing_env["TELEGRAM_BOT_TOKEN"] = credentials["bot_token"]
        existing_env["TELEGRAM_CHAT_ID"] = credentials["chat_id"]
        
        # Adicionar outras variáveis importantes se não existirem
        default_vars = {
            "TZ": "America/Sao_Paulo",
            "DRY_RUN": "false",
            "SIMULATION_MODE": "false",
            "PRODUCTION_MODE": "true",
            "REAL_POSTING": "true"
        }
        
        for key, value in default_vars.items():
            if key not in existing_env:
                existing_env[key] = value
                
        # Escrever arquivo .env
        try:
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write("# Variáveis de Ambiente - Agente Post Instagram\n")
                f.write(f"# Gerado automaticamente em {datetime.now().isoformat()}\n\n")
                
                # Telegram
                f.write("# Telegram Configuration\n")
                f.write(f"TELEGRAM_BOT_TOKEN={existing_env['TELEGRAM_BOT_TOKEN']}\n")
                f.write(f"TELEGRAM_CHAT_ID={existing_env['TELEGRAM_CHAT_ID']}\n\n")
                
                # Outras variáveis
                f.write("# System Configuration\n")
                for key, value in existing_env.items():
                    if not key.startswith("TELEGRAM_"):
                        f.write(f"{key}={value}\n")
                        
            logger.info(f"✅ Arquivo .env criado: {env_path}")
            self.fixes_applied.append({
                "type": "ENV_FILE_CREATED",
                "description": f"Arquivo .env criado com credenciais do Telegram",
                "path": str(env_path)
            })
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar arquivo .env: {str(e)}")
            return False
            
    def update_config_py(self):
        """Atualizar src/config.py para carregar .env automaticamente"""
        logger.info("🔧 Atualizando src/config.py para carregar .env...")
        
        config_path = self.project_root / "src" / "config.py"
        if not config_path.exists():
            logger.warning("⚠️ Arquivo src/config.py não encontrado")
            return False
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Verificar se já tem carregamento do .env
            if "load_dotenv" in content:
                logger.info("✅ src/config.py já carrega .env")
                return True
                
            # Adicionar import e carregamento do .env
            new_content = content
            
            # Adicionar import no topo
            if "from dotenv import load_dotenv" not in content:
                import_section = "import os\nfrom pathlib import Path\nfrom dotenv import load_dotenv\n"
                new_content = new_content.replace("import os\nfrom pathlib import Path", import_section)
                
            # Adicionar carregamento do .env no início da função get_config
            if "load_dotenv()" not in content:
                get_config_start = "def get_config():"
                if get_config_start in new_content:
                    replacement = f"""{get_config_start}
    # Carregar variáveis do arquivo .env
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    """
                    new_content = new_content.replace(get_config_start, replacement)
                    
            # Salvar arquivo atualizado
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            logger.info("✅ src/config.py atualizado para carregar .env")
            self.fixes_applied.append({
                "type": "CONFIG_PY_UPDATED",
                "description": "src/config.py atualizado para carregar arquivo .env",
                "path": str(config_path)
            })
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar src/config.py: {str(e)}")
            return False
            
    def install_python_dotenv(self):
        """Instalar python-dotenv se necessário"""
        logger.info("📦 Verificando instalação do python-dotenv...")
        
        try:
            import dotenv
            logger.info("✅ python-dotenv já está instalado")
            return True
        except ImportError:
            logger.info("📦 Instalando python-dotenv...")
            
            try:
                import subprocess
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", "python-dotenv"
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    logger.info("✅ python-dotenv instalado com sucesso")
                    self.fixes_applied.append({
                        "type": "PYTHON_DOTENV_INSTALLED",
                        "description": "Pacote python-dotenv instalado",
                        "output": result.stdout
                    })
                    return True
                else:
                    logger.error(f"❌ Erro ao instalar python-dotenv: {result.stderr}")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Erro ao instalar python-dotenv: {str(e)}")
                return False
                
    def update_requirements_txt(self):
        """Atualizar requirements.txt para incluir python-dotenv"""
        logger.info("📝 Atualizando requirements.txt...")
        
        requirements_path = self.project_root / "requirements.txt"
        
        # Ler requirements existente
        existing_requirements = []
        if requirements_path.exists():
            try:
                with open(requirements_path, 'r', encoding='utf-8') as f:
                    existing_requirements = [line.strip() for line in f if line.strip()]
            except Exception as e:
                logger.warning(f"⚠️ Erro ao ler requirements.txt: {str(e)}")
                
        # Verificar se python-dotenv já está listado
        has_dotenv = any("python-dotenv" in req for req in existing_requirements)
        
        if not has_dotenv:
            existing_requirements.append("python-dotenv>=1.0.0")
            
            try:
                with open(requirements_path, 'w', encoding='utf-8') as f:
                    for req in existing_requirements:
                        f.write(f"{req}\n")
                        
                logger.info("✅ requirements.txt atualizado com python-dotenv")
                self.fixes_applied.append({
                    "type": "REQUIREMENTS_UPDATED",
                    "description": "requirements.txt atualizado com python-dotenv",
                    "path": str(requirements_path)
                })
                return True
                
            except Exception as e:
                logger.error(f"❌ Erro ao atualizar requirements.txt: {str(e)}")
                return False
        else:
            logger.info("✅ python-dotenv já está em requirements.txt")
            return True
            
    def test_environment_loading(self):
        """Testar se as variáveis de ambiente estão sendo carregadas corretamente"""
        logger.info("🧪 Testando carregamento das variáveis de ambiente...")
        
        try:
            # Limpar variáveis de ambiente atuais
            if "TELEGRAM_BOT_TOKEN" in os.environ:
                del os.environ["TELEGRAM_BOT_TOKEN"]
            if "TELEGRAM_CHAT_ID" in os.environ:
                del os.environ["TELEGRAM_CHAT_ID"]
                
            # Importar e testar config
            sys.path.insert(0, str(self.project_root / "src"))
            
            # Recarregar módulo config
            if "config" in sys.modules:
                del sys.modules["config"]
                
            from config import get_config
            
            config = get_config()
            
            bot_token = config.get("TELEGRAM_BOT_TOKEN")
            chat_id = config.get("TELEGRAM_CHAT_ID")
            
            if bot_token and chat_id:
                logger.info("✅ Variáveis de ambiente carregadas com sucesso")
                logger.info(f"Bot Token: {bot_token[:20]}...")
                logger.info(f"Chat ID: {chat_id}")
                
                self.fixes_applied.append({
                    "type": "ENVIRONMENT_TEST_SUCCESS",
                    "description": "Variáveis de ambiente carregadas corretamente",
                    "bot_token_length": len(bot_token),
                    "chat_id": chat_id
                })
                return True
            else:
                logger.error("❌ Variáveis de ambiente não foram carregadas")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao testar carregamento: {str(e)}")
            return False
            
    def run_complete_fix(self):
        """Executar correção completa"""
        logger.info("🚀 Iniciando correção completa do ambiente Telegram...")
        
        success_count = 0
        total_steps = 6
        
        try:
            # 1. Carregar credenciais dos arquivos
            credentials = self.load_credentials_from_files()
            if not credentials["bot_token"] or not credentials["chat_id"]:
                logger.error("❌ Não foi possível encontrar credenciais válidas")
                return False
            success_count += 1
            
            # 2. Instalar python-dotenv
            if self.install_python_dotenv():
                success_count += 1
                
            # 3. Atualizar requirements.txt
            if self.update_requirements_txt():
                success_count += 1
                
            # 4. Criar arquivo .env
            if self.create_env_file(credentials):
                success_count += 1
                
            # 5. Atualizar src/config.py
            if self.update_config_py():
                success_count += 1
                
            # 6. Testar carregamento
            if self.test_environment_loading():
                success_count += 1
                
            # Resultado final
            success_rate = (success_count / total_steps) * 100
            
            if success_count == total_steps:
                logger.info("🎉 Correção completa realizada com sucesso!")
                return True
            else:
                logger.warning(f"⚠️ Correção parcial: {success_count}/{total_steps} passos concluídos ({success_rate:.1f}%)")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro durante correção: {str(e)}")
            return False
            
    def save_fix_report(self):
        """Salvar relatório das correções aplicadas"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.project_root / f"telegram_fix_report_{timestamp}.json"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "fixes_applied": self.fixes_applied,
            "total_fixes": len(self.fixes_applied),
            "status": "SUCCESS" if self.fixes_applied else "NO_FIXES_NEEDED"
        }
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
                
            logger.info(f"📄 Relatório de correções salvo: {report_path}")
            return report_path
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar relatório: {str(e)}")
            return None

def main():
    """Função principal"""
    print("🔧 CORREÇÃO AUTOMÁTICA DO AMBIENTE TELEGRAM")
    print("=" * 50)
    
    fixer = TelegramEnvironmentFixer()
    
    # Executar correção completa
    success = fixer.run_complete_fix()
    
    # Salvar relatório
    report_path = fixer.save_fix_report()
    
    # Exibir resumo
    print(f"\n📊 RESUMO DA CORREÇÃO:")
    print(f"Status: {'✅ SUCESSO' if success else '⚠️ PARCIAL'}")
    print(f"Correções aplicadas: {len(fixer.fixes_applied)}")
    
    if fixer.fixes_applied:
        print("\n🔧 CORREÇÕES APLICADAS:")
        for fix in fixer.fixes_applied:
            print(f"  • {fix['type']}: {fix['description']}")
            
    if report_path:
        print(f"\n📄 Relatório detalhado: {report_path}")
        
    if success:
        print("\n🎉 TELEGRAM CONFIGURADO COM SUCESSO!")
        print("As variáveis de ambiente agora serão carregadas automaticamente.")
    else:
        print("\n⚠️ CORREÇÃO PARCIAL APLICADA")
        print("Verifique o relatório para detalhes dos problemas encontrados.")
        
    return success

if __name__ == "__main__":
    main()