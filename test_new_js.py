#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
from accounts.models import User
import json
import re

print('=' * 70)
print('TEST DEL NUEVO JAVASCRIPT - COMPARACIÓN POR data-case-number')
print('=' * 70)

client = Client()
user = User.objects.get(document_number='1001')
client.login(username='1001', password='1234')

# Parte 1: API retorna case_number correcto
print('\n1. VERIFICACIÓN DE API')
print('-' * 70)

response = client.get('/cases/api/casos/buscar-por-id/?id=00030')
data = json.loads(response.content)
api_case_number = data.get('case', {}).get('case_number')
print(f'✓ API devuelve case_number: {api_case_number}')

# Parte 2: Dashboard tiene data-case-number correcto
print('\n2. VERIFICACIÓN DE HTML')
print('-' * 70)

response = client.get('/secretaria/dashboard/')
content = response.content.decode()

# Buscar data-case-number="00030"
pattern = r'data-case-number="([^"]*)"'
matches = re.findall(pattern, content)
print(f'✓ data-case-number encontrados en HTML: {len(matches)}')
print(f'  Primeros 5 valores: {matches[:5]}')

if '00030' in matches:
    print(f'✓ data-case-number="00030" ENCONTRADO')
else:
    print(f'✗ data-case-number="00030" NO ENCONTRADO')

# Parte 3: Simular lógica del nuevo JavaScript
print('\n3. SIMULACIÓN DEL NUEVO JAVASCRIPT')
print('-' * 70)

# El API retorna case_number
target_case_number = data['case']['case_number'].lower()
print(f'Target case_number (from API): "{target_case_number}"')

# Comparar con data-case-number en HTML
print(f'\nComparando con HTML data-case-number:')
found = False
for item_case_number in matches:
    if item_case_number == target_case_number:
        print(f'✓ COINCIDENCIA ENCONTRADA: "{item_case_number}" == "{target_case_number}"')
        found = True
        break

if found:
    print('\n✓ LA BÚSQUEDA FUNCIONARÁ CORRECTAMENTE')
else:
    print('\n✗ LA BÚSQUEDA NO FUNCIONARÁ')
    print(f'  Buscando: "{target_case_number}"')
    print(f'  En: {matches}')

print('\n' + '=' * 70)
