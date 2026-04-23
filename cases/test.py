from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import Area, Estudiante, Caso
from .services import asignar_caso_automatico

User = get_user_model()

class RepartoAutomaticoTests(TestCase):
    
    def setUp(self):
        """
        Esta función setUp se ejecuta ANTES de cada prueba. 
        Prepara una base de datos temporal en blanco con datos ficticios.
        """
        self.grupo_secretaria = Group.objects.create(name='Secretaria')
        self.secretaria = User.objects.create_user(document_number='11111', password='password123')
        self.secretaria.groups.add(self.grupo_secretaria)
        self.intruso = User.objects.create_user(document_number='99999', password='password123')
        self.area_penal = Area.objects.create(nombre='Penal')
        user_est1 = User.objects.create_user(document_number='22222', password='pw')
        self.est1 = Estudiante.objects.create(usuario=user_est1, area=self.area_penal)
        Caso.objects.create(titulo="Caso Viejo", area=self.area_penal, estado='Asignado', estudiante_asignado=self.est1)
        user_est2 = User.objects.create_user(document_number='33333', password='pw')
        self.est2 = Estudiante.objects.create(usuario=user_est2, area=self.area_penal)
        self.caso_nuevo = Caso.objects.create(titulo='Robo a mano armada', area=self.area_penal, estado='Pendiente')

    def test_reparto_exitoso_menor_carga(self):
        """Prueba que el algoritmo elige al estudiante con menos casos."""
        
        exito, mensaje = asignar_caso_automatico(self.caso_nuevo.id, self.secretaria)
        self.caso_nuevo.refresh_from_db()
        self.assertTrue(exito)
        self.assertEqual(self.caso_nuevo.estado, 'Asignado')
        self.assertEqual(self.caso_nuevo.estudiante_asignado, self.est2) 

    def test_reparto_falla_por_permisos(self):
        """Prueba que un usuario sin el rol de Secretaria es bloqueado."""
        exito, mensaje = asignar_caso_automatico(self.caso_nuevo.id, self.intruso)
        self.assertFalse(exito)
        self.assertEqual(mensaje, "Error: Solo Secretaría puede ejecutar el reparto.")