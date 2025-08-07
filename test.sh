#!/bin/bash

# Script para executar testes com as configurações corretas

# Definir variável de ambiente
export DJANGO_SETTINGS_MODULE=core.test_settings

# Executar pytest com os argumentos passados
uv run pytest "$@"