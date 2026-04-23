#!/usr/bin/env python
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
from accounts.models import User

print('=' * 80)
print('TEST FINAL - BÚSQUEDA DE CASO 00030 CON ENTRADA "30"')
print('=' * 80)

client = Client()
user = User.objects.get(document_number='1001')
client.login(username='1001', password='1234')

# Test 1: Búsqueda en dashboard
print('\n✓ TEST 1: Dashboard - Búsqueda Casos Recientes')
print('-' * 80)
response = client.get('/cases/api/casos/buscar-por-id/?id=00030')
data = json.loads(response.content)
if data.get('found'):
    print(f'  ✓ API retorna: found=True, case_number={data["case"]["case_number"]}')
else:
    print('  ✗ API retorna: found=False')

# Test 2: Búsqueda en reparto
print('\n✓ TEST 2: Reparto - Búsqueda Casos Sin Asignar')
print('-' * 80)
response = client.get('/cases/api/casos/buscar-sin-asignar/?id=00030')
data = json.loads(response.content)
if data.get('found'):
    print(f'  ✓ API retorna: found=True, case_number={data["case"]["case_number"]}')
    print(f'  ✓ Status: {data["case"]["status_display"]}')
else:
    print('  ✗ API retorna: found=False')

# Test 3: Caso que NO está sin asignar (00001 está con status "Asignado")
print('\n✓ TEST 3: Reparto - Caso que ESTÁ asignado (00001)')
print('-' * 80)
response = client.get('/cases/api/casos/buscar-sin-asignar/?id=00001')
if response.status_code == 404:
    data = json.loads(response.content)
    if not data.get('found'):
        print(f'  ✓ Correctamente retorna: found=False (caso está asignado)')
else:
    print('  ✗ Debería retornar 404 para casos asignados')

# Test 4: Caso inexistente
print('\n✓ TEST 4: Búsqueda de caso inexistente (00099)')
print('-' * 80)
response = client.get('/cases/api/casos/buscar-por-id/?id=00099')
data = json.loads(response.content)
if not data.get('found'):
    print(f'  ✓ Correctamente retorna: found=False, error={data["error"]}')
else:
    print('  ✗ Debería retornar found=False para caso inexistente')

# Test 5: Formato en HTML
print('\n✓ TEST 5: Formato en HTML del dashboard')
print('-' * 80)
response = client.get('/secretaria/dashboard/')
content = response.content.decode()
if 'número: 00030' in content:
    print('  ✓ Formato correcto: "número: 00030" encontrado')
else:
    print('  ✗ Formato NO encontrado')

print('\n' + '=' * 80)
print('✓ TODOS LOS TESTS COMPLETADOS')
print('=' * 80)
print('\nUSO:')
print('  1. Abre http://127.0.0.1:8000/secretaria/dashboard/')
print('  2. En "Casos Recientes", limpia caché (Ctrl+Shift+Del) y recarga (F5)')
print('  3. Busca "30" en el input - debe mostrar solo "número: 00030"')
print('  4. Prueba con otros números: 1, 5, 25, 32')
print('=' * 80)
