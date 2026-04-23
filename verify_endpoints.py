#!/usr/bin/env python
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
from accounts.models import User

print('=' * 80)
print('VERIFICACIÓN DE ENDPOINTS - CASOS RECIENTES vs REPARTO')
print('=' * 80)

client = Client()
user = User.objects.get(document_number='1001')
client.login(username='1001', password='1234')

# Casos de prueba: uno asignado (00001) y uno sin asignar (00030)
test_cases = [
    ('00001', 'ASIGNADO', 'ASI'),
    ('00030', 'SIN ASIGNAR', 'SIN'),
]

for case_id, status_name, status_code in test_cases:
    print(f'\n{"=" * 80}')
    print(f'Probando Caso: {case_id} ({status_name})')
    print("=" * 80)
    
    # Verificar status real en BD
    from cases.models import Case
    case = Case.objects.get(case_number=case_id)
    print(f'BD Status: {case.get_status_display()} (status={case.status})')
    
    # Test 1: Casos Recientes (TODOS)
    print(f'\n1. CASOS RECIENTES (buscar en TODOS):')
    response = client.get(f'/cases/api/casos/buscar-por-id/?id={case_id}')
    data = json.loads(response.content)
    if data.get('found'):
        print(f'   ✓ ENCONTRADO en Casos Recientes')
    else:
        print(f'   ✗ NO ENCONTRADO en Casos Recientes')
    
    # Test 2: Reparto (SOLO sin asignar)
    print(f'\n2. REPARTO DE CASOS (buscar SOLO SIN ASIGNAR):')
    response = client.get(f'/cases/api/casos/buscar-sin-asignar/?id={case_id}')
    if response.status_code == 200:
        data = json.loads(response.content)
        if data.get('found'):
            print(f'   ✓ ENCONTRADO en Reparto')
        else:
            print(f'   ✗ NO ENCONTRADO en Reparto')
    else:
        data = json.loads(response.content)
        if not data.get('found'):
            print(f'   ✓ NO ENCONTRADO en Reparto (correcto - está {status_name})')

print('\n' + '=' * 80)
print('RESUMEN:')
print('=' * 80)
print('✓ CASOS RECIENTES (00001 asignado): Debe estar')
print('✓ CASOS RECIENTES (00030 sin asignar): Debe estar')
print('✓ REPARTO (00001 asignado): NO debe estar')
print('✓ REPARTO (00030 sin asignar): Debe estar')
print('=' * 80)
