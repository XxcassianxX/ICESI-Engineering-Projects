import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from cases.models import Case
from .models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView

from cases.models import Case
from .models import User
from cases.models import Notification, CaseDeadline
from .services import get_notifications_for_user, run_deadline_check, run_inactivity_check


def get_type_label(type_value):
    """Convierte el valor corto del tipo a su etiqueta completa."""
    if not type_value:
        return "Sin tipo"

    type_map = {
        # Tipos Penales
        "DER_FIS": "Derecho fiscal",
        "DER_DIS": "Derecho disciplinario",
        "PEN": "Penal",
        # Tipos Público
        "MIG": "Migrantes",
        "DER_ADM": "Derecho Administrativo y constitucional",
        # Tipos Laboral
        "TUT": "Tutelas",
        "LIQ": "Liquidaciones",
        "PROC": "Procesos",
        # Tipos Civil / Familia
        "CON": "Conceptos",
        # Tipos Administrativo
        "ASI": "Asignados",
    }

    return type_map.get(type_value, type_value)


def get_topbar_user_data(user):
    return {
        "full_name": user.full_name,
        "role_name": user.get_role_display(),
        "initials": user.initials,
    }


class SplashView(TemplateView):
    template_name = "accounts/splash.html"


class RoleSelectionView(TemplateView):
    template_name = "accounts/role_selection.html"


class RoleLoginView(View):
    template_name = "accounts/login.html"

    ROLE_CONFIG = {
        "beneficiario": {
            "display_name": "Beneficiario/Usuario",
            "user_label": "Número de cédula",
            "user_placeholder": "Ingresa tu número de cédula",
            "icon": "beneficiario",
            "expected_role": User.Role.BENEFICIARIO,
        },
        "secretaria": {
            "display_name": "Secretaría",
            "user_label": "Número de documento",
            "user_placeholder": "Ingresa tu número de documento",
            "icon": "secretaria",
            "expected_role": User.Role.SECRETARIA,
        },
        "estudiante": {
            "display_name": "Estudiante",
            "user_label": "Número de documento",
            "user_placeholder": "Ingresa tu número de documento",
            "icon": "estudiante",
            "expected_role": User.Role.ESTUDIANTE,
        },
        "asesor": {
            "display_name": "Asesor",
            "user_label": "Número de documento",
            "user_placeholder": "Ingresa tu número de documento",
            "icon": "asesor",
            "expected_role": User.Role.ASESOR,
        },
    }

    def get_role_data(self):
        role = self.kwargs.get("role")
        return role, self.ROLE_CONFIG.get(role)

    def build_context(self):
        role, role_data = self.get_role_data()
        return {
            "role_key": role,
            "role_data": role_data,
        }

    def get(self, request, *args, **kwargs):
        role, role_data = self.get_role_data()
        if not role_data:
            messages.error(request, "Rol no válido.")
            return redirect("role_selection")
        return render(request, self.template_name, self.build_context())

    def post(self, request, *args, **kwargs):
        role, role_data = self.get_role_data()

        if not role_data:
            messages.error(request, "Rol no válido.")
            return redirect("role_selection")

        document_number = request.POST.get("document_number", "").strip()
        password = request.POST.get("password", "").strip()

        if not document_number or not password:
            messages.error(request, "Debes completar todos los campos.")
            return render(request, self.template_name, self.build_context())

        user = authenticate(
            request,
            document_number=document_number,
            password=password,
        )

        if user is None:
            messages.error(request, "Documento o contraseña incorrectos.")
            return render(request, self.template_name, self.build_context())

        if user.role != role_data["expected_role"]:
            messages.error(request, "Este usuario no corresponde al rol seleccionado.")
            return render(request, self.template_name, self.build_context())

        login(request, user)
        return redirect("dashboard_redirect")


@method_decorator(login_required, name="dispatch")
class DashboardRedirectView(View):
    def get(self, request, *args, **kwargs):
        if request.user.role == User.Role.BENEFICIARIO:
            return redirect("beneficiary_dashboard")
        if request.user.role == User.Role.SECRETARIA:
            return redirect("secretary_dashboard")
        if request.user.role == User.Role.ESTUDIANTE:
            return redirect("student_dashboard")
        if request.user.role == User.Role.ASESOR:
            return redirect("advisor_dashboard")
        return redirect("splash")


@method_decorator(login_required, name="dispatch")
class BeneficiaryDashboardView(TemplateView):
    template_name = "accounts/beneficiary_dashboard.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != User.Role.BENEFICIARIO:
            return redirect("dashboard_redirect")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Mantengo la estructura demo original para no romper la UI existente
        context["beneficiary_data"] = {
            "full_name": "María González Pérez",
            "role_name": "Beneficiario/Usuario",
            "initials": "MG",
            "case_id": "12345",
            "process_stage": "En revisión de documentos",
            "assigned_student_name": "Carlos Ramírez",
            "assigned_student_program": "Estudiante de Derecho",
            "next_appointment": "28 de Febrero, 2026 - 2:00 PM",
            "start_date": "15 de Enero, 2026",
            "last_appointment_status": "No asistió",
            "last_appointment_date": "10 de Febrero, 2026",
            "next_appointment_title": "Revisión de caso",
            "assistant_url": "https://elevenlabs.io/app/talk-to?agent_id=agent_7401kc1tzgwae23r1jx4vwg53hrt&branch_id=agtbrch_4001kc9xrcq7e2wb914gezsma87x",
        }

        context["user_data"] = get_topbar_user_data(self.request.user)
        return context


@method_decorator(login_required, name="dispatch")
class BeneficiaryAppointmentsView(TemplateView):
    template_name = "accounts/beneficiary_appointments.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != User.Role.BENEFICIARIO:
            return redirect("dashboard_redirect")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["beneficiary_data"] = {
            "full_name": "María González Pérez",
            "role_name": "Beneficiario/Usuario",
            "initials": "MG",
        }

        context["upcoming_appointments"] = [
            {
                "title": "Revisión de caso",
                "date": "28 de Febrero, 2026 - 2:00 PM",
                "with_person": "Carlos Ramírez",
                "status": "Pendiente",
            },
            {
                "title": "Preparación audiencia",
                "date": "15 de Marzo, 2026 - 10:00 AM",
                "with_person": "Carlos Ramírez",
                "status": "Pendiente",
            },
        ]

        context["past_appointments"] = [
            {
                "title": "Entrega documentos (Reprogramada)",
                "date": "20 de Febrero, 2026 - 3:00 PM",
                "with_person": "Carlos Ramírez",
                "notes": "Cliente entregó documentos faltantes. Todo en orden.",
                "status": "Asistió",
                "status_type": "success",
            },
            {
                "title": "Entrega documentos",
                "date": "10 de Febrero, 2026 - 11:00 AM",
                "with_person": "Carlos Ramírez",
                "notes": "Cliente no asistió. Se contactó vía telefónica para reprogramar.",
                "status": "No asistió",
                "status_type": "danger",
            },
            {
                "title": "Seguimiento",
                "date": "28 de Enero, 2026 - 2:00 PM",
                "with_person": "Carlos Ramírez",
                "notes": "Cliente entregó documentación solicitada. Se revisó avance del caso.",
                "status": "Asistió",
                "status_type": "success",
            },
            {
                "title": "Consulta inicial",
                "date": "15 de Enero, 2026 - 10:00 AM",
                "with_person": "Carlos Ramírez",
                "notes": "Primera consulta. Se explicó el proceso completo y se solicitó documentación inicial.",
                "status": "Asistió",
                "status_type": "success",
            },
        ]

        context["user_data"] = get_topbar_user_data(self.request.user)
        return context


@method_decorator(login_required, name="dispatch")
class SecretaryDashboardView(TemplateView):
    template_name = "accounts/secretary_dashboard.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != User.Role.SECRETARIA:
            return redirect("dashboard_redirect")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cases = Case.objects.select_related(
            "beneficiary",
            "assigned_student"
        ).all().order_by("-updated_at")

        context["user_data"] = get_topbar_user_data(self.request.user)
        context["total_cases"] = cases.count()
        context["unassigned_cases"] = cases.filter(assigned_student__isnull=True).count()
        context["assigned_cases"] = cases.filter(
            status__in=[
                Case.CaseStatus.ASIGNADO,
                Case.CaseStatus.EN_PROCESO,
                Case.CaseStatus.ESPERANDO_USUARIO,
                Case.CaseStatus.EN_REVISION,
            ]
        ).count()
        
        # Contar casos cerrados por tipo
        closed_cases_total = cases.filter(status=Case.CaseStatus.CERRADO).count()
        closed_favorable = cases.filter(
            status=Case.CaseStatus.CERRADO,
            closure_type=Case.ClosureType.FAVORABLE
        ).count()
        closed_negative = cases.filter(
            status=Case.CaseStatus.CERRADO,
            closure_type=Case.ClosureType.NEGATIVE
        ).count()
        closed_dismissed = cases.filter(
            status=Case.CaseStatus.CERRADO,
            closure_type=Case.ClosureType.DISMISSED
        ).count()
        
        context["closed_cases"] = closed_cases_total
        context["closed_favorable"] = closed_favorable
        context["closed_negative"] = closed_negative
        context["closed_dismissed"] = closed_dismissed
        context["recent_cases"] = cases

        assigned_cases = Case.objects.filter(
            status__in=[
                Case.CaseStatus.ASIGNADO,
                Case.CaseStatus.EN_PROCESO,
                Case.CaseStatus.ESPERANDO_USUARIO,
                Case.CaseStatus.EN_REVISION,
            ]
        ).select_related("beneficiary", "assigned_student")

        all_types_by_category = {
            "PEN": {
                "DER_FIS": "Derecho fiscal",
                "DER_DIS": "Derecho disciplinario",
                "PEN": "Penal",
            },
            "PUB": {
                "MIG": "Migrantes",
                "DER_ADM": "Derecho Administrativo y constitucional",
            },
            "LAB": {
                "TUT": "Tutelas",
                "LIQ": "Liquidaciones",
                "PROC": "Procesos",
            },
            "CIV": {
                "CON": "Conceptos",
                "PROC": "Procesos",
            },
            "FAM": {
                "CON": "Conceptos",
                "PROC": "Procesos",
            },
            "ADM": {
                "ASI": "Asignados",
            },
        }

        cases_count = {}
        total_by_category = {}

        for case in assigned_cases:
            category = case.category if case.category else None
            case_type = case.case_type_specific if case.case_type_specific else None

            if category:
                total_by_category[category] = total_by_category.get(category, 0) + 1
                key = (category, case_type)
                cases_count[key] = cases_count.get(key, 0) + 1

        categories_list = []
        for cat_code, cat_label in Case.CaseCategory.choices:
            if cat_code in all_types_by_category:
                types_data = []
                for type_code, type_label in all_types_by_category[cat_code].items():
                    count = cases_count.get((cat_code, type_code), 0)
                    types_data.append({
                        "code": type_code,
                        "label": type_label,
                        "count": count,
                    })

                category_total = total_by_category.get(cat_code, 0)
                categories_list.append({
                    "key": cat_code,
                    "label": cat_label,
                    "count": category_total,
                    "types": sorted(types_data, key=lambda x: x["label"]),
                })

        # NO hacer json.dumps() - dejar que json_script lo maneje
        context["categories_json"] = categories_list

        return context


@method_decorator(login_required, name="dispatch")
class StudentDashboardView(TemplateView):
    template_name = "accounts/student_dashboard.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != User.Role.ESTUDIANTE:
            return redirect("dashboard_redirect")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        case_obj = (
            Case.objects.select_related("beneficiary", "advisor")
            .filter(assigned_student=self.request.user)
            .order_by("-updated_at")
            .first()
        )

        assigned_cases_count = Case.objects.filter(
            assigned_student=self.request.user
        ).count()

        context["user_data"] = get_topbar_user_data(self.request.user)
        context["assigned_case"] = case_obj
        context["assigned_cases_count"] = assigned_cases_count
        context["alerts"] = [
            {
                "title": "Audiencia",
                "text": "Audiencia de divorcio y custodia - Juzgado Familia",
                "date": "24 de febrero de 2026",
                "type": "danger",
            },
            {
                "title": "Entrega Documentos",
                "text": "Presentar documentación complementaria al juzgado",
                "date": "1 de marzo de 2026",
                "type": "warning",
            },
            {
                "title": "Vencimiento",
                "text": "Fecha límite para responder solicitud de información",
                "date": "8 de marzo de 2026",
                "type": "success",
            },
            {
                "title": "Cita Cliente",
                "text": "Reunión seguimiento con beneficiaria",
                "date": "13 de marzo de 2026",
                "type": "success",
            },
        ]
        context["latest_notes"] = [
            "Cliente aportó certificado de matrimonio y actas de nacimiento de los hijos.",
            "Primera entrevista realizada. Cliente solicita custodia compartida.",
        ]
        return context


@method_decorator(login_required, name="dispatch")
class AdvisorDashboardView(TemplateView):
    template_name = "accounts/advisor_dashboard.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != User.Role.ASESOR:
            return redirect("dashboard_redirect")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        supervised_cases = Case.objects.filter(advisor=self.request.user).count()

        context["user_data"] = get_topbar_user_data(self.request.user)
        context["supervised_cases"] = supervised_cases
        context["students_count"] = User.objects.filter(role=User.Role.ESTUDIANTE).count()
        context["cases_on_time"] = max(supervised_cases - 3, 0)
        context["delayed_cases"] = 3
        context["alerts"] = [
            {
                "case_number": "12343",
                "beneficiary": "Juan Pérez",
                "text": "No ha actualizado la bitácora en 5 días",
                "badge": "Retraso",
            },
            {
                "case_number": "12338",
                "beneficiary": "Ana Torres",
                "text": "Tarea vencida desde el 20/02/2026",
                "badge": "Fecha vencida",
            },
        ]
        return context


@method_decorator(login_required, name="dispatch")
class NotificationsCenterView(TemplateView):
    template_name = "accounts/notifications_center.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        run_inactivity_check()
        run_deadline_check()

        all_notifications = Notification.objects.filter(
            recipient=self.request.user,
            is_resolved=False
        ).select_related("case", "deadline").order_by("-created_at")

        inactivity_notifications = all_notifications.filter(
            notification_type=Notification.NotificationType.INACTIVITY
        )

        alert_notifications = all_notifications.filter(
            notification_type__in=[
                Notification.NotificationType.DEADLINE,
                Notification.NotificationType.INFO,
            ]
        )

        context["user_data"] = get_topbar_user_data(self.request.user)
        context["all_notifications"] = all_notifications
        context["inactivity_notifications"] = inactivity_notifications
        context["alert_notifications"] = alert_notifications
        context["total_notifications"] = all_notifications.count()
        context["total_inactivity"] = inactivity_notifications.count()
        context["total_alerts"] = alert_notifications.count()

        return context

class LogoutView(View):
    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect("splash")
    

def get_topbar_user_data(user):
    return {
        "full_name": user.full_name,
        "role_name": user.get_role_display(),
        "initials": user.initials,
    }