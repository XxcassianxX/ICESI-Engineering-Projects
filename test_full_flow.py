#!/usr/bin/env python
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
from accounts.models import User

print('=== TEST DE API CON LA BÚSQUEDA "30" ===\n')

client = Client()
user = User.objects.get(document_number='1001')
client.login(username='1001', password='1234')

# Simular lo que hace JavaScript con "30"
search_input = '30'
padded = str(int(search_input)).zfill(5)
print(f'1. Usuario ingresa: "{search_input}"')
print(f'2. JavaScript convierte a: "{padded}"')
print(f'3. Llama a API: /cases/api/casos/buscar-por-id/?id={padded}\n')

# Hacer la petición igual que JavaScript
response = client.get(f'/cases/api/casos/buscar-por-id/?id={padded}')
print(f'4. Respuesta HTTP Status: {response.status_code}')

if response.status_code == 200:
    data = json.loads(response.content)
    print(f'5. Respuesta JSON:')
    print(f'   - found: {data.get("found")}')
    print(f'   - case.id: {data.get("case", {}).get("id")}')
    print(f'   - case.case_number: {data.get("case", {}).get("case_number")}')
    print(f'   - case.sequence_number: {data.get("case", {}).get("sequence_number")}')
    print(f'   - case.beneficiary_name: {data.get("case", {}).get("beneficiary_name")}')
else:
    print(f'5. Error en respuesta: {response.content.decode()[:200]}')

# Ahora ver si el dashboard renderiza bien el caso
print('\n=== TEST DE RENDERIZADO DEL DASHBOARD ===\n')

response = client.get('/secretaria/dashboard/')
print(f'6. Acceso al dashboard HTTP Status: {response.status_code}')

content = response.content.decode()
if 'número: 00030' in content:
    print('7. ✓ Formato "número: 00030" encontrado en HTML')
else:
    print('7. ✗ Formato "número: 00030" NO encontrado en HTML')

# Ver si data-case-number tiene 00030
if 'data-case-number="00030"' in content:
    print('8. ✓ Atributo data-case-number="00030" encontrado')
elif 'data-case-number' in content:
    import re
    matches = re.findall(r'data-case-number="([^"]*)"', content)
    print(f'8. ✗ Atributos data-case-number encontrados: {matches}')
else:
    print('8. ✗ Atributo data-case-number NO encontrado')

print('\n=== CONCLUSIÓN ===')
print('Si case.id es diferente en JavaScript al hacer match, ese es el problema.')
print('El match es: /casos/(\d+)/ donde \\d+ es el ID de Django')
print('El API devuelve case.id que es el ID de Django')
