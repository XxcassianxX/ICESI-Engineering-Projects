#!/usr/bin/env python
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
from cases.models import Case
from accounts.models import User

print('=' * 70)
print('TEST DE ENDPOINTS DE BÚSQUEDA')
print('=' * 70)

# Crear cliente de prueba
client = Client()

# Obtener un usuario para autenticación
try:
    secretaria = User.objects.get(document_number='1001')
    print(f'\n✓ Usuario encontrado: {secretaria.full_name} ({secretaria.role})')
except User.DoesNotExist:
    print('\n✗ No se encontró usuario de prueba')
    exit(1)

# Hacer login
login_result = client.login(username=secretaria.document_number, password='1234')
if login_result:
    print('✓ Login exitoso')
else:
    print('✗ Login fallido')
    exit(1)

# PRUEBA 1: Búsqueda en todos (API)
print('\n' + '-' * 70)
print('TEST 1: API /cases/api/casos/buscar-por-id/ (todos los casos)')
print('-' * 70)

test_ids = [
    ('00001', True, 'Caso asignado - debe encontrar'),
    ('00005', True, 'Caso sin asignar - debe encontrar'),
    ('99999', False, 'Caso inexistente - no debe encontrar'),
]

for case_id, should_find, description in test_ids:
    response = client.get(f'/cases/api/casos/buscar-por-id/?id={case_id}')
    data = json.loads(response.content)
    
    if should_find:
        if data.get('found'):
            print(f'✓ {description}: ENCONTRADO')
            print(f'  Respuesta: {data["case"]["case_number"]} ({data["case"]["status_display"]})')
        else:
            print(f'✗ {description}: NO ENCONTRADO (ERROR)')
    else:
        if not data.get('found'):
            print(f'✓ {description}: NO ENCONTRADO (correcto)')
        else:
            print(f'✗ {description}: ENCONTRADO (ERROR)')

# PRUEBA 2: Búsqueda en sin asignar solo
print('\n' + '-' * 70)
print('TEST 2: API /cases/api/casos/buscar-sin-asignar/ (solo sin asignar)')
print('-' * 70)

test_ids_unassigned = [
    ('00001', False, 'Caso ASIGNADO - no debe encontrar'),
    ('00005', True, 'Caso SIN ASIGNAR - debe encontrar'),
    ('99999', False, 'Caso inexistente - no debe encontrar'),
]

for case_id, should_find, description in test_ids_unassigned:
    response = client.get(f'/cases/api/casos/buscar-sin-asignar/?id={case_id}')
    data = json.loads(response.content)
    
    if should_find:
        if data.get('found'):
            print(f'✓ {description}: ENCONTRADO')
            print(f'  Respuesta: {data["case"]["case_number"]} ({data["case"]["status_display"]})')
        else:
            print(f'✗ {description}: NO ENCONTRADO (ERROR)')
    else:
        if not data.get('found'):
            print(f'✓ {description}: NO ENCONTRADO (correcto)')
        else:
            print(f'✗ {description}: ENCONTRADO (ERROR)')

# PRUEBA 3: Validación de entrada
print('\n' + '-' * 70)
print('TEST 3: Validación de entrada')
print('-' * 70)

invalid_inputs = [
    ('ABC12', 400, 'Letras - debe rechazar'),
    ('1234', 400, 'Menos de 5 dígitos - puede aceptar (se completa con ceros)'),
    ('', 400, 'Vacío - debe rechazar'),
]

for input_val, expected_status, description in invalid_inputs:
    response = client.get(f'/cases/api/casos/buscar-por-id/?id={input_val}')
    if response.status_code == expected_status or input_val == '1234':
        print(f'✓ {description}: Status {response.status_code}')
    else:
        print(f'✗ {description}: Status {response.status_code} (esperado {expected_status})')

# PRUEBA 4: Conversión de entrada de usuario
print('\n' + '-' * 70)
print('TEST 4: Conversión de entrada (0-padding)')
print('-' * 70)

# Simular lo que hace el JS: "1" -> "00001"
user_inputs = ['1', '5', '25', '32']
for user_input in user_inputs:
    padded = str(int(user_input)).zfill(5)
    response = client.get(f'/cases/api/casos/buscar-por-id/?id={padded}')
    data = json.loads(response.content)
    
    if data.get('found'):
        print(f'✓ Input usuario "{user_input}" -> API "{padded}": ENCONTRADO ({data["case"]["sequence_number"]}. {data["case"]["case_number"]})')
    else:
        print(f'✗ Input usuario "{user_input}" -> API "{padded}": NO ENCONTRADO')

print('\n' + '=' * 70)
print('✓ TODOS LOS TESTS COMPLETADOS')
print('=' * 70)
