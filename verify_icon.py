#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
from cases.models import Case

print('=' * 80)
print('VERIFICACIÓN DEL ÍCONO DE LUPA EN BÚSQUEDA')
print('=' * 80)

# Obtener un ID que NO existe
existing_ids = list(Case.objects.values_list('case_number', flat=True))
print(f'\nCasos existentes: {len(existing_ids)}')
print(f'Primeros 5: {sorted(existing_ids)[:5]}')
print(f'Últimos 5: {sorted(existing_ids)[-5:]}')

# Verificar que el código tiene el SVG
with open('templates/accounts/secretary_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()
    
    if 'showNoCasesFoundMessage' in content:
        print('\n✓ Función showNoCasesFoundMessage encontrada')
    
    # Buscar el SVG dentro de esa función
    start = content.find('function showNoCasesFoundMessage')
    end = content.find('hideNoCasesFoundMessage', start)
    func_content = content[start:end]
    
    if 'width="70" height="70"' in func_content and 'viewBox="0 0 70 70"' in func_content:
        print('✓ SVG de lupa (70x70) encontrado en showNoCasesFoundMessage')
    
    if '<circle cx="35" cy="35" r="32"' in func_content:
        print('✓ Círculo de fondo del SVG encontrado')
    
    if '<circle cx="32" cy="32" r="14"' in func_content:
        print('✓ Lupa (círculo pequeño) del SVG encontrado')
    
    if '<line x1="43" y1="43" x2="52" y2="52"' in func_content:
        print('✓ Línea de la lupa del SVG encontrada')
    
    if 'fill="#5b5ce2"' in func_content and 'stroke="#5b5ce2"' in func_content:
        print('✓ Color #5b5ce2 (violeta) configurado en el SVG')
    
    if 'opacity="0.2"' in func_content:
        print('✓ Transparencia del círculo de fondo configurada (0.2)')

print('\n' + '=' * 80)
print('INSTRUCCIONES FINALES:')
print('=' * 80)
print('1. Abre: http://127.0.0.1:8000/secretaria/dashboard/')
print('2. Limpia caché: Ctrl+Shift+Del → Todas › Cookies › Borrar')
print('3. Recarga: F5')
print('4. En "Casos Recientes" busca: 99 (no existe)')
print('5. Verás: Lupa violeta + "No se encuentra un caso con ese ID"')
print('6. Busca: 30 (existe)')
print('7. Verás: El caso resaltado en la lista')
print('=' * 80)
