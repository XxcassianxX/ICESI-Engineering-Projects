#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client

print('=' * 80)
print('PROBANDO BÚSQUEDA CON TODOS LOS CASOS')
print('=' * 80)

client = Client()
client.login(username='1001', password='1234')

# Casos para probar (con 5 dígitos)
test_cases = ['00001', '00030', '00005', '00032', '00015', '00099']

for search_id in test_cases:
    response = client.get(f'/cases/api/casos/buscar-por-id/?id={search_id}')
    data = response.json()
    
    print(f'\nBúsqueda: {search_id}')
    if data.get('found'):
        case_data = data.get('case')
        print(f'  ✓ ENCONTRADO: Caso {case_data["case_number"]} - {case_data["beneficiary_name"]}')
    else:
        print(f'  ✗ NO ENCONTRADO: {data.get("error", "Desconocido")}')

print('\n' + '=' * 80)
print('✅ LA BÚSQUEDA DEBE FUNCIONAR AHORA')
print('=' * 80)
print('\nPASOS:')
print('1. Limpiar caché: Ctrl+Shift+Del')
print('2. Recargar: F5')
print('3. Buscar un número: 1, 5, 30, etc.')
print('4. El JavaScript convierte a 5 dígitos automáticamente')
print('5. El caso debe aparecer resaltado')
print('=' * 80)
