#!/usr/bin/env python
import os
import django
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
from accounts.models import User

client = Client()
user = User.objects.get(document_number='1001')
client.login(username='1001', password='1234')

response = client.get('/secretaria/dashboard/')
content = response.content.decode()

# Buscar los hrefs de los casos
print('=== BÚSQUEDA DE HREFS EN CASOS RECIENTES ===\n')

# Buscar los links de casos que contain "00030"
pattern = r'<a href="([^"]*)" class="recent-case-item[^>]*>[\s\S]*?(?:00030|número:)[\s\S]*?</a>'
matches = re.findall(pattern, content, re.DOTALL)

print(f'Links encontrados: {len(matches)}')
for match in matches[:5]:
    print(f'  Link: {match}')

# Buscar todos los recent-case-item links
print('\n=== PRIMER CASO RECIENTE (00001 o 00030) ===\n')
pattern = r'<a href="([^"]*)" class="recent-case-item'
matches = re.findall(pattern, content)
print(f'Total de links recent-case-item: {len(matches)}')
if matches:
    print(f'Primer link: {matches[0]}')
    # Extraer ID
    id_match = re.search(r'/cases/(\d+)/', matches[0])
    if id_match:
        print(f'ID extraído: {id_match.group(1)}')

# Buscar específicamente para caso 00030
print('\n=== BÚSQUEDA ESPECÍFICA PARA 00030 ===\n')
lines = content.split('\n')
for i, line in enumerate(lines):
    if '00030' in line:
        # Print 5 líneas antes y después
        start = max(0, i-5)
        end = min(len(lines), i+5)
        print(f'Encontrado en línea {i}:')
        for j in range(start, end):
            marker = '>>> ' if j == i else '    '
            print(f'{marker}{lines[j][:100]}')
        break
