from django.urls import path

from .views import (
    AssignedCaseDetailView,
    AssignedCasesAPIView,
    AssignedCasesCategoriesView,
    AssignedCasesFilteredView,
    CaseBitacoraView,
    CaseClosureAPIView,
    CaseDetailView,
    CaseDistributionListView,
    CaseDistributionView,
    CaseReportView,
    CaseSearchAPIView,
    CaseSearchByIdAPIView,
    CaseSearchUnassignedByIdAPIView,
    CaseStatusChangeAPIView,
    PendingCasesView,
    ReassignCaseView,
    SecretaryCasesView,
    calendario_seguimientos,
    ejecutar_reparto,
    panel_secretaria,
)
from cases import views

urlpatterns = [
    # Gestión principal de casos
    path("secretaria/casos/", SecretaryCasesView.as_view(), name="secretary_cases"),
    path("reporte/", CaseReportView.as_view(), name="case_report"),

    # Reparto / distribución
    path("casos/distribuir/", CaseDistributionListView.as_view(), name="case_distribution_list"),
    path("casos/<int:case_id>/distribucion/", CaseDistributionView.as_view(), name="case_distribution"),
    path("panel/", panel_secretaria, name="panel_secretaria"),
    path("repartir/<int:caso_id>/", ejecutar_reparto, name="ejecutar_reparto"),

    # Consulta y detalle
    path("casos/<int:case_id>/", CaseDetailView.as_view(), name="case_detail"),
    path("casos/<int:case_id>/reasignar/", ReassignCaseView.as_view(), name="reassign_case"),
    path("casos/<int:case_id>/bitacora/", CaseBitacoraView.as_view(), name="case_bitacora"),

    # Casos asignados / filtros / categorías
    path("casos/asignados/categorias/", AssignedCasesCategoriesView.as_view(), name="assigned_cases_categories"),
    path("casos/asignados/filtrados/", AssignedCasesFilteredView.as_view(), name="assigned_cases_filtered"),
    path("api/casos/asignados/", AssignedCasesAPIView.as_view(), name="assigned_cases_api"),
    path("api/casos/buscar/", CaseSearchAPIView.as_view(), name="case_search_api"),
    path("api/casos/buscar-por-id/", CaseSearchByIdAPIView.as_view(), name="case_search_by_id_api"),
    path("api/casos/buscar-sin-asignar/", CaseSearchUnassignedByIdAPIView.as_view(), name="case_search_unassigned_api"),
    path("api/casos/cambiar-estado/", CaseStatusChangeAPIView.as_view(), name="case_status_change_api"),
    path("api/casos/cerrar/", CaseClosureAPIView.as_view(), name="case_closure_api"),

    # HU1 / HU2
    path("pending/", PendingCasesView.as_view(), name="pending_cases"),
    path("assigned/<int:case_id>/", AssignedCaseDetailView.as_view(), name="assigned_case_detail"),

    # Otros
    path("calendario/", calendario_seguimientos, name="calendario_seguimientos"),

    path('distribuir/automatico/', views.reparto_automatico_view, name='reparto_automatico'),
]