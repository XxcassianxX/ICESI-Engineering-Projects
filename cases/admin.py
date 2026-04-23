from django.contrib import admin
from .models import Case, CaseAssignment, BitacoraEntry

admin.site.register(Case)
admin.site.register(CaseAssignment)
admin.site.register(BitacoraEntry)
