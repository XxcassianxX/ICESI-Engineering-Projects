import os
import django
import random
from faker import Faker

# Configurar el entorno de Django para poder ejecutar el script por fuera
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings') 
django.setup()

from accounts.models import User
from cases.models import Case

fake = Faker('es_CO')

def run_seed():
    print(" Iniciando la siembra de datos...")

    # 1. Crear 20 Usuarios Aleatorios
    print("Creando usuarios...")
    roles = [User.Role.BENEFICIARIO, User.Role.ESTUDIANTE, User.Role.ASESOR]
    usuarios_creados = []
    
    for _ in range(20):
        user = User.objects.create_user(
            document_number=str(fake.unique.random_number(digits=10)),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            role=random.choice(roles)
        )
        usuarios_creados.append(user)

    # Filtrar usuarios por rol para las asignaciones
    beneficiarios = [u for u in usuarios_creados if u.role == User.Role.BENEFICIARIO]
    estudiantes = [u for u in usuarios_creados if u.role == User.Role.ESTUDIANTE]

    # 2. Crear 30 Casos Aleatorios
    print("Creando casos...")
    categorias = [Case.CaseCategory.PENAL, Case.CaseCategory.LABORAL, Case.CaseCategory.CIVIL]
    estados = [Case.CaseStatus.SIN_ASIGNAR, Case.CaseStatus.ASIGNADO, Case.CaseStatus.EN_PROCESO]

    if not beneficiarios:
        print(" No hay beneficiarios para asignar casos.")
        return

    for _ in range(30):
        Case.objects.create(
            beneficiary=random.choice(beneficiarios),
            assigned_student=random.choice(estudiantes) if estudiantes and random.choice([True, False]) else None,
            title=fake.sentence(nb_words=6),
            description=fake.paragraph(nb_sentences=3),
            category=random.choice(categorias),
            status=random.choice(estados),
            phone=fake.phone_number(),
            address=fake.address()
        )

    print(" ¡Siembra de datos exitosa! Creados 20 usuarios y 30 casos en Neon.")

if __name__ == '__main__':
    run_seed()