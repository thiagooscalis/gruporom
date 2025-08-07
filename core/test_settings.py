"""
Configurações específicas para testes
"""
from config.settings import *

# Usar armazenamento em memória para arquivos durante testes
DEFAULT_FILE_STORAGE = 'django.core.files.storage.InMemoryStorage'

# Desabilitar cache durante testes
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Acelerar testes com hash de senha mais rápido
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Desabilitar migrações para acelerar testes
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Log apenas erros durante testes
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['console'],
    },
}