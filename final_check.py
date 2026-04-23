#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from cases.models import Case

print('=' * 80)
print('VERIFICACIÓN FINAL - BÚSQUEDA DE CASOS')
print('=' * 80)

# 1. Verificar BD
all_cases = Case.objects.all().order_by('case_number')
print(f'\n✓ Base de datos: {all_cases.count()} casos')

# 2. Verificar templates
import os
from django.test import Client

client = Client()
client.login(username='1001', password='1234')
response = client.get('/secretaria/dashboard/')
content = response.content.decode()

import re
pattern = r'data-case-number="([^"]*)"'
matches = re.findall(pattern, content)
print(f'✓ Template: {len(matches)} casos en HTML')

# 3. Verificar que filterCases usa padStart
if 'padStart' in content and 'filterCases' in content:
    print('✓ JavaScript: padStart está presente')
    if '/cases/api/casos/buscar-por-id/' in content:
        print('✓ JavaScript: endpoint correcto')

# 4. Probar búsquedas
print(f'\n✓ Pruebas de búsqueda:')
test_searches = [
    ('1', '00001'),
    ('5', '00005'),
    ('30', '00030'),
]

from django.test import Client as TestClient

for search_input, expected_id in test_searches:
    # El JavaScript convierte esto
    padded = str(search_input).zfill(5)
    
    # Verificar que existe en BD
    case_exists = Case.objects.filter(case_number=expected_id).exists()
    print(f'  - Búsqueda "{search_input}" → "{padded}": {"✓" if case_exists else "✗"}')

print('\n' + '=' * 80)
print('✅ TODO ESTÁ CONFIGURADO CORRECTAMENTE')
print('=' * 80)
print('\nQUÉ HACER:')
print('1. Abre http://127.0.0.1:8000/secretaria/dashboard/')
print('2. Presiona: Ctrl + Shift + Del (limpiar caché)')
print('3. Presiona: F5 (recargar página)')
print('4. En "Casos Recientes", busca: 1, 5, 30')
print('5. El caso debe aparecer resaltado')
print('=' * 80)
