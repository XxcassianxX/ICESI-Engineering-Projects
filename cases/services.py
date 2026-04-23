"""
Services para la funcionalidad de Reparto de Casos (HU3).

Este módulo contiene la lógica de negocio para la asignación manual y automática
de casos, validación de completitud y gestión de etapas.
"""

import logging

from django.db import transaction
from django.db.models import Count, Q

from accounts.models import User
from .models import BitacoraEntry, Case, CaseAssignment, CaseDocument

logger = logging.getLogger(__name__)


class CaseNumberGenerator:
    """
    Genera números de caso únicos con 5 dígitos numéricos.
    """

    @staticmethod
    def generate_case_number() -> str:
        last_case = Case.objects.filter(
            case_number__regex=r'^\d{5}$'
        ).order_by('-case_number').first()

        if last_case:
            last_number = int(last_case.case_number)
            next_number = last_number + 1
        else:
            next_number = 1

        if next_number > 99999:
            raise ValueError("Se ha alcanzado el número máximo de casos (99999)")

        return str(next_number).zfill(5)


class CaseCompletionValidator:
    """
    Valida si un caso está completo para proceder con la asignación.
    """

    REQUIRED_DOCUMENTS = [
        CaseDocument.DocumentType.DOCUMENTO,
        CaseDocument.DocumentType.RECIBO_SERVICIOS,
        CaseDocument.DocumentType.FOTO,
    ]

    @staticmethod
    def is_complete(case: Case) -> dict:
        result = {
            "is_complete": True,
            "missing_documents": [],
            "invalid_documents": [],
            "details": [],
        }

        if not case.title or not case.title.strip():
            result["is_complete"] = False
            result["details"].append("El caso no tiene título.")

        if not case.description or not case.description.strip():
            result["is_complete"] = False
            result["details"].append("El caso no tiene descripción.")

        if not case.beneficiary:
            result["is_complete"] = False
            result["details"].append("El caso no tiene beneficiario asignado.")

        case_documents = case.case_documents.all()
        documents_dict = {doc.document_type: doc for doc in case_documents}

        for doc_type in CaseCompletionValidator.REQUIRED_DOCUMENTS:
            doc_label = CaseDocument.DocumentType(doc_type).label

            if doc_type not in documents_dict:
                result["is_complete"] = False
                result["missing_documents"].append(doc_label)
                result["details"].append(f"Falta documento: {doc_label}")
            else:
                doc = documents_dict[doc_type]
                if not doc.is_valid:
                    result["is_complete"] = False
                    result["invalid_documents"].append(doc_label)
                    result["details"].append(f"Documento inválido: {doc_label}")

        return result

    @staticmethod
    def get_document_status(case: Case) -> dict:
        status = {
            "DOCUMENTO": {"exists": False, "valid": False},
            "RECIBO_SERVICIOS": {"exists": False, "valid": False},
            "FOTO": {"exists": False, "valid": False},
        }

        case_documents = case.case_documents.all()

        for doc in case_documents:
            if doc.document_type == CaseDocument.DocumentType.DOCUMENTO:
                key = "DOCUMENTO"
            elif doc.document_type == CaseDocument.DocumentType.RECIBO_SERVICIOS:
                key = "RECIBO_SERVICIOS"
            elif doc.document_type == CaseDocument.DocumentType.FOTO:
                key = "FOTO"
            else:
                continue

            status[key] = {
                "exists": True,
                "valid": doc.is_valid,
            }

        return status


class CaseDistributionService:
    """
    Servicio para gestionar el reparto (asignación) manual de casos.
    """

    @staticmethod
    def can_assign_case(case: Case, user: User) -> tuple[bool, str]:
        if user.role not in [User.Role.SECRETARIA, User.Role.ASESOR]:
            return False, "Solo Secretaría y Asesores pueden asignar casos."

        if case.status != Case.CaseStatus.SIN_ASIGNAR:
            current_status = case.get_status_display()
            return False, f"El caso debe estar sin asignar, actualmente está '{current_status}'."

        if case.assigned_student:
            return False, "El caso ya tiene un estudiante asignado."

        return True, ""

    @staticmethod
    @transaction.atomic
    def assign_case_manually(
            case: Case,
            student: User,
            category: str,
            case_type: str,
            assigned_by: User,
            notes: str = "",
    ) -> tuple[bool, str, CaseAssignment | None]:
        if student.role != User.Role.ESTUDIANTE:
            return False, "El usuario seleccionado no es un estudiante.", None

        if not student.is_active:
            return False, "El estudiante seleccionado no está activo.", None

        can_assign, reason = CaseDistributionService.can_assign_case(case, assigned_by)
        if not can_assign:
            return False, reason, None

        try:
            assignment = CaseAssignment.objects.create(
                case=case,
                assigned_student=student,
                assigned_advisor=assigned_by,
                assignment_type=CaseAssignment.AssignmentType.MANUAL,
                case_category=category,
                notes=notes,
            )

            case.assigned_student = student
            case.status = Case.CaseStatus.ASIGNADO
            case.category = category
            case.case_type_specific = case_type
            # Al asignar: etapa 1 se completa, ponemos etapa 2 como la activa
            case.current_stage = Case.CaseStage.INFORMATION_GATHERING

            if category in dict(Case.CaseType.choices):
                case.case_type = category
            else:
                case.case_type = Case.CaseType.OTRO

            case.save(
                update_fields=[
                    "assigned_student",
                    "status",
                    "category",
                    "case_type_specific",
                    "case_type",
                    "current_stage",
                    "updated_at",
                ]
            )

            bitacora_content = (
                f"Caso asignado manualmente a {student.full_name} "
                f"por {assigned_by.full_name}."
            )
            if notes:
                bitacora_content += f" Notas: {notes}"

            BitacoraEntry.objects.create(
                case=case,
                author=assigned_by,
                entry_type=BitacoraEntry.EntryType.CASO_ASIGNADO_MANUALMENTE,
                content=bitacora_content,
            )

            return True, "Caso asignado exitosamente.", assignment

        except Exception as e:
            logger.exception("Error al asignar caso manualmente.")
            return False, f"Error al asignar el caso: {str(e)}", None

    @staticmethod
    @transaction.atomic
    def send_to_review(
            case: Case,
            sent_by: User,
            reason: str = "",
    ) -> tuple[bool, str]:
        if sent_by.role not in [User.Role.SECRETARIA, User.Role.ASESOR]:
            return False, "Solo Secretaría y Asesores pueden enviar a revisión."

        if case.status != Case.CaseStatus.SIN_ASIGNAR:
            current_status = case.get_status_display()
            return False, f"El caso debe estar sin asignar, actualmente está '{current_status}'."

        try:
            case.status = Case.CaseStatus.DOCUMENTACION
            case.current_stage = Case.CaseStage.UNASSIGNED
            case.save(update_fields=["status", "current_stage", "updated_at"])

            bitacora_content = f"Caso enviado a revisión por {sent_by.full_name}."
            if reason:
                bitacora_content += f" Motivo: {reason}"

            BitacoraEntry.objects.create(
                case=case,
                author=sent_by,
                entry_type=BitacoraEntry.EntryType.CASO_ENVIADO_REVISION,
                content=bitacora_content,
            )

            return True, "Caso enviado a revisión exitosamente."

        except Exception as e:
            logger.exception("Error al enviar caso a revisión.")
            return False, f"Error al enviar el caso a revisión: {str(e)}"


class CaseDocumentService:
    """
    Servicio para gestionar documentos de los casos.
    """

    @staticmethod
    def get_required_documents_for_display(case: Case) -> dict:
        documents = {}
        status = CaseCompletionValidator.get_document_status(case)

        for doc_type in CaseCompletionValidator.REQUIRED_DOCUMENTS:
            if doc_type == CaseDocument.DocumentType.DOCUMENTO:
                doc_type_key = "DOCUMENTO"
            elif doc_type == CaseDocument.DocumentType.RECIBO_SERVICIOS:
                doc_type_key = "RECIBO_SERVICIOS"
            else:
                doc_type_key = "FOTO"

            doc_status = status.get(doc_type_key, {"exists": False, "valid": False})

            documents[doc_type_key] = {
                "exists": doc_status["exists"],
                "valid": doc_status["valid"],
            }

        return documents


class CaseStageManager:
    """
    Gestiona el flujo de etapas del caso.

    Lógica de etapas:
      current_stage indica cuál etapa está EN PROGRESO.
      Toda etapa con número < current_stage aparece como COMPLETADA.
      Toda etapa con número > current_stage aparece como PENDIENTE.

    Mapeo estado → current_stage:
      SIN_ASIGNAR / DOCUMENTACION → 0  (ninguna etapa activa)
      ASIGNADO                    → 2  (etapa 1 completada, etapa 2 en progreso)
      EN_PROCESO                  → 3  (etapas 1-2 completadas, etapa 3 en progreso)
      ESPERANDO_USUARIO           → 3  (igual que EN_PROCESO)
      EN_REVISION                 → 4  (etapas 1-3 completadas, etapa 4 en progreso)
      CERRADO                     → 6  (todas completadas, 6 > max etapa 5)
    """

    @staticmethod
    def advance_to_stage_1(case: Case) -> None:
        """
        Avanza el caso a Etapa 2 (Recopilación), dejando la etapa 1 como completada.
        Se llama justo después de asignar un estudiante.
        """
        if case.current_stage < Case.CaseStage.INFORMATION_GATHERING:
            case.current_stage = Case.CaseStage.INFORMATION_GATHERING
            case.save(update_fields=["current_stage", "updated_at"])

    @staticmethod
    def calculate_current_stage(case: Case) -> int:
        """
        Calcula y devuelve el número de etapa activa según el estado del caso.
        """
        if case.status in [Case.CaseStatus.SIN_ASIGNAR, Case.CaseStatus.DOCUMENTACION]:
            return Case.CaseStage.UNASSIGNED                # 0 — ninguna activa

        if case.status == Case.CaseStatus.ASIGNADO:
            return Case.CaseStage.INFORMATION_GATHERING     # 2 — etapa 1 ✓, etapa 2 en progreso

        if case.status == Case.CaseStatus.EN_PROCESO:
            return Case.CaseStage.ANALYSIS_DRAFTING         # 3 — etapas 1-2 ✓, etapa 3 en progreso

        if case.status == Case.CaseStatus.ESPERANDO_USUARIO:
            return Case.CaseStage.ANALYSIS_DRAFTING         # 3 — igual que EN_PROCESO

        if case.status == Case.CaseStatus.EN_REVISION:
            return Case.CaseStage.SUPERVISOR_REVIEW         # 4 — etapas 1-3 ✓, etapa 4 en progreso

        if case.status == Case.CaseStatus.CERRADO:
            return 6                                        # 6 > 5 — todas ✓ completadas

        return Case.CaseStage.UNASSIGNED                    # 0 — default

    @staticmethod
    def get_stage_display_info(case: Case) -> list:
        """
        Genera la lista de etapas con flags: active, completed, pending.
        Usado por el template case_detail.html.
        """
        current_stage = CaseStageManager.calculate_current_stage(case)
        is_closed = case.status == Case.CaseStatus.CERRADO

        stages = [
            {
                "number": Case.CaseStage.ASSIGNMENT,
                "title": Case.CaseStage.ASSIGNMENT.label,
                "active": current_stage == Case.CaseStage.ASSIGNMENT,
                "completed": is_closed or current_stage > Case.CaseStage.ASSIGNMENT,
            },
            {
                "number": Case.CaseStage.INFORMATION_GATHERING,
                "title": Case.CaseStage.INFORMATION_GATHERING.label,
                "active": current_stage == Case.CaseStage.INFORMATION_GATHERING,
                "completed": is_closed or current_stage > Case.CaseStage.INFORMATION_GATHERING,
            },
            {
                "number": Case.CaseStage.ANALYSIS_DRAFTING,
                "title": Case.CaseStage.ANALYSIS_DRAFTING.label,
                "active": current_stage == Case.CaseStage.ANALYSIS_DRAFTING,
                "completed": is_closed or current_stage > Case.CaseStage.ANALYSIS_DRAFTING,
            },
            {
                "number": Case.CaseStage.SUPERVISOR_REVIEW,
                "title": Case.CaseStage.SUPERVISOR_REVIEW.label,
                "active": current_stage == Case.CaseStage.SUPERVISOR_REVIEW,
                "completed": is_closed or current_stage > Case.CaseStage.SUPERVISOR_REVIEW,
            },
            {
                "number": Case.CaseStage.COURT_PRESENTATION,
                "title": Case.CaseStage.COURT_PRESENTATION.label,
                "active": current_stage == Case.CaseStage.COURT_PRESENTATION,
                "completed": is_closed or current_stage > Case.CaseStage.COURT_PRESENTATION,
            },
        ]

        return stages


def asignar_caso_automatico(caso_id: str, usuario_ejecutor: User) -> tuple[bool, str]:
    """
    Asigna un caso al estudiante con menor carga de trabajo.
    Solo debe ser ejecutado por usuarios con rol de Secretaría.
    """
    if usuario_ejecutor.role != User.Role.SECRETARIA:
        return False, "Error: Solo Secretaría puede ejecutar el reparto."

    try:
        caso = Case.objects.get(id=caso_id, status=Case.CaseStatus.SIN_ASIGNAR)
    except Case.DoesNotExist:
        return False, "El caso no existe o ya fue asignado."

    estudiantes_disponibles = (
        User.objects.filter(
            role=User.Role.ESTUDIANTE,
            is_active=True,
        )
        .annotate(
            num_casos=Count(
                "assigned_cases",
                filter=Q(assigned_cases__status=Case.CaseStatus.ASIGNADO),
            )
        )
        .filter(num_casos__lt=5)
        .order_by("num_casos", "first_name", "last_name")
    )

    estudiante_elegido = estudiantes_disponibles.first()

    if not estudiante_elegido:
        logger.warning("No hay estudiantes disponibles o todos llegaron al límite de 5 casos.")
        return False, "No hay estudiantes con cupo disponible en este momento."

    try:
        with transaction.atomic():
            CaseAssignment.objects.create(
                case=caso,
                assigned_student=estudiante_elegido,
                assigned_advisor=usuario_ejecutor,
                assignment_type=CaseAssignment.AssignmentType.AUTOMATIC,
                case_category=caso.case_type,
                notes="Asignación automática",
            )

            caso.assigned_student = estudiante_elegido
            caso.status = Case.CaseStatus.ASIGNADO
            # Etapa 1 completada, etapa 2 en progreso
            caso.current_stage = Case.CaseStage.INFORMATION_GATHERING
            caso.save(update_fields=["assigned_student", "status", "current_stage", "updated_at"])

            BitacoraEntry.objects.create(
                case=caso,
                author=usuario_ejecutor,
                entry_type=BitacoraEntry.EntryType.ASIGNACION,
                content=f"El sistema asignó automáticamente el caso a {estudiante_elegido.full_name}.",
            )

            logger.info(
                "Caso %s asignado automáticamente a %s",
                caso.id,
                estudiante_elegido.full_name,
            )
            return True, f"Caso asignado exitosamente a {estudiante_elegido.full_name}."

    except Exception as e:
        logger.exception("Error al asignar caso automáticamente.")
        return False, f"Error al asignar el caso: {str(e)}"


class CaseAutomaticDistributionService:
    """
    Servicio para distribuir automáticamente múltiples casos completos
    entre estudiantes de forma equitativa.
    """

    @staticmethod
    @transaction.atomic
    def ejecutar_reparto_automatico_masivo(
            executed_by: User,
    ) -> tuple[bool, str]:
        if executed_by.role not in [User.Role.SECRETARIA, User.Role.ASESOR]:
            return False, "Solo Secretaría y Asesores pueden ejecutar el reparto automático."

        casos_sin_asignar = Case.objects.filter(
            status=Case.CaseStatus.SIN_ASIGNAR
        ).select_related("beneficiary")

        casos_completos = []
        for caso in casos_sin_asignar:
            completion_check = CaseCompletionValidator.is_complete(caso)
            if completion_check["is_complete"]:
                casos_completos.append(caso)

        if not casos_completos:
            return False, "No hay casos completos sin asignar para distribuir."

        estudiantes = (
            User.objects.filter(
                role=User.Role.ESTUDIANTE,
                is_active=True,
            )
            .annotate(
                num_casos=Count(
                    "assigned_cases",
                    filter=Q(assigned_cases__status=Case.CaseStatus.ASIGNADO),
                )
            )
            .order_by("num_casos", "first_name", "last_name")
        )

        if not estudiantes.exists():
            return False, "No hay estudiantes disponibles en el sistema."

        asignaciones_exitosas = 0
        errores = []

        for idx, caso in enumerate(casos_completos):
            estudiante_idx = idx % len(estudiantes)
            estudiante = estudiantes[estudiante_idx]

            try:
                CaseAssignment.objects.create(
                    case=caso,
                    assigned_student=estudiante,
                    assigned_advisor=executed_by,
                    assignment_type=CaseAssignment.AssignmentType.AUTOMATIC,
                    case_category=caso.category or caso.case_type,
                    notes="Distribución automática equitativa",
                )

                caso.assigned_student = estudiante
                caso.status = Case.CaseStatus.ASIGNADO
                # Etapa 1 completada, etapa 2 en progreso
                caso.current_stage = Case.CaseStage.INFORMATION_GATHERING
                caso.save(
                    update_fields=[
                        "assigned_student",
                        "status",
                        "current_stage",
                        "updated_at",
                    ]
                )

                BitacoraEntry.objects.create(
                    case=caso,
                    author=executed_by,
                    entry_type=BitacoraEntry.EntryType.ASIGNACION,
                    content=f"Caso distribuido automáticamente a {estudiante.full_name}.",
                )

                asignaciones_exitosas += 1

            except Exception as e:
                logger.exception(f"Error al asignar caso {caso.id}")
                errores.append(f"Error en caso {caso.case_number}: {str(e)}")

        mensaje = f"Se distribuyeron exitosamente {asignaciones_exitosas} de {len(casos_completos)} casos."
        if errores:
            mensaje += f" Con {len(errores)} error(es)."
            logger.warning(f"Errores en reparto automático: {errores}")

        return True, mensaje