#!/usr/bin/env python
import os
import django
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
from accounts.models import User
from cases.models import Case

print('=' * 80)
print('DEBUG COMPLETO DE BÚSQUEDA')
print('=' * 80)

# Verificar casos en BD
print('\n1. CASOS EN BASE DE DATOS:')
print('-' * 80)
all_cases = Case.objects.all().order_by('case_number')
print(f'Total casos: {all_cases.count()}')
for case in all_cases[:10]:
    print(f'  {case.sequence_number:2}. {case.case_number} - {case.status} - {case.beneficiary.full_name}')

# Acceder al dashboard
print('\n2. ACCEDIENDO AL DASHBOARD:')
print('-' * 80)
client = Client()
user = User.objects.get(document_number='1001')
login_ok = client.login(username='1001', password='1234')
print(f'Login: {login_ok}')

response = client.get('/secretaria/dashboard/')
print(f'HTTP Status: {response.status_code}')

# Verificar que los casos están en el HTML
print('\n3. CASOS EN EL HTML:')
print('-' * 80)
content = response.content.decode()

# Buscar data-case-number
pattern = r'data-case-number="([^"]*)"'
matches = re.findall(pattern, content)
print(f'data-case-number encontrados: {len(matches)}')
print(f'Valores: {matches}')

# Buscar "número: XXXXX"
pattern = r'número: (\d{5})'
numero_matches = re.findall(pattern, content)
print(f'\nFormato "número: XXXXX": {len(numero_matches)} encontrados')
print(f'Primeros 5: {numero_matches[:5]}')

# Buscar el script de búsqueda
print('\n4. SCRIPT DE BÚSQUEDA EN HTML:')
print('-' * 80)
if 'function filterCases()' in content:
    print('✓ Función filterCases encontrada')
    # Extraer el contenido de la función
    start = content.find('function filterCases()')
    end = content.find('\n}', start) + 2
    func_content = content[start:end]
    if 'data-case-number' in func_content:
        print('✓ Usa data-case-number para comparar')
    if 'padStart' in func_content:
        print('✓ Usa padStart para convertir números')
    if '/cases/api/casos/buscar-por-id/' in func_content:
        print('✓ Llama al endpoint correcto')
else:
    print('✗ Función filterCases NO encontrada')

# Verificar input de búsqueda
print('\n5. INPUT DE BÚSQUEDA:')
print('-' * 80)
if 'caseSearchInput' in content:
    pattern = r'id="caseSearchInput"[^>]*placeholder="([^"]*)"'
    placeholder_match = re.search(pattern, content)
    if placeholder_match:
        print(f'✓ Input encontrado, placeholder: "{placeholder_match.group(1)}"')
else:
    print('✗ Input NO encontrado')

# Verificar que el container de casos existe
print('\n6. CONTENEDOR DE CASOS:')
print('-' * 80)
if 'recentCasesList' in content:
    print('✓ Contenedor recentCasesList encontrado')
else:
    print('✗ Contenedor NO encontrado')

print('\n' + '=' * 80)
print('CONCLUSIÓN:')
print('=' * 80)
print('Si todo está bien, probablemente el problema sea:')
print('1. Caché del navegador - limpiar (Ctrl+Shift+Del)')
print('2. JavaScript no se ejecuta - revisar consola (F12)')
print('3. Buscar con números que existan: 1, 5, 30, etc.')
print('=' * 80)
