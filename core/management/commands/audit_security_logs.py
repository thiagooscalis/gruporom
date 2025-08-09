# -*- coding: utf-8 -*-
"""
Command para auditar logs e identificar possíveis vazamentos de informações sensíveis
"""

import os
import re
import glob
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Audita logs existentes procurando por informações sensíveis'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Aplica correções automáticas nos arquivos de código',
        )
        parser.add_argument(
            '--path',
            type=str,
            default='core',
            help='Caminho para auditar (padrão: core)',
        )
    
    def handle(self, *args, **options):
        self.fix_mode = options['fix']
        self.audit_path = options['path']
        
        self.stdout.write(self.style.SUCCESS('🔍 Iniciando auditoria de segurança dos logs...'))
        
        issues_found = []
        
        # 1. Audita arquivos Python
        issues_found.extend(self._audit_python_files())
        
        # 2. Audita configurações
        issues_found.extend(self._audit_settings())
        
        # 3. Relatório final
        self._generate_report(issues_found)
    
    def _audit_python_files(self):
        """Audita arquivos Python procurando por logs inseguros"""
        issues = []
        
        # Padrões problemáticos
        dangerous_patterns = [
            # Logs que podem vazar informações
            (r'logger\.(debug|info|warning|error)\([^)]*(?:password|token|key|secret|header)', 
             'Log pode conter informações sensíveis'),
            
            # Logs de traceback completo
            (r'logger\.(error|critical)\([^)]*traceback\.format_exc\(\)', 
             'Traceback completo pode vazar informações internas'),
            
            # Logs de request.body completo
            (r'logger\.(debug|info|warning|error)\([^)]*request\.body', 
             'Log do body da requisição pode conter dados sensíveis'),
            
            # Logs de payloads JSON completos
            (r'logger\.(debug|info|warning|error)\([^)]*json\.dumps\([^)]+\)', 
             'Log de JSON completo pode conter dados sensíveis'),
            
            # Print statements (não devem existir em produção)
            (r'print\s*\(', 
             'Print statement deve ser substituído por logger'),
        ]
        
        # Busca arquivos Python
        python_files = glob.glob(f'{self.audit_path}/**/*.py', recursive=True)
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                for line_num, line in enumerate(lines, 1):
                    for pattern, description in dangerous_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            issues.append({
                                'file': file_path,
                                'line': line_num,
                                'content': line.strip(),
                                'issue': description,
                                'severity': 'HIGH' if any(word in pattern for word in ['password', 'token', 'secret']) else 'MEDIUM'
                            })
                            
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Erro ao ler arquivo {file_path}: {e}')
                )
        
        return issues
    
    def _audit_settings(self):
        """Audita configurações do Django"""
        issues = []
        
        # Verifica se DEBUG está desabilitado em produção
        if hasattr(settings, 'DEBUG') and settings.DEBUG:
            issues.append({
                'file': 'settings.py',
                'line': 'N/A',
                'content': 'DEBUG = True',
                'issue': 'DEBUG deve ser False em produção',
                'severity': 'HIGH'
            })
        
        # Verifica configuração de logging
        if hasattr(settings, 'LOGGING'):
            logging_config = settings.LOGGING
            
            # Verifica se há formatters seguros
            formatters = logging_config.get('formatters', {})
            if not any('secure' in formatter_name.lower() for formatter_name in formatters.keys()):
                issues.append({
                    'file': 'settings.py',
                    'line': 'N/A',
                    'content': 'LOGGING configuration',
                    'issue': 'Não há formatters seguros configurados',
                    'severity': 'MEDIUM'
                })
        
        return issues
    
    def _generate_report(self, issues):
        """Gera relatório da auditoria"""
        if not issues:
            self.stdout.write(self.style.SUCCESS('✅ Nenhum problema de segurança encontrado nos logs!'))
            return
        
        self.stdout.write(self.style.WARNING(f'⚠️  Encontrados {len(issues)} possíveis problemas:'))
        self.stdout.write('')
        
        # Agrupa por severidade
        high_issues = [i for i in issues if i['severity'] == 'HIGH']
        medium_issues = [i for i in issues if i['severity'] == 'MEDIUM']
        
        if high_issues:
            self.stdout.write(self.style.ERROR('🚨 SEVERIDADE ALTA:'))
            for issue in high_issues:
                self._print_issue(issue)
            self.stdout.write('')
        
        if medium_issues:
            self.stdout.write(self.style.WARNING('⚠️  SEVERIDADE MÉDIA:'))
            for issue in medium_issues:
                self._print_issue(issue)
        
        # Sugestões de correção
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('💡 SUGESTÕES DE CORREÇÃO:'))
        self.stdout.write('')
        self.stdout.write('1. Use o SecureLogger ao invés de logger padrão:')
        self.stdout.write('   from core.utils.secure_logger import get_secure_logger')
        self.stdout.write('   logger = get_secure_logger(__name__)')
        self.stdout.write('')
        self.stdout.write('2. Configure logging seguro em settings.py:')
        self.stdout.write('   from core.logging_config import LOGGING_CONFIG')
        self.stdout.write('   LOGGING = LOGGING_CONFIG')
        self.stdout.write('')
        self.stdout.write('3. Use middleware de logging seguro:')
        self.stdout.write('   Adicione core.middleware.SecureLoggingMiddleware ao MIDDLEWARE')
    
    def _print_issue(self, issue):
        """Imprime detalhes de um problema"""
        self.stdout.write(f"  📄 {issue['file']}:{issue['line']}")
        self.stdout.write(f"     {issue['content'][:100]}...")
        self.stdout.write(f"     ➜ {issue['issue']}")
        self.stdout.write('')
    
    def _create_secure_logging_example(self):
        """Cria exemplo de configuração segura"""
        example_file = 'secure_logging_example.py'
        
        example_content = '''# -*- coding: utf-8 -*-
"""
Exemplo de uso de logging seguro
"""

from core.utils.secure_logger import get_secure_logger

# Use isso ao invés de logging.getLogger()
logger = get_secure_logger(__name__)

def example_function():
    # ✅ Correto - dados sensíveis são automaticamente removidos
    logger.info("Usuário logou", extra={
        "user_id": 123,
        "token": "abc123",  # Será mascarado automaticamente
        "password": "secret"  # Será removido automaticamente
    })
    
    # ✅ Correto - erro sem traceback em produção
    try:
        risky_operation()
    except Exception as e:
        logger.exception("Erro na operação", extra={"operation": "example"})
    
    # ❌ Evite - pode vazar informações
    # logger.info(f"Headers completos: {request.META}")
    
    # ❌ Evite - traceback pode vazar caminhos internos
    # import traceback
    # logger.error(f"Erro: {traceback.format_exc()}")

def risky_operation():
    raise ValueError("Exemplo de erro")
'''
        
        with open(example_file, 'w', encoding='utf-8') as f:
            f.write(example_content)
        
        self.stdout.write(f'📝 Exemplo criado: {example_file}')