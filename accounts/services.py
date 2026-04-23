from datetime import timedelta
from django.utils import timezone

from cases.models import Case
from cases.models import Notification, CaseDeadline


INACTIVITY_DAYS = 7


# =========================================================
# INACTIVIDAD
# =========================================================

def get_last_case_activity(case_obj):
    last_entry = case_obj.bitacora_entries.order_by("-created_at").first()

    if last_entry:
        return last_entry.created_at

    return case_obj.updated_at


def build_inactivity_message(case_obj, last_activity):
    days_inactive = (timezone.now() - last_activity).days

    return {
        "title": "Caso sin actividad reciente",
        "message": (
            f"El caso {case_obj.case_number} lleva {days_inactive} días sin actividad registrada."
        ),
    }


def create_notification_if_needed(recipient, case_obj, title, message):
    already_exists = Notification.objects.filter(
        recipient=recipient,
        case=case_obj,
        notification_type=Notification.NotificationType.INACTIVITY,
        is_resolved=False,
    ).exists()

    if not already_exists:
        Notification.objects.create(
            recipient=recipient,
            case=case_obj,
            notification_type=Notification.NotificationType.INACTIVITY,
            title=title,
            message=message,
        )


def resolve_inactivity_notifications(case_obj):
    Notification.objects.filter(
        case=case_obj,
        notification_type=Notification.NotificationType.INACTIVITY,
        is_resolved=False,
    ).update(is_resolved=True)


def check_case_inactivity(case_obj):
    last_activity = get_last_case_activity(case_obj)
    limit_date = timezone.now() - timedelta(days=INACTIVITY_DAYS)

    if last_activity <= limit_date:
        data = build_inactivity_message(case_obj, last_activity)

        recipients = [
            getattr(case_obj, "assigned_student", None),
            getattr(case_obj, "advisor", None),
            getattr(case_obj, "secretary", None),
        ]

        recipients = list(filter(None, set(recipients)))  # 🔥 evita duplicados

        for recipient in recipients:
            create_notification_if_needed(
                recipient=recipient,
                case_obj=case_obj,
                title=data["title"],
                message=data["message"],
            )
    else:
        resolve_inactivity_notifications(case_obj)


def run_inactivity_check():
    cases = Case.objects.all().prefetch_related("bitacora_entries")
    for case_obj in cases:
        check_case_inactivity(case_obj)


# =========================================================
# FECHAS LÍMITE
# =========================================================

def build_deadline_message(deadline, days_remaining):
    formatted_date = deadline.due_date.strftime("%d/%m/%Y %I:%M %p")

    if days_remaining < 0:
        return {
            "title": "Fecha límite vencida",
            "message": (
                f"El caso {deadline.case.case_number} tenía como fecha límite '{deadline.title}' "
                f"el {formatted_date} y ya venció hace {abs(days_remaining)} día(s)."
            ),
        }

    if days_remaining == 0:
        return {
            "title": "Fecha límite hoy",
            "message": (
                f"El caso {deadline.case.case_number} tiene la fecha límite '{deadline.title}' "
                f"para hoy ({formatted_date})."
            ),
        }

    if days_remaining == 1:
        return {
            "title": "Fecha límite mañana",
            "message": (
                f"El caso {deadline.case.case_number} tiene la fecha límite '{deadline.title}' "
                f"para mañana ({formatted_date})."
            ),
        }

    return {
        "title": "Fecha límite próxima",
        "message": (
            f"El caso {deadline.case.case_number} tiene la fecha límite '{deadline.title}' "
            f"el {formatted_date}, es decir, en {days_remaining} días."
        ),
    }


def create_deadline_notification_if_needed(recipient, deadline, title, message):
    already_exists = Notification.objects.filter(
        recipient=recipient,
        case=deadline.case,
        deadline=deadline,
        notification_type=Notification.NotificationType.DEADLINE,
        title=title,
        is_resolved=False,
    ).exists()

    if not already_exists:
        Notification.objects.create(
            recipient=recipient,
            case=deadline.case,
            deadline=deadline,
            notification_type=Notification.NotificationType.DEADLINE,
            title=title,
            message=message,
        )


def resolve_deadline_notifications(deadline):
    Notification.objects.filter(
        deadline=deadline,
        notification_type=Notification.NotificationType.DEADLINE,
        is_resolved=False,
    ).update(is_resolved=True)


def check_single_deadline(deadline):
    if deadline.is_completed:
        resolve_deadline_notifications(deadline)
        return

    now = timezone.now()
    days_remaining = (deadline.due_date.date() - now.date()).days

    if days_remaining <= 3:
        data = build_deadline_message(deadline, days_remaining)

        Notification.objects.filter(
            deadline=deadline,
            notification_type=Notification.NotificationType.DEADLINE,
            is_resolved=False,
        ).exclude(title=data["title"]).update(is_resolved=True)

        recipients = [
            getattr(deadline.case, "assigned_student", None),
            getattr(deadline.case, "advisor", None),
            getattr(deadline.case, "secretary", None),
        ]

        recipients = list(filter(None, set(recipients)))  # 🔥 evita duplicados

        for recipient in recipients:
            create_deadline_notification_if_needed(
                recipient=recipient,
                deadline=deadline,
                title=data["title"],
                message=data["message"],
            )
    else:
        resolve_deadline_notifications(deadline)


def run_deadline_check():
    deadlines = CaseDeadline.objects.filter(is_completed=False).select_related("case")
    for deadline in deadlines:
        check_single_deadline(deadline)


# =========================================================
# CONSULTA
# =========================================================

def get_notifications_for_user(user, notification_type=None):
    queryset = Notification.objects.filter(
        recipient=user,
        is_resolved=False,
    ).select_related("case", "deadline").order_by("-created_at")

    if notification_type and notification_type != "ALL":
        queryset = queryset.filter(notification_type=notification_type)

    return queryset