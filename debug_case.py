#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from cases.models import Case

print('=== BÚSQUEDA DE CASO 00030 ===')
try:
    case = Case.objects.get(case_number='00030')
    print(f'✓ Caso ENCONTRADO: ID={case.id}, case_number={case.case_number}, beneficiary={case.beneficiary.full_name}, status={case.status}')
except Case.DoesNotExist:
    print('✗ Caso 00030 NO ENCONTRADO')

print('\n=== PRUEBA DE PADDING ===')
search_input = '30'
padded = str(int(search_input)).zfill(5)
print(f'Input: "{search_input}" -> Padded: "{padded}"')

try:
    case = Case.objects.get(case_number=padded)
    print(f'✓ Caso ENCONTRADO con búsqueda: {case.case_number}')
except Case.DoesNotExist:
    print(f'✗ Caso {padded} NO ENCONTRADO')

print('\n=== TODOS LOS CASOS ===')
for case in Case.objects.all().order_by('case_number'):
    print(f'{case.sequence_number:2}. {case.case_number} - {case.status} - {case.beneficiary.full_name}')
