#!/usr/bin/env python3
"""
Enhanced Data Validator - Sistema de Validação de Dados Robusta
Implementa validação avançada com verificação de tipos, integridade e regras de negócio
"""

import json
import sqlite3
import hashlib
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional, Union
from dataclasses import dataclass
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Resultado de uma validação"""
    is_valid: bool
    error_code: str = ""
    error_message: str = ""
    warnings: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.metadata is None:
            self.metadata = {}

class EnhancedDataValidator:
    """Sistema de validação de dados robusta"""
    
    def __init__(self, base_path: Path = None):
        self.base_path = base_path or Path.cwd()
        self.validation_rules = self._load_validation_rules()
        self.business_rules = self._load_business_rules()
        
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Carregar regras de validação"""
        return {
            'ltm_documents': {
                'required_fields': ['service_hour', 'doc_path', 'checklist_path'],
                'field_types': {
                    'service_hour': str,
                    'doc_path': (str, Path),
                    'checklist_path': (str, Path),
                    'checksum': str,
                    'created_at': str
                },
                'field_patterns': {
                    'service_hour': r'^(6h|9h|12h|15h|19h|21h)$',
                    'checksum': r'^[a-f0-9]{64}$',
                    'created_at': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'
                }
            },
            'instagram_credentials': {
                'required_fields': ['access_token', 'business_account_id'],
                'field_types': {
                    'access_token': str,
                    'business_account_id': str
                },
                'field_patterns': {
                    'access_token': r'^[A-Za-z0-9_-]+$',
                    'business_account_id': r'^\d+$'
                }
            },
            'telegram_config': {
                'required_fields': ['bot_token', 'chat_id'],
                'field_types': {
                    'bot_token': str,
                    'chat_id': str
                },
                'field_patterns': {
                    'bot_token': r'^\d+:[A-Za-z0-9_-]+$',
                    'chat_id': r'^-?\d+$'
                }
            }
        }
    
    def _load_business_rules(self) -> Dict[str, Any]:
        """Carregar regras de negócio"""
        return {
            'ltm_consistency': {
                'doc_checklist_naming': {
                    'description': 'Documento e checklist devem ter nomes consistentes',
                    'pattern': r'LTM_(POST|CHECKLIST)_(\d+H)_BRT\.md$'
                },
                'hour_consistency': {
                    'description': 'Hora no nome do arquivo deve corresponder ao service_hour',
                    'mapping': {
                        '6h': '6H', '9h': '9H', '12h': '12H',
                        '15h': '15H', '19h': '19H', '21h': '21H'
                    }
                }
            },
            'posting_schedule': {
                'valid_hours': ['6h', '9h', '12h', '15h', '19h', '21h'],
                'timezone': 'BRT',
                'max_posts_per_day': 6,
                'min_interval_hours': 3
            },
            'content_quality': {
                'min_doc_size_bytes': 100,
                'max_doc_size_bytes': 50000,
                'required_markdown_headers': ['#'],
                'forbidden_patterns': [r'TODO', r'FIXME', r'XXX']
            }
        }
    
    def validate_ltm_document(self, data: Dict[str, Any]) -> ValidationResult:
        """Validar documento LTM"""
        try:
            # Validação de tipos
            type_result = self._validate_field_types(data, 'ltm_documents')
            if not type_result.is_valid:
                return type_result
            
            # Validação de padrões
            pattern_result = self._validate_field_patterns(data, 'ltm_documents')
            if not pattern_result.is_valid:
                return pattern_result
            
            # Validação de regras de negócio
            business_result = self._validate_ltm_business_rules(data)
            if not business_result.is_valid:
                return business_result
            
            # Validação de integridade de arquivos
            if 'doc_path' in data and 'checklist_path' in data:
                file_result = self._validate_file_integrity(
                    Path(data['doc_path']), 
                    Path(data['checklist_path'])
                )
                if not file_result.is_valid:
                    return file_result
            
            return ValidationResult(
                is_valid=True,
                metadata={'validation_type': 'ltm_document', 'timestamp': datetime.now().isoformat()}
            )
            
        except Exception as e:
            logger.error(f"Erro na validação de documento LTM: {e}")
            return ValidationResult(
                is_valid=False,
                error_code='VALIDATION_EXCEPTION',
                error_message=f"Erro interno na validação: {str(e)}"
            )
    
    def validate_instagram_credentials(self, data: Dict[str, Any]) -> ValidationResult:
        """Validar credenciais do Instagram"""
        try:
            # Validação de tipos
            type_result = self._validate_field_types(data, 'instagram_credentials')
            if not type_result.is_valid:
                return type_result
            
            # Validação de padrões
            pattern_result = self._validate_field_patterns(data, 'instagram_credentials')
            if not pattern_result.is_valid:
                return pattern_result
            
            # Validações específicas do Instagram
            access_token = data.get('access_token', '')
            business_id = data.get('business_account_id', '')
            
            warnings = []
            
            # Verificar comprimento do token
            if len(access_token) < 50:
                warnings.append("Token de acesso parece muito curto")
            elif len(access_token) > 500:
                warnings.append("Token de acesso parece muito longo")
            
            # Verificar ID da conta
            if len(business_id) < 10:
                warnings.append("ID da conta de negócios parece muito curto")
            
            return ValidationResult(
                is_valid=True,
                warnings=warnings,
                metadata={'validation_type': 'instagram_credentials', 'timestamp': datetime.now().isoformat()}
            )
            
        except Exception as e:
            logger.error(f"Erro na validação de credenciais Instagram: {e}")
            return ValidationResult(
                is_valid=False,
                error_code='VALIDATION_EXCEPTION',
                error_message=f"Erro interno na validação: {str(e)}"
            )
    
    def validate_telegram_config(self, data: Dict[str, Any]) -> ValidationResult:
        """Validar configuração do Telegram"""
        try:
            # Validação de tipos
            type_result = self._validate_field_types(data, 'telegram_config')
            if not type_result.is_valid:
                return type_result
            
            # Validação de padrões
            pattern_result = self._validate_field_patterns(data, 'telegram_config')
            if not pattern_result.is_valid:
                return pattern_result
            
            # Validações específicas do Telegram
            bot_token = data.get('bot_token', '')
            chat_id = data.get('chat_id', '')
            
            warnings = []
            
            # Verificar formato do bot token
            if ':' not in bot_token:
                return ValidationResult(
                    is_valid=False,
                    error_code='INVALID_BOT_TOKEN_FORMAT',
                    error_message="Token do bot deve conter ':' separando ID e hash"
                )
            
            bot_id, bot_hash = bot_token.split(':', 1)
            if not bot_id.isdigit():
                return ValidationResult(
                    is_valid=False,
                    error_code='INVALID_BOT_ID',
                    error_message="ID do bot deve ser numérico"
                )
            
            if len(bot_hash) < 20:
                warnings.append("Hash do bot parece muito curto")
            
            # Verificar chat ID
            try:
                chat_id_int = int(chat_id)
                if chat_id_int > 0:
                    warnings.append("Chat ID positivo indica chat privado")
                else:
                    warnings.append("Chat ID negativo indica grupo/canal")
            except ValueError:
                return ValidationResult(
                    is_valid=False,
                    error_code='INVALID_CHAT_ID',
                    error_message="Chat ID deve ser numérico"
                )
            
            return ValidationResult(
                is_valid=True,
                warnings=warnings,
                metadata={'validation_type': 'telegram_config', 'timestamp': datetime.now().isoformat()}
            )
            
        except Exception as e:
            logger.error(f"Erro na validação de configuração Telegram: {e}")
            return ValidationResult(
                is_valid=False,
                error_code='VALIDATION_EXCEPTION',
                error_message=f"Erro interno na validação: {str(e)}"
            )
    
    def validate_database_integrity(self, db_path: Path) -> ValidationResult:
        """Validar integridade do banco de dados"""
        try:
            if not db_path.exists():
                return ValidationResult(
                    is_valid=False,
                    error_code='DATABASE_NOT_FOUND',
                    error_message=f"Banco de dados não encontrado: {db_path}"
                )
            
            # Verificar se é um arquivo SQLite válido
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Verificar integridade
                cursor.execute("PRAGMA integrity_check")
                integrity_result = cursor.fetchone()[0]
                
                if integrity_result != 'ok':
                    return ValidationResult(
                        is_valid=False,
                        error_code='DATABASE_INTEGRITY_FAILED',
                        error_message=f"Falha na integridade: {integrity_result}"
                    )
                
                # Verificar tabelas
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                # Contar registros
                total_records = 0
                table_info = {}
                
                for table in tables:
                    if table != 'sqlite_sequence':
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        table_info[table] = count
                        total_records += count
                
                conn.close()
                
                return ValidationResult(
                    is_valid=True,
                    metadata={
                        'validation_type': 'database_integrity',
                        'timestamp': datetime.now().isoformat(),
                        'tables_count': len(tables),
                        'total_records': total_records,
                        'table_details': table_info
                    }
                )
                
            except sqlite3.Error as e:
                return ValidationResult(
                    is_valid=False,
                    error_code='DATABASE_ERROR',
                    error_message=f"Erro SQLite: {str(e)}"
                )
            
        except Exception as e:
            logger.error(f"Erro na validação de integridade do banco: {e}")
            return ValidationResult(
                is_valid=False,
                error_code='VALIDATION_EXCEPTION',
                error_message=f"Erro interno na validação: {str(e)}"
            )
    
    def _validate_field_types(self, data: Dict[str, Any], rule_set: str) -> ValidationResult:
        """Validar tipos de campos"""
        rules = self.validation_rules.get(rule_set, {})
        required_fields = rules.get('required_fields', [])
        field_types = rules.get('field_types', {})
        
        # Verificar campos obrigatórios
        for field in required_fields:
            if field not in data:
                return ValidationResult(
                    is_valid=False,
                    error_code='MISSING_REQUIRED_FIELD',
                    error_message=f"Campo obrigatório ausente: {field}"
                )
        
        # Verificar tipos
        for field, expected_type in field_types.items():
            if field in data:
                value = data[field]
                if isinstance(expected_type, tuple):
                    # Múltiplos tipos aceitos
                    if not isinstance(value, expected_type):
                        return ValidationResult(
                            is_valid=False,
                            error_code='INVALID_FIELD_TYPE',
                            error_message=f"Campo {field} deve ser do tipo {expected_type}, recebido: {type(value)}"
                        )
                else:
                    # Tipo único
                    if not isinstance(value, expected_type):
                        return ValidationResult(
                            is_valid=False,
                            error_code='INVALID_FIELD_TYPE',
                            error_message=f"Campo {field} deve ser do tipo {expected_type}, recebido: {type(value)}"
                        )
        
        return ValidationResult(is_valid=True)
    
    def _validate_field_patterns(self, data: Dict[str, Any], rule_set: str) -> ValidationResult:
        """Validar padrões de campos"""
        rules = self.validation_rules.get(rule_set, {})
        field_patterns = rules.get('field_patterns', {})
        
        for field, pattern in field_patterns.items():
            if field in data:
                value = str(data[field])
                if not re.match(pattern, value):
                    return ValidationResult(
                        is_valid=False,
                        error_code='INVALID_FIELD_PATTERN',
                        error_message=f"Campo {field} não atende ao padrão esperado: {pattern}"
                    )
        
        return ValidationResult(is_valid=True)
    
    def _validate_ltm_business_rules(self, data: Dict[str, Any]) -> ValidationResult:
        """Validar regras de negócio específicas do LTM"""
        service_hour = data.get('service_hour', '')
        doc_path = data.get('doc_path', '')
        checklist_path = data.get('checklist_path', '')
        
        # Verificar consistência de nomes
        if doc_path and checklist_path:
            doc_name = Path(doc_path).name
            checklist_name = Path(checklist_path).name
            
            # Extrair hora dos nomes dos arquivos
            doc_match = re.search(r'LTM_POST_(\d+H)_BRT\.md$', doc_name)
            checklist_match = re.search(r'LTM_CHECKLIST_(\d+H)_BRT\.md$', checklist_name)
            
            if not doc_match:
                return ValidationResult(
                    is_valid=False,
                    error_code='INVALID_DOC_NAME_FORMAT',
                    error_message=f"Nome do documento não segue o padrão: {doc_name}"
                )
            
            if not checklist_match:
                return ValidationResult(
                    is_valid=False,
                    error_code='INVALID_CHECKLIST_NAME_FORMAT',
                    error_message=f"Nome do checklist não segue o padrão: {checklist_name}"
                )
            
            # Verificar consistência de horas
            doc_hour = doc_match.group(1)
            checklist_hour = checklist_match.group(1)
            
            if doc_hour != checklist_hour:
                return ValidationResult(
                    is_valid=False,
                    error_code='HOUR_MISMATCH',
                    error_message=f"Horas inconsistentes: doc={doc_hour}, checklist={checklist_hour}"
                )
            
            # Verificar se a hora corresponde ao service_hour
            hour_mapping = self.business_rules['ltm_consistency']['hour_consistency']['mapping']
            expected_hour = hour_mapping.get(service_hour, '')
            
            if doc_hour != expected_hour:
                return ValidationResult(
                    is_valid=False,
                    error_code='SERVICE_HOUR_MISMATCH',
                    error_message=f"Hora do arquivo ({doc_hour}) não corresponde ao service_hour ({service_hour})"
                )
        
        return ValidationResult(is_valid=True)
    
    def _validate_file_integrity(self, doc_path: Path, checklist_path: Path) -> ValidationResult:
        """Validar integridade dos arquivos"""
        # Verificar existência
        if not doc_path.exists():
            return ValidationResult(
                is_valid=False,
                error_code='DOC_FILE_NOT_FOUND',
                error_message=f"Arquivo de documento não encontrado: {doc_path}"
            )
        
        if not checklist_path.exists():
            return ValidationResult(
                is_valid=False,
                error_code='CHECKLIST_FILE_NOT_FOUND',
                error_message=f"Arquivo de checklist não encontrado: {checklist_path}"
            )
        
        # Verificar tamanhos
        doc_size = doc_path.stat().st_size
        checklist_size = checklist_path.stat().st_size
        
        min_size = self.business_rules['content_quality']['min_doc_size_bytes']
        max_size = self.business_rules['content_quality']['max_doc_size_bytes']
        
        if doc_size < min_size:
            return ValidationResult(
                is_valid=False,
                error_code='DOC_TOO_SMALL',
                error_message=f"Documento muito pequeno: {doc_size} bytes (mínimo: {min_size})"
            )
        
        if doc_size > max_size:
            return ValidationResult(
                is_valid=False,
                error_code='DOC_TOO_LARGE',
                error_message=f"Documento muito grande: {doc_size} bytes (máximo: {max_size})"
            )
        
        if checklist_size < min_size:
            return ValidationResult(
                is_valid=False,
                error_code='CHECKLIST_TOO_SMALL',
                error_message=f"Checklist muito pequeno: {checklist_size} bytes (mínimo: {min_size})"
            )
        
        # Verificar conteúdo básico
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                doc_content = f.read()
            
            with open(checklist_path, 'r', encoding='utf-8') as f:
                checklist_content = f.read()
            
            # Verificar headers markdown
            if not doc_content.strip().startswith('#'):
                return ValidationResult(
                    is_valid=False,
                    error_code='MISSING_MARKDOWN_HEADER',
                    error_message=f"Documento não possui header markdown: {doc_path}"
                )
            
            if not checklist_content.strip().startswith('#'):
                return ValidationResult(
                    is_valid=False,
                    error_code='MISSING_MARKDOWN_HEADER',
                    error_message=f"Checklist não possui header markdown: {checklist_path}"
                )
            
            # Verificar padrões proibidos
            forbidden_patterns = self.business_rules['content_quality']['forbidden_patterns']
            warnings = []
            
            for pattern in forbidden_patterns:
                if re.search(pattern, doc_content, re.IGNORECASE):
                    warnings.append(f"Padrão proibido encontrado no documento: {pattern}")
                
                if re.search(pattern, checklist_content, re.IGNORECASE):
                    warnings.append(f"Padrão proibido encontrado no checklist: {pattern}")
            
            return ValidationResult(
                is_valid=True,
                warnings=warnings,
                metadata={
                    'doc_size': doc_size,
                    'checklist_size': checklist_size,
                    'doc_lines': len(doc_content.splitlines()),
                    'checklist_lines': len(checklist_content.splitlines())
                }
            )
            
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error_code='FILE_READ_ERROR',
                error_message=f"Erro ao ler arquivos: {str(e)}"
            )
    
    def generate_validation_report(self, validations: List[Tuple[str, ValidationResult]]) -> Dict[str, Any]:
        """Gerar relatório de validação"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_validations': len(validations),
            'passed': 0,
            'failed': 0,
            'warnings_count': 0,
            'results': [],
            'summary': {
                'overall_status': 'UNKNOWN',
                'critical_issues': [],
                'warnings': [],
                'recommendations': []
            }
        }
        
        for validation_name, result in validations:
            report['results'].append({
                'name': validation_name,
                'status': 'PASSED' if result.is_valid else 'FAILED',
                'error_code': result.error_code,
                'error_message': result.error_message,
                'warnings': result.warnings,
                'metadata': result.metadata
            })
            
            if result.is_valid:
                report['passed'] += 1
            else:
                report['failed'] += 1
                report['summary']['critical_issues'].append({
                    'validation': validation_name,
                    'error': result.error_message
                })
            
            report['warnings_count'] += len(result.warnings)
            report['summary']['warnings'].extend(result.warnings)
        
        # Determinar status geral
        if report['failed'] == 0:
            report['summary']['overall_status'] = 'PASSED'
        elif report['passed'] > 0:
            report['summary']['overall_status'] = 'PARTIAL'
        else:
            report['summary']['overall_status'] = 'FAILED'
        
        # Gerar recomendações
        if report['failed'] > 0:
            report['summary']['recommendations'].append("Corrigir todos os erros críticos antes de prosseguir")
        
        if report['warnings_count'] > 0:
            report['summary']['recommendations'].append("Revisar e resolver avisos quando possível")
        
        if report['summary']['overall_status'] == 'PASSED':
            report['summary']['recommendations'].append("Todas as validações passaram - sistema pronto para operação")
        
        return report

def main():
    """Função principal para teste"""
    validator = EnhancedDataValidator()
    
    # Teste de validação de documento LTM
    ltm_data = {
        'service_hour': '9h',
        'doc_path': 'docs/LTM_POST_9H_BRT.md',
        'checklist_path': 'docs/LTM_CHECKLIST_9H_BRT.md',
        'checksum': 'a1b2c3d4e5f6789012345678901234567890123456789012345678901234567890',
        'created_at': '2025-11-03T21:53:20.751786'
    }
    
    result = validator.validate_ltm_document(ltm_data)
    print(f"Validação LTM: {'✅ PASSOU' if result.is_valid else '❌ FALHOU'}")
    if not result.is_valid:
        print(f"Erro: {result.error_message}")
    if result.warnings:
        print(f"Avisos: {result.warnings}")
    
    print("\n🔍 Sistema de validação de dados robusta implementado com sucesso!")

if __name__ == "__main__":
    main()