from unittest import case

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class Case(models.Model):
    """
    Modelo principal del caso jurídico.
    Conserva campos de compatibilidad con versiones anteriores
    y agrega los nuevos necesarios para el sprint.
    """

    class CaseCategory(models.TextChoices):
        PENAL = "PEN", "Penal"
        PUBLICO = "PUB", "Público"
        LABORAL = "LAB", "Laboral"
        CIVIL = "CIV", "Civil"
        FAMILIA = "FAM", "Familia"
        ADMINISTRATIVO = "ADM", "Administrativo"

    class PenalType(models.TextChoices):
        DERECHO_FISCAL = "DER_FIS", "Derecho fiscal"
        DERECHO_DISCIPLINARIO = "DER_DIS", "Derecho disciplinario"
        PENAL = "PEN", "Penal"

    class PublicoType(models.TextChoices):
        MIGRANTES = "MIG", "Migrantes"
        DERECHO_ADMINISTRATIVO = "DER_ADM", "Derecho Administrativo y constitucional"

    class LaboralType(models.TextChoices):
        TUTELAS = "TUT", "Tutelas"
        LIQUIDACIONES = "LIQ", "Liquidaciones"
        PROCESOS = "PROC", "Procesos"

    class CivilType(models.TextChoices):
        CONCEPTOS = "CON", "Conceptos"
        PROCESOS = "PROC", "Procesos"

    class FamiliaType(models.TextChoices):
        CONCEPTOS = "CON", "Conceptos"
        PROCESOS = "PROC", "Procesos"

    class AdministrativoType(models.TextChoices):
        ASIGNADOS = "ASI", "Asignados"

    class CaseStatus(models.TextChoices):
        SIN_ASIGNAR = "SIN", "Sin asignar"
        DOCUMENTACION = "DOC", "Documentación"
        ASIGNADO = "ASI", "Asignado"
        EN_PROCESO = "PRO", "En proceso"
        ESPERANDO_USUARIO = "ESP", "Esperando por usuario"
        EN_REVISION = "REV", "En revisión"
        CERRADO = "CER", "Cerrado"

    class CaseStage(models.IntegerChoices):
        UNASSIGNED = 0, "Sin asignar"
        ASSIGNMENT = 1, "Asignación de Estudiante"
        INFORMATION_GATHERING = 2, "Recopilación de Información"
        ANALYSIS_DRAFTING = 3, "Análisis y Redacción"
        SUPERVISOR_REVIEW = 4, "Revisión con Supervisor"
        COURT_PRESENTATION = 5, "Presentación ante Juzgado"

    class ClosureType(models.TextChoices):
        FAVORABLE = "FAV", "A favor del beneficiario"
        NEGATIVE = "NEG", "Respuesta negativa al beneficiario"
        DISMISSED = "DIS", "Desistidos"

    case_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Número de caso",
    )

    sequence_number = models.IntegerField(
        unique=True,
        null=True,
        blank=True,
        verbose_name="Número secuencial",
        help_text="Número de orden del caso (1, 2, 3, ...)",
    )

    beneficiary = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="beneficiary_cases",
        verbose_name="Beneficiario",
    )

    assigned_student = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_cases",
        verbose_name="Estudiante asignado",
    )

    advisor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="advisor_cases",
        verbose_name="Asesor",
    )

    secretary = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_cases",
        verbose_name="Secretaría",
    )

    title = models.CharField(
        max_length=255,
        verbose_name="Título",
    )

    description = models.TextField(
        verbose_name="Descripción",
    )

    # Nueva estructura usada por reparto/manual/filtros
    category = models.CharField(
        max_length=10,
        choices=CaseCategory.choices,
        null=True,
        blank=True,
        verbose_name="Categoría",
    )

    case_type_specific = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="Tipo específico",
    )

    status = models.CharField(
        max_length=10,
        choices=CaseStatus.choices,
        default=CaseStatus.SIN_ASIGNAR,
        verbose_name="Estado",
    )

    current_stage = models.IntegerField(
        choices=CaseStage.choices,
        default=CaseStage.UNASSIGNED,
        verbose_name="Etapa actual del caso",
    )

    phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Teléfono",
    )

    address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Dirección",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización",
    )

    closure_type = models.CharField(
        max_length=10,
        choices=ClosureType.choices,
        null=True,
        blank=True,
        verbose_name="Tipo de cierre",
        help_text="Solo se llena cuando el caso se cierra",
    )

    class Meta:
        verbose_name = "Caso"
        verbose_name_plural = "Casos"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Caso {self.case_number}"

    def get_specific_type_display(self):
        """
        Devuelve una etiqueta legible del tipo específico según la categoría.
        Esto ayuda a vistas y templates.
        """
        if not self.case_type_specific:
            return ""

        mapping = {
            self.CaseCategory.PENAL: dict(self.PenalType.choices),
            self.CaseCategory.PUBLICO: dict(self.PublicoType.choices),
            self.CaseCategory.LABORAL: dict(self.LaboralType.choices),
            self.CaseCategory.CIVIL: dict(self.CivilType.choices),
            self.CaseCategory.FAMILIA: dict(self.FamiliaType.choices),
            self.CaseCategory.ADMINISTRATIVO: dict(self.AdministrativoType.choices),
        }

        category_choices = mapping.get(self.category, {})
        return category_choices.get(self.case_type_specific, self.case_type_specific)

    def save(self, *args, **kwargs):
        """
        Genera automáticamente el case_number si no existe.
        """
        if not self.case_number:
            from .services import CaseNumberGenerator
            self.case_number = CaseNumberGenerator.generate_case_number()
        
        super().save(*args, **kwargs)


class BitacoraEntry(models.Model):
    """
    Entradas de seguimiento del caso.
    Reemplaza la lógica vieja de Binnacle.
    """

    class EntryType(models.TextChoices):
        ACTUALIZACION = "ACT", "Actualización"
        ENTREVISTA = "ENT", "Entrevista"
        OBSERVACION = "OBS", "Observación"
        ASIGNACION = "ASI", "Asignación"
        DOCUMENTO = "DOC", "Documento"
        EVENTO = "EVE", "Evento"
        CASO_ASIGNADO_MANUALMENTE = "CAS_MAN", "Caso Asignado Manualmente"
        CASO_ENVIADO_REVISION = "CAS_REV", "Caso Enviado a Revisión"

    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name="bitacora_entries",
        verbose_name="Caso",
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bitacora_entries",
        verbose_name="Autor",
    )

    entry_type = models.CharField(
        max_length=10,
        choices=EntryType.choices,
        default=EntryType.ACTUALIZACION,
        verbose_name="Tipo de entrada",
    )

    content = models.TextField(
        verbose_name="Contenido",
    )

    scheduled_for = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha del evento",
    )

    notify = models.BooleanField(
        default=False,
        verbose_name="Notificar",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación",
    )

    class Meta:
        verbose_name = "Entrada de Bitácora"
        verbose_name_plural = "Entradas de Bitácora"
        ordering = ["-created_at"]

    def clean(self):
        if self.scheduled_for and self.scheduled_for < timezone.now():
            raise ValidationError("La fecha programada no puede estar en el pasado.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def author_initials(self):
        try:
            return self.author.initials
        except AttributeError:
            first = getattr(self.author, "first_name", "") or ""
            last = getattr(self.author, "last_name", "") or ""
            initials = f"{first[:1]}{last[:1]}".upper()
            return initials or "US"

    @property
    def author_role(self):
        try:
            return self.author.get_role_display()
        except AttributeError:
            return "Usuario"

    def __str__(self):
        return f"Bitácora {self.id} - Caso {self.case.case_number}"


class CaseDocument(models.Model):
    """
    Documentos requeridos para reparto/validación del caso.
    """

    class DocumentType(models.TextChoices):
        DOCUMENTO = "DOC", "Documento"
        RECIBO_SERVICIOS = "REC", "Recibo de Servicios"
        FOTO = "FOT", "Foto"

    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name="case_documents",
        verbose_name="Caso",
    )

    document_type = models.CharField(
        max_length=3,
        choices=DocumentType.choices,
        verbose_name="Tipo de Documento",
    )

    file = models.FileField(
        upload_to="case_documents/%Y/%m/%d/",
        verbose_name="Archivo",
    )

    original_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Nombre original",
    )

    is_valid = models.BooleanField(
        default=True,
        verbose_name="Válido",
    )

    file_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Tamaño del archivo",
    )

    content_type = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Tipo MIME",
    )

    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="case_documents_uploaded",
        verbose_name="Subido por",
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de subida",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización",
    )

    class Meta:
        verbose_name = "Documento de Caso"
        verbose_name_plural = "Documentos de Caso"
        ordering = ["-uploaded_at"]
        unique_together = [["case", "document_type"]]

    def __str__(self):
        return f"{self.get_document_type_display()} - Caso {self.case.case_number}"

    def save(self, *args, **kwargs):
        if self.file:
            if not self.original_name:
                self.original_name = self.file.name
            if not self.file_size:
                try:
                    self.file_size = self.file.size
                except Exception:
                    pass
            if not self.content_type:
                try:
                    self.content_type = self.file.file.content_type
                except Exception:
                    pass
        super().save(*args, **kwargs)

class CaseAssignment(models.Model):
    """
    Historial de asignaciones del caso.
    No reemplaza el assigned_student del caso; lo complementa para trazabilidad.
    """

    class AssignmentType(models.TextChoices):
        MANUAL = "MAN", "Manual"
        AUTOMATIC = "AUTO", "Automática"

    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name="assignments",
        verbose_name="Caso",
    )

    assigned_student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="student_assignments",
        verbose_name="Estudiante asignado",
    )

    assigned_advisor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="advisor_assignments",
        verbose_name="Asesor o asignador",
    )

    assignment_type = models.CharField(
        max_length=4,
        choices=AssignmentType.choices,
        default=AssignmentType.MANUAL,
        verbose_name="Tipo de asignación",
    )

    case_category = models.CharField(
        max_length=10,
        choices=Case.CaseCategory.choices,
        verbose_name="Categoría de caso",
    )

    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de asignación",
    )

    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notas",
    )

    class Meta:
        verbose_name = "Asignación de Caso"
        verbose_name_plural = "Asignaciones de Caso"
        ordering = ["-assigned_at"]

    def __str__(self):
        student_name = getattr(self.assigned_student, "full_name", str(self.assigned_student))
        return f"Caso {self.case.case_number} → {student_name}"


class CaseDeadline(models.Model):
    """
    Fechas límite asociadas a un caso.
    """
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name="deadlines",
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_deadlines",
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateTimeField()
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["due_date"]
        verbose_name = "Fecha límite"
        verbose_name_plural = "Fechas límite"

    def __str__(self):
        return f"{self.title} - {self.case.case_number}"

    @property
    def is_overdue(self):
        return not self.is_completed and self.due_date < timezone.now()

    @property
    def is_due_soon(self):
        if self.is_completed:
            return False
        delta = self.due_date - timezone.now()
        return 0 <= delta.days <= 2


class Notification(models.Model):
    """
    Notificaciones del sistema.
    """

    class NotificationType(models.TextChoices):
        INACTIVITY = "INA", "Inactividad"
        DEADLINE = "DEA", "Fecha límite"
        INFO = "INF", "Informativa"

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )
    deadline = models.ForeignKey(
        CaseDeadline,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )
    notification_type = models.CharField(
        max_length=3,
        choices=NotificationType.choices,
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"

    def __str__(self):
        return f"{self.title} - {self.recipient.full_name}"