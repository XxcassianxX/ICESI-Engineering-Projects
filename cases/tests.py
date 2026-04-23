import os
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import User
from .models import AttachedDocument, BitacoraEntry, Case


TEST_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class CasesFlowTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.secretaria = User.objects.create_user(
            document_number="1000000001",
            password="123456",
            first_name="Ana María",
            last_name="López",
            role=User.Role.SECRETARIA,
            email="secretaria@email.com",
            is_active=True,
        )

        self.estudiante_actual = User.objects.create_user(
            document_number="1000000002",
            password="123456",
            first_name="Carlos",
            last_name="Ramírez",
            role=User.Role.ESTUDIANTE,
            email="estudiante@email.com",
            is_active=True,
        )

        self.estudiante_nuevo = User.objects.create_user(
            document_number="1000000004",
            password="123456",
            first_name="Laura",
            last_name="Torres",
            role=User.Role.ESTUDIANTE,
            email="laura@email.com",
            is_active=True,
        )

        self.asesor = User.objects.create_user(
            document_number="1000000003",
            password="123456",
            first_name="Roberto",
            last_name="Gómez",
            role=User.Role.ASESOR,
            email="asesor@email.com",
            is_active=True,
        )

        self.beneficiario = User.objects.create_user(
            document_number="1234567890",
            password="1234567890",
            first_name="María",
            last_name="González Pérez",
            role=User.Role.BENEFICIARIO,
            email="maria@email.com",
            is_active=True,
        )

        self.case = Case.objects.create(
            case_number="12345",
            title="Caso de familia - custodia y visitas",
            description="Solicitud de regulación de visitas y cuota alimentaria para menor de edad.",
            case_type=Case.CaseType.FAMILIA,
            status=Case.CaseStatus.ASIGNADO,
            beneficiary=self.beneficiario,
            assigned_student=self.estudiante_actual,
            advisor=self.asesor,
            secretary=self.secretaria,
        )

    def tearDown(self):
        for document in AttachedDocument.objects.all():
            if document.file and hasattr(document.file, "path") and os.path.isfile(document.file.path):
                os.remove(document.file.path)

    def test_secretaria_puede_reasignar_caso(self):
        self.client.force_login(self.secretaria)

        response = self.client.post(
            reverse("reassign_case", args=[self.case.id]),
            {
                "new_student": self.estudiante_nuevo.id,
                "reason": "Balanceo de carga entre estudiantes",
            },
            follow=True,
        )

        self.case.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.case.assigned_student, self.estudiante_nuevo)

        bitacora = BitacoraEntry.objects.filter(case=self.case).order_by("-created_at").first()
        self.assertIsNotNone(bitacora)
        self.assertEqual(bitacora.author, self.secretaria)
        self.assertEqual(bitacora.entry_type, BitacoraEntry.EntryType.ASIGNACION)
        self.assertIn("Balanceo de carga", bitacora.content)

    def test_secretaria_no_puede_reasignar_al_mismo_estudiante(self):
        self.client.force_login(self.secretaria)

        response = self.client.post(
            reverse("reassign_case", args=[self.case.id]),
            {
                "new_student": self.estudiante_actual.id,
                "reason": "Intento inválido",
            },
            follow=True,
        )

        self.case.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.case.assigned_student, self.estudiante_actual)
        self.assertContains(
            response,
            "Debes seleccionar un estudiante diferente al que ya tiene asignado el caso."
        )
        self.assertEqual(BitacoraEntry.objects.filter(case=self.case).count(), 0)

    def test_estudiante_no_puede_reasignar_caso(self):
        self.client.force_login(self.estudiante_actual)

        response = self.client.post(
            reverse("reassign_case", args=[self.case.id]),
            {
                "new_student": self.estudiante_nuevo.id,
                "reason": "Intento no autorizado",
            },
            follow=True,
        )

        self.case.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.case.assigned_student, self.estudiante_actual)
        self.assertEqual(BitacoraEntry.objects.filter(case=self.case).count(), 0)

    def test_no_se_reasigna_si_estudiante_no_existe(self):
        self.client.force_login(self.secretaria)

        response = self.client.post(
            reverse("reassign_case", args=[self.case.id]),
            {
                "new_student": 999999,
                "reason": "Prueba estudiante inválido",
            },
            follow=True,
        )

        self.case.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.case.assigned_student, self.estudiante_actual)
        self.assertContains(response, "El estudiante seleccionado no es válido.")

    def test_si_caso_estaba_sin_asignar_pasa_a_asignado(self):
        self.case.assigned_student = None
        self.case.status = Case.CaseStatus.SIN_ASIGNAR
        self.case.save()

        self.client.force_login(self.secretaria)

        response = self.client.post(
            reverse("reassign_case", args=[self.case.id]),
            {
                "new_student": self.estudiante_nuevo.id,
                "reason": "Asignación inicial",
            },
            follow=True,
        )

        self.case.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.case.assigned_student, self.estudiante_nuevo)
        self.assertEqual(self.case.status, Case.CaseStatus.ASIGNADO)

    def test_estudiante_puede_subir_documento_valido_y_guardar_metadata(self):
        self.client.force_login(self.estudiante_actual)

        archivo = SimpleUploadedFile(
            "evidencia.pdf",
            b"%PDF-1.4 archivo de prueba",
            content_type="application/pdf"
        )

        response = self.client.post(
            reverse("case_bitacora", args=[self.case.id]),
            data={
                "entry_type": BitacoraEntry.EntryType.DOCUMENTO,
                "content": "Se adjunta evidencia del caso.",
                "notify": False,
                "files": [archivo],
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)

        entry = BitacoraEntry.objects.filter(
            case=self.case,
            author=self.estudiante_actual
        ).order_by("-created_at").first()

        self.assertIsNotNone(entry)
        self.assertEqual(entry.entry_type, BitacoraEntry.EntryType.DOCUMENTO)

        documento = AttachedDocument.objects.filter(entry=entry).first()
        self.assertIsNotNone(documento)
        self.assertEqual(documento.original_name, "evidencia.pdf")
        self.assertTrue(bool(documento.file))
        self.assertEqual(documento.file_size, len(b"%PDF-1.4 archivo de prueba"))
        self.assertEqual(documento.content_type, "application/pdf")
        self.assertIsNotNone(documento.uploaded_at)

    def test_secretaria_tambien_puede_subir_documento(self):
        self.client.force_login(self.secretaria)

        archivo = SimpleUploadedFile(
            "memo.pdf",
            b"%PDF-1.4 memo",
            content_type="application/pdf"
        )

        response = self.client.post(
            reverse("case_bitacora", args=[self.case.id]),
            data={
                "entry_type": BitacoraEntry.EntryType.ACTUALIZACION,
                "content": "Secretaría adjunta soporte administrativo.",
                "notify": True,
                "files": [archivo],
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)

        entry = BitacoraEntry.objects.filter(
            case=self.case,
            author=self.secretaria
        ).order_by("-created_at").first()

        self.assertIsNotNone(entry)
        documento = AttachedDocument.objects.filter(entry=entry).first()
        self.assertIsNotNone(documento)
        self.assertEqual(documento.original_name, "memo.pdf")

    def test_beneficiario_no_puede_subir_documento(self):
        self.client.force_login(self.beneficiario)

        archivo = SimpleUploadedFile(
            "archivo.pdf",
            b"%PDF-1.4 test",
            content_type="application/pdf"
        )

        response = self.client.post(
            reverse("case_bitacora", args=[self.case.id]),
            data={
                "entry_type": BitacoraEntry.EntryType.DOCUMENTO,
                "content": "Intento no autorizado.",
                "notify": False,
                "files": [archivo],
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(AttachedDocument.objects.count(), 0)

    def test_estudiante_no_asignado_no_puede_subir_documento(self):
        otro_estudiante = User.objects.create_user(
            document_number="1000000005",
            password="123456",
            first_name="Mateo",
            last_name="Ruiz",
            role=User.Role.ESTUDIANTE,
            email="mateo@email.com",
            is_active=True,
        )

        self.client.force_login(otro_estudiante)

        archivo = SimpleUploadedFile(
            "archivo.pdf",
            b"%PDF-1.4 test",
            content_type="application/pdf"
        )

        response = self.client.post(
            reverse("case_bitacora", args=[self.case.id]),
            data={
                "entry_type": BitacoraEntry.EntryType.DOCUMENTO,
                "content": "Intento no autorizado del estudiante no asignado.",
                "notify": False,
                "files": [archivo],
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(AttachedDocument.objects.count(), 0)

    def test_se_guardan_dos_documentos_en_una_misma_entrada(self):
        self.client.force_login(self.estudiante_actual)

        archivo1 = SimpleUploadedFile(
            "doc1.pdf",
            b"%PDF-1.4 uno",
            content_type="application/pdf"
        )
        archivo2 = SimpleUploadedFile(
            "doc2.pdf",
            b"%PDF-1.4 dos",
            content_type="application/pdf"
        )

        response = self.client.post(
            reverse("case_bitacora", args=[self.case.id]),
            data={
                "entry_type": BitacoraEntry.EntryType.DOCUMENTO,
                "content": "Se adjuntan dos soportes.",
                "notify": False,
                "files": [archivo1, archivo2],
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)

        entry = BitacoraEntry.objects.filter(
            case=self.case,
            author=self.estudiante_actual
        ).order_by("-created_at").first()

        self.assertIsNotNone(entry)

        documentos = AttachedDocument.objects.filter(entry=entry).order_by("original_name")
        self.assertEqual(documentos.count(), 2)
        self.assertEqual(documentos[0].original_name, "doc1.pdf")
        self.assertEqual(documentos[1].original_name, "doc2.pdf")

    def test_rechaza_formato_no_permitido(self):
        self.client.force_login(self.estudiante_actual)

        archivo = SimpleUploadedFile(
            "malicioso.exe",
            b"MZ fake exe",
            content_type="application/x-msdownload"
        )

        response = self.client.post(
            reverse("case_bitacora", args=[self.case.id]),
            data={
                "entry_type": BitacoraEntry.EntryType.DOCUMENTO,
                "content": "Intento subir exe.",
                "notify": False,
                "files": [archivo],
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Formato no permitido")
        self.assertEqual(AttachedDocument.objects.count(), 0)

    def test_rechaza_archivo_muy_pesado(self):
        self.client.force_login(self.estudiante_actual)

        contenido = b"a" * (5 * 1024 * 1024 + 1)
        archivo = SimpleUploadedFile(
            "grande.pdf",
            contenido,
            content_type="application/pdf"
        )

        response = self.client.post(
            reverse("case_bitacora", args=[self.case.id]),
            data={
                "entry_type": BitacoraEntry.EntryType.DOCUMENTO,
                "content": "Intento subir archivo grande.",
                "notify": False,
                "files": [archivo],
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "supera el tamaño máximo permitido")
        self.assertEqual(AttachedDocument.objects.count(), 0)


# =========================
# HU3 - REPARTO DE CASOS
# =========================

class CaseDistributionTests(TestCase):
    """Pruebas para la funcionalidad de Reparto de Casos (HU3)."""

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """Configura datos para las pruebas de reparto."""
        from cases.models import CaseDocument
        from cases.services import CaseCompletionValidator

        self.secretary = User.objects.create_user(
            document_number='SEC001',
            first_name='Secretaria',
            last_name='Reparto',
            role=User.Role.SECRETARIA,
            password='testpass123',
            is_active=True,
        )

        self.advisor = User.objects.create_user(
            document_number='ADV001',
            first_name='Asesor',
            last_name='Reparto',
            role=User.Role.ASESOR,
            password='testpass123',
            is_active=True,
        )

        self.student = User.objects.create_user(
            document_number='EST001',
            first_name='Estudiante',
            last_name='Reparto',
            role=User.Role.ESTUDIANTE,
            is_active=True,
            password='testpass123'
        )

        self.beneficiary = User.objects.create_user(
            document_number='BEN001',
            first_name='Beneficiario',
            last_name='Reparto',
            role=User.Role.BENEFICIARIO,
            password='testpass123'
        )

        self.case_complete = Case.objects.create(
            case_number='DIST-001',
            beneficiary=self.beneficiary,
            title='Caso Completo para Reparto',
            description='Descripción del caso completo',
            case_type=Case.CaseType.FAMILIA,
            status=Case.CaseStatus.PENDING_DISTRIBUTION,
        )

        # Crear documentos válidos
        CaseDocument.objects.create(
            case=self.case_complete,
            document_type=CaseDocument.DocumentType.DOCUMENTO,
            file='test_file.pdf',
            is_valid=True,
        )
        CaseDocument.objects.create(
            case=self.case_complete,
            document_type=CaseDocument.DocumentType.RECIBO_SERVICIOS,
            file='test_file.pdf',
            is_valid=True,
        )
        CaseDocument.objects.create(
            case=self.case_complete,
            document_type=CaseDocument.DocumentType.FOTO,
            file='test_file.pdf',
            is_valid=True,
        )

    def test_solo_secretaria_puede_acceder_distribucion(self):
        """Verifica que solo Secretaría pueda acceder a la pantalla de reparto."""
        # Estudiante no puede acceder
        self.client.force_login(self.student)
        response = self.client.get(
            reverse('case_distribution', args=[self.case_complete.id]),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Reparto de Casos')

        # Secretaría sí puede acceder
        self.client.force_login(self.secretary)
        response = self.client.get(
            reverse('case_distribution', args=[self.case_complete.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Reparto de Casos')

    def test_advisor_can_access_distribution(self):
        """Verifica que los Asesores también pueden acceder."""
        self.client.force_login(self.advisor)
        response = self.client.get(
            reverse('case_distribution', args=[self.case_complete.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Reparto de Casos')

    def test_vista_muestra_estado_completo(self):
        """Verifica que la vista muestra 'Completo' para un caso completo."""
        self.client.force_login(self.secretary)
        response = self.client.get(
            reverse('case_distribution', args=[self.case_complete.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Completo')

    def test_vista_muestra_estado_incompleto(self):
        """Verifica que la vista muestra 'Incompleto' para un caso sin documentos."""
        case_incomplete = Case.objects.create(
            case_number='DIST-002',
            beneficiary=self.beneficiary,
            title='Caso Incompleto',
            description='Descripción',
            case_type=Case.CaseType.CIVIL,
            status=Case.CaseStatus.PENDING_DISTRIBUTION,
        )

        self.client.force_login(self.secretary)
        response = self.client.get(
            reverse('case_distribution', args=[case_incomplete.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Incompleto')

    def test_asignacion_manual_exitosa(self):
        """Verifica que un caso completo se puede asignar manualmente."""
        self.client.force_login(self.secretary)

        response = self.client.post(
            reverse('case_distribution', args=[self.case_complete.id]),
            {
                'category': Case.CaseType.FAMILIA,
                'case_type': Case.CaseType.FAMILIA,
                'assigned_student': self.student.id,
                'notes': 'Asignación de prueba',
            },
            follow=True
        )

        # Verificar que el caso fue asignado
        self.case_complete.refresh_from_db()
        self.assertEqual(self.case_complete.assigned_student, self.student)
        self.assertEqual(self.case_complete.status, Case.CaseStatus.ASIGNADO)

        # Verificar que se creó registro en CaseAssignment
        from cases.models import CaseAssignment
        assignment = CaseAssignment.objects.get(case=self.case_complete)
        self.assertEqual(assignment.assigned_student, self.student)
        self.assertEqual(assignment.assigned_advisor, self.secretary)

        # Verificar que se creó entrada en bitácora
        bitacora = BitacoraEntry.objects.get(
            case=self.case_complete,
            entry_type=BitacoraEntry.EntryType.CASO_ASIGNADO_MANUALMENTE
        )
        self.assertEqual(bitacora.author, self.secretary)

    def test_caso_incompleto_envio_revision(self):
        """Verifica que un caso incompleto se envía a revisión."""
        case_incomplete = Case.objects.create(
            case_number='DIST-003',
            beneficiary=self.beneficiary,
            title='Caso Incompleto',
            description='Descripción',
            case_type=Case.CaseType.LABORAL,
            status=Case.CaseStatus.PENDING_DISTRIBUTION,
        )

        self.client.force_login(self.secretary)

        response = self.client.post(
            reverse('case_distribution', args=[case_incomplete.id]),
            {
                'reason': 'Falta documentación',
            },
            follow=True
        )

        # Verificar que el estado cambió a UNDER_REVIEW
        case_incomplete.refresh_from_db()
        self.assertEqual(case_incomplete.status, Case.CaseStatus.UNDER_REVIEW)

        # Verificar que se creó entrada en bitácora
        bitacora = BitacoraEntry.objects.get(
            case=case_incomplete,
            entry_type=BitacoraEntry.EntryType.CASO_ENVIADO_REVISION
        )
        self.assertIn('Falta documentación', bitacora.content)

    def test_no_se_puede_asignar_caso_no_pending(self):
        """Verifica que no se pueda asignar un caso que no esté en PENDING_DISTRIBUTION."""
        self.case_complete.status = Case.CaseStatus.ASIGNADO
        self.case_complete.save()

        self.client.force_login(self.secretary)
        response = self.client.get(
            reverse('case_distribution', args=[self.case_complete.id])
        )

        self.assertContains(response, 'no está disponible para reparto')

    def test_boton_asignar_habilitado_para_completo(self):
        """Verifica que el botón 'Asignar Caso' está habilitado para casos completos."""
        self.client.force_login(self.secretary)
        response = self.client.get(
            reverse('case_distribution', args=[self.case_complete.id])
        )

        self.assertContains(response, 'Asignar Caso')
        # El botón NO debe tener disabled
        self.assertNotIn('disabled', response.content.decode().split('Asignar Caso')[0].split('<button')[-1])

    def test_boton_revision_habilitado_para_incompleto(self):
        """Verifica que el botón 'Enviar a Revisión' está para casos incompletos."""
        case_incomplete = Case.objects.create(
            case_number='DIST-004',
            beneficiary=self.beneficiary,
            title='Caso Incompleto',
            description='Descripción',
            case_type=Case.CaseType.PENAL,
            status=Case.CaseStatus.PENDING_DISTRIBUTION,
        )

        self.client.force_login(self.secretary)
        response = self.client.get(
            reverse('case_distribution', args=[case_incomplete.id])
        )

        self.assertContains(response, 'Enviar a Revisión')

    def test_validacion_campo_estudiante_requerido(self):
        """Verifica que el campo estudiante es obligatorio."""
        self.client.force_login(self.secretary)

        response = self.client.post(
            reverse('case_distribution', args=[self.case_complete.id]),
            {
                'category': Case.CaseType.FAMILIA,
                'case_type': Case.CaseType.FAMILIA,
                'assigned_student': '',  # Campo vacío
                'notes': '',
            },
            follow=True
        )

        # El caso NO debe estar asignado
        self.case_complete.refresh_from_db()
        self.assertIsNone(self.case_complete.assigned_student)

    def test_trazabilidad_quién_asignó(self):
        """Verifica que se registra quién realizó la asignación."""
        self.client.force_login(self.secretary)

        self.client.post(
            reverse('case_distribution', args=[self.case_complete.id]),
            {
                'category': Case.CaseType.FAMILIA,
                'case_type': Case.CaseType.FAMILIA,
                'assigned_student': self.student.id,
                'notes': '',
            },
        )

        # Verificar que la bitácora registra al usuario que asignó
        bitacora = BitacoraEntry.objects.get(
            case=self.case_complete,
            entry_type=BitacoraEntry.EntryType.CASO_ASIGNADO_MANUALMENTE
        )
        self.assertEqual(bitacora.author, self.secretary)
        self.assertIn(self.secretary.full_name, bitacora.content)

    def test_solo_secretaria_y_asesor_pueden_asignar(self):
        """Verifica control de acceso para asignación."""
        from cases.services import CaseDistributionService

        # Beneficiario NO puede asignar
        can_assign, _ = CaseDistributionService.can_assign_case(
            self.case_complete,
            self.beneficiary
        )
        self.assertFalse(can_assign)

        # Secretaría SÍ puede asignar
        can_assign, _ = CaseDistributionService.can_assign_case(
            self.case_complete,
            self.secretary
        )
        self.assertTrue(can_assign)

        # Asesor SÍ puede asignar
        can_assign, _ = CaseDistributionService.can_assign_case(
            self.case_complete,
            self.advisor
        )
        self.assertTrue(can_assign)