#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from cases.models import Case

print('=' * 60)
print('VERIFICACIÓN DE DATOS Y BÚSQUEDA')
print('=' * 60)

# 1. Verificar primeros y últimos casos
print('\n1. PRIMEROS 5 CASOS')
print('-' * 60)
for case in Case.objects.order_by('case_number')[:5]:
    print(f'{case.sequence_number}. {case.case_number} - {case.status} - {case.beneficiary.full_name}')

print('\n2. ÚLTIMOS 5 CASOS')
print('-' * 60)
for case in Case.objects.order_by('-case_number')[:5]:
    print(f'{case.sequence_number}. {case.case_number} - {case.status} - {case.beneficiary.full_name}')

# 2. Pruebas de búsqueda simulando input del usuario
print('\n3. PRUEBAS DE BÚSQUEDA (simulando entrada del usuario)')
print('-' * 60)

test_searches = [
    '1',      # -> 00001
    '5',      # -> 00005
    '25',     # -> 00025
    '32',     # -> 00032
    '99',     # -> no existe
]

for search_input in test_searches:
    # Convertir como lo hace el JS (padStart)
    padded_id = str(int(search_input)).zfill(5)
    
    try:
        case = Case.objects.get(case_number=padded_id)
        print(f'✓ Input "{search_input}" -> ID "{padded_id}": ENCONTRADO ({case.sequence_number}. {case.case_number})')
    except Case.DoesNotExist:
        print(f'✗ Input "{search_input}" -> ID "{padded_id}": NO ENCONTRADO')

# 3. Casos sin asignar
print('\n4. CASOS SIN ASIGNAR (para "Reparto de Casos")')
print('-' * 60)
unassigned_cases = Case.objects.filter(status='SIN')
print(f'Total: {unassigned_cases.count()} casos')
print('Primeros 5:')
for case in unassigned_cases[:5]:
    print(f'  {case.sequence_number}. {case.case_number}')

# 4. Casos con otros estados
print('\n5. DISTRIBUCIÓN DE ESTADOS')
print('-' * 60)
for status, label in Case.CaseStatus.choices:
    count = Case.objects.filter(status=status).count()
    print(f'{label:25} -> {count:2} casos')

# 5. Verificar casos para "Casos Recientes" (todos)
print('\n6. CASOS RECIENTES (todos, asignados y sin asignar)')
print('-' * 60)
all_cases = Case.objects.all()
print(f'Total: {all_cases.count()} casos')
assigned = Case.objects.filter(status__in=['ASI', 'PRO', 'DOC'])
unassigned = Case.objects.filter(status='SIN')
closed = Case.objects.filter(status='CER')
print(f'  Asignados: {assigned.count()}')
print(f'  Sin asignar: {unassigned.count()}')
print(f'  Cerrados: {closed.count()}')

print('\n' + '=' * 60)
print('✓ VERIFICACIÓN COMPLETA')
print('=' * 60)
