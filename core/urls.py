from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Accounts (login, dashboards, etc.)
    path("", include("accounts.urls")),

    # Cases (todo lo de casos)
    path("cases/", include("cases.urls")),
]

# Archivos media (uploads)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)