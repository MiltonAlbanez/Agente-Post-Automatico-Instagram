#!/usr/bin/env python3
"""
Sistema de Backup Automático
Gerencia backups dos dados de performance e configurações do sistema
"""

import json
import sqlite3
import shutil
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import schedule
import time
import threading

class BackupManager:
    """
    Gerencia backups automáticos dos dados do sistema
    """
    
    def __init__(self, config_path: str = "config/backup_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.backup_dir = Path(self.config["backup"]["directory"])
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self._setup_scheduler()
    
    def _load_config(self) -> Dict:
        """Carrega configurações de backup"""
        default_config = {
            "backup": {
                "directory": "backups",
                "retention_days": 30,
                "max_backups": 50,
                "compress": True,
                "include_logs": True
            },
            "schedule": {
                "daily_backup": "02:00",
                "weekly_full_backup": "sunday",
                "monthly_cleanup": 1
            },
            "targets": {
                "database": {
                    "enabled": True,
                    "path": "data/engagement_data.db"
                },
                "configs": {
                    "enabled": True,
                    "paths": [
                        "accounts.json",
                        "config/",
                        "prompts/"
                    ]
                },
                "logs": {
                    "enabled": True,
                    "paths": [
                        "logs/",
                        "data/performance_logs/"
                    ]
                },
                "generated_content": {
                    "enabled": False,
                    "paths": [
                        "generated_images/",
                        "generated_content/"
                    ]
                }
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
    
    def _setup_scheduler(self) -> None:
        """Configura agendamento automático de backups"""
        # Backup diário
        daily_time = self.config["schedule"]["daily_backup"]
        schedule.every().day.at(daily_time).do(self.create_daily_backup)
        
        # Backup semanal completo
        weekly_day = self.config["schedule"]["weekly_full_backup"]
        schedule.every().week.at(daily_time).do(self.create_full_backup)
        
        # Limpeza mensal
        schedule.every().month.do(self.cleanup_old_backups)
    
    def create_daily_backup(self) -> str:
        """Cria backup diário (apenas dados essenciais)"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"daily_backup_{timestamp}"
            backup_path = self.backup_dir / backup_name
            backup_path.mkdir(exist_ok=True)
            
            print(f"📦 Iniciando backup diário: {backup_name}")
            
            # Backup do banco de dados
            if self.config["targets"]["database"]["enabled"]:
                self._backup_database(backup_path)
            
            # Backup das configurações
            if self.config["targets"]["configs"]["enabled"]:
                self._backup_configs(backup_path)
            
            # Comprimir se habilitado
            if self.config["backup"]["compress"]:
                zip_path = self._compress_backup(backup_path)
                shutil.rmtree(backup_path)
                backup_path = zip_path
            
            print(f"✅ Backup diário concluído: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            print(f"❌ Erro no backup diário: {e}")
            return ""
    
    def create_full_backup(self) -> str:
        """Cria backup completo (todos os dados)"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"full_backup_{timestamp}"
            backup_path = self.backup_dir / backup_name
            backup_path.mkdir(exist_ok=True)
            
            print(f"📦 Iniciando backup completo: {backup_name}")
            
            # Backup de todos os componentes habilitados
            for target_name, target_config in self.config["targets"].items():
                if target_config["enabled"]:
                    if target_name == "database":
                        self._backup_database(backup_path)
                    elif target_name == "configs":
                        self._backup_configs(backup_path)
                    elif target_name == "logs":
                        self._backup_logs(backup_path)
                    elif target_name == "generated_content":
                        self._backup_generated_content(backup_path)
            
            # Criar manifesto do backup
            self._create_backup_manifest(backup_path)
            
            # Comprimir se habilitado
            if self.config["backup"]["compress"]:
                zip_path = self._compress_backup(backup_path)
                shutil.rmtree(backup_path)
                backup_path = zip_path
            
            print(f"✅ Backup completo concluído: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            print(f"❌ Erro no backup completo: {e}")
            return ""
    
    def _backup_database(self, backup_path: Path) -> None:
        """Faz backup do banco de dados SQLite"""
        try:
            db_path = Path(self.config["targets"]["database"]["path"])
            if db_path.exists():
                db_backup_dir = backup_path / "database"
                db_backup_dir.mkdir(exist_ok=True)
                
                # Backup do arquivo de banco
                shutil.copy2(db_path, db_backup_dir / db_path.name)
                
                # Exportar dados em formato JSON para redundância
                self._export_database_to_json(db_path, db_backup_dir)
                
                print("📊 Backup do banco de dados concluído")
                
        except Exception as e:
            print(f"❌ Erro no backup do banco: {e}")
    
    def _export_database_to_json(self, db_path: Path, backup_dir: Path) -> None:
        """Exporta dados do banco para JSON"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Obter lista de tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            for table_name, in tables:
                # Exportar cada tabela
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                
                # Obter nomes das colunas
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [col[1] for col in cursor.fetchall()]
                
                # Converter para formato JSON
                table_data = []
                for row in rows:
                    table_data.append(dict(zip(columns, row)))
                
                # Salvar arquivo JSON
                json_file = backup_dir / f"{table_name}.json"
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(table_data, f, indent=2, ensure_ascii=False, default=str)
            
            conn.close()
            print("📄 Exportação JSON do banco concluída")
            
        except Exception as e:
            print(f"❌ Erro na exportação JSON: {e}")
    
    def _backup_configs(self, backup_path: Path) -> None:
        """Faz backup das configurações"""
        try:
            config_backup_dir = backup_path / "configs"
            config_backup_dir.mkdir(exist_ok=True)
            
            for config_path in self.config["targets"]["configs"]["paths"]:
                source_path = Path(config_path)
                
                if source_path.exists():
                    if source_path.is_file():
                        shutil.copy2(source_path, config_backup_dir / source_path.name)
                    elif source_path.is_dir():
                        dest_dir = config_backup_dir / source_path.name
                        shutil.copytree(source_path, dest_dir, dirs_exist_ok=True)
            
            print("⚙️ Backup das configurações concluído")
            
        except Exception as e:
            print(f"❌ Erro no backup das configurações: {e}")
    
    def _backup_logs(self, backup_path: Path) -> None:
        """Faz backup dos logs"""
        try:
            logs_backup_dir = backup_path / "logs"
            logs_backup_dir.mkdir(exist_ok=True)
            
            for log_path in self.config["targets"]["logs"]["paths"]:
                source_path = Path(log_path)
                
                if source_path.exists():
                    if source_path.is_file():
                        shutil.copy2(source_path, logs_backup_dir / source_path.name)
                    elif source_path.is_dir():
                        dest_dir = logs_backup_dir / source_path.name
                        shutil.copytree(source_path, dest_dir, dirs_exist_ok=True)
            
            print("📝 Backup dos logs concluído")
            
        except Exception as e:
            print(f"❌ Erro no backup dos logs: {e}")
    
    def _backup_generated_content(self, backup_path: Path) -> None:
        """Faz backup do conteúdo gerado"""
        try:
            content_backup_dir = backup_path / "generated_content"
            content_backup_dir.mkdir(exist_ok=True)
            
            for content_path in self.config["targets"]["generated_content"]["paths"]:
                source_path = Path(content_path)
                
                if source_path.exists():
                    if source_path.is_file():
                        shutil.copy2(source_path, content_backup_dir / source_path.name)
                    elif source_path.is_dir():
                        dest_dir = content_backup_dir / source_path.name
                        shutil.copytree(source_path, dest_dir, dirs_exist_ok=True)
            
            print("🎨 Backup do conteúdo gerado concluído")
            
        except Exception as e:
            print(f"❌ Erro no backup do conteúdo: {e}")
    
    def _create_backup_manifest(self, backup_path: Path) -> None:
        """Cria manifesto do backup"""
        try:
            manifest = {
                "backup_type": "full",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0",
                "components": [],
                "file_count": 0,
                "total_size_mb": 0
            }
            
            # Calcular estatísticas do backup
            total_size = 0
            file_count = 0
            
            for item in backup_path.rglob("*"):
                if item.is_file():
                    file_count += 1
                    total_size += item.stat().st_size
            
            manifest["file_count"] = file_count
            manifest["total_size_mb"] = round(total_size / (1024 * 1024), 2)
            
            # Listar componentes incluídos
            for component_dir in backup_path.iterdir():
                if component_dir.is_dir():
                    manifest["components"].append(component_dir.name)
            
            # Salvar manifesto
            manifest_file = backup_path / "backup_manifest.json"
            with open(manifest_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
            
            print(f"📋 Manifesto criado: {file_count} arquivos, {manifest['total_size_mb']} MB")
            
        except Exception as e:
            print(f"❌ Erro ao criar manifesto: {e}")
    
    def _compress_backup(self, backup_path: Path) -> Path:
        """Comprime o backup em arquivo ZIP"""
        try:
            zip_path = backup_path.with_suffix('.zip')
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in backup_path.rglob("*"):
                    if file_path.is_file():
                        arcname = file_path.relative_to(backup_path)
                        zipf.write(file_path, arcname)
            
            # Calcular compressão
            original_size = sum(f.stat().st_size for f in backup_path.rglob("*") if f.is_file())
            compressed_size = zip_path.stat().st_size
            compression_ratio = (1 - compressed_size / original_size) * 100
            
            print(f"🗜️ Backup comprimido: {compression_ratio:.1f}% de redução")
            
            return zip_path
            
        except Exception as e:
            print(f"❌ Erro na compressão: {e}")
            return backup_path
    
    def cleanup_old_backups(self) -> None:
        """Remove backups antigos baseado na política de retenção"""
        try:
            retention_days = self.config["backup"]["retention_days"]
            max_backups = self.config["backup"]["max_backups"]
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            backups = []
            for backup_file in self.backup_dir.iterdir():
                if backup_file.is_file() or backup_file.is_dir():
                    stat = backup_file.stat()
                    creation_time = datetime.fromtimestamp(stat.st_ctime)
                    backups.append((backup_file, creation_time))
            
            # Ordenar por data de criação (mais antigos primeiro)
            backups.sort(key=lambda x: x[1])
            
            removed_count = 0
            
            # Remover backups antigos
            for backup_file, creation_time in backups:
                if creation_time < cutoff_date or len(backups) - removed_count > max_backups:
                    if backup_file.is_file():
                        backup_file.unlink()
                    elif backup_file.is_dir():
                        shutil.rmtree(backup_file)
                    
                    removed_count += 1
                    print(f"🗑️ Backup removido: {backup_file.name}")
            
            if removed_count == 0:
                print("✅ Nenhum backup antigo para remover")
            else:
                print(f"🧹 Limpeza concluída: {removed_count} backups removidos")
                
        except Exception as e:
            print(f"❌ Erro na limpeza de backups: {e}")
    
    def restore_backup(self, backup_path: str, target_dir: str = ".") -> bool:
        """Restaura um backup"""
        try:
            backup_file = Path(backup_path)
            target_path = Path(target_dir)
            
            if not backup_file.exists():
                print(f"❌ Backup não encontrado: {backup_path}")
                return False
            
            print(f"🔄 Iniciando restauração: {backup_file.name}")
            
            if backup_file.suffix == '.zip':
                # Extrair arquivo ZIP
                with zipfile.ZipFile(backup_file, 'r') as zipf:
                    zipf.extractall(target_path)
            else:
                # Copiar diretório
                shutil.copytree(backup_file, target_path / backup_file.name, dirs_exist_ok=True)
            
            print("✅ Restauração concluída")
            return True
            
        except Exception as e:
            print(f"❌ Erro na restauração: {e}")
            return False
    
    def list_backups(self) -> List[Dict]:
        """Lista todos os backups disponíveis"""
        try:
            backups = []
            
            for backup_item in self.backup_dir.iterdir():
                if backup_item.is_file() or backup_item.is_dir():
                    stat = backup_item.stat()
                    
                    backup_info = {
                        "name": backup_item.name,
                        "path": str(backup_item),
                        "size_mb": round(stat.st_size / (1024 * 1024), 2) if backup_item.is_file() else 0,
                        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "type": "compressed" if backup_item.suffix == '.zip' else "directory"
                    }
                    
                    backups.append(backup_info)
            
            # Ordenar por data de criação (mais recentes primeiro)
            backups.sort(key=lambda x: x["created"], reverse=True)
            
            return backups
            
        except Exception as e:
            print(f"❌ Erro ao listar backups: {e}")
            return []
    
    def start_scheduler(self) -> None:
        """Inicia o agendador de backups em thread separada"""
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Verificar a cada minuto
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        print("⏰ Agendador de backups iniciado")

if __name__ == "__main__":
    # Teste do sistema de backup
    backup_manager = BackupManager()
    
    print("🔧 Testando sistema de backup...")
    
    # Criar backup de teste
    backup_path = backup_manager.create_daily_backup()
    
    if backup_path:
        print(f"✅ Backup de teste criado: {backup_path}")
        
        # Listar backups
        backups = backup_manager.list_backups()
        print(f"📋 Total de backups: {len(backups)}")
        
        for backup in backups[:3]:  # Mostrar apenas os 3 mais recentes
            print(f"  - {backup['name']} ({backup['size_mb']} MB)")
    
    print("✅ Teste de backup concluído!")