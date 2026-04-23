from django import forms
from accounts.models import User
from .models import BitacoraEntry


# ================================
# MULTI FILE INPUT CORRECTO
# ================================
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault(
            "widget",
            MultipleFileInput(attrs={
                "class": "hidden-file-input",
                "multiple": True
            }),
        )
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        """
        Convierte múltiples archivos en lista limpia
        """
        if not data:
            return []

        if not isinstance(data, (list, tuple)):
            data = [data]

        cleaned = []
        for f in data:
            cleaned.append(super().clean(f, initial))

        return cleaned


# ================================
# FORM BITÁCORA
# ================================
class BitacoraEntryForm(forms.ModelForm):

    ALLOWED_CONTENT_TYPES = [
        "application/pdf",
        "image/png",
        "image/jpeg",
    ]

    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

    files = MultipleFileField(required=False)

    class Meta:
        model = BitacoraEntry
        fields = ["entry_type", "content", "scheduled_for", "notify"]

        widgets = {
            "entry_type": forms.Select(attrs={"class": "form-select"}),

            "content": forms.Textarea(attrs={
                "class": "form-textarea",
                "placeholder": "Describe la actividad realizada...",
                "rows": 5,
            }),

            "scheduled_for": forms.DateTimeInput(
                attrs={
                    "class": "form-input",
                    "type": "datetime-local"
                },
                format="%Y-%m-%dT%H:%M"
            ),

            "notify": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
        }

        labels = {
            "entry_type": "Tipo de movimiento",
            "content": "Descripción",
            "scheduled_for": "Fecha del evento",
            "notify": "Enviar notificación",
        }

    def clean_files(self):
        """
        VALIDACIÓN CORRECTA DE ARCHIVOS
        """
        files = self.cleaned_data.get("files", [])

        for file in files:

            # Validar tipo
            content_type = getattr(file, "content_type", None)
            if content_type not in self.ALLOWED_CONTENT_TYPES:
                raise forms.ValidationError(
                    "Formato no permitido. Solo PDF, PNG y JPG."
                )

            # Validar tamaño
            if file.size > self.MAX_FILE_SIZE:
                raise forms.ValidationError(
                    "Archivo demasiado grande (máx 5MB)."
                )

        return files


# ================================
# FORM REPARTO / ASIGNACIÓN
# ================================
class CaseDistributionForm(forms.Form):

    CATEGORY_TYPES = {
        "PEN": [
            ("DER_FIS", "Derecho fiscal"),
            ("DER_DIS", "Derecho disciplinario"),
            ("PEN", "Penal"),
        ],
        "PUB": [
            ("MIG", "Migrantes"),
            ("DER_ADM", "Derecho Administrativo"),
        ],
        "LAB": [
            ("TUT", "Tutelas"),
            ("LIQ", "Liquidaciones"),
            ("PROC", "Procesos"),
        ],
        "CIV": [
            ("CON", "Conceptos"),
            ("PROC", "Procesos"),
        ],
        "FAM": [
            ("CON", "Conceptos"),
            ("PROC", "Procesos"),
        ],
        "ADM": [
            ("ASI", "Asignados"),
        ],
    }

    category = forms.ChoiceField(
        choices=[("", "-- Seleccionar --")] + [
            ("PEN", "Penal"),
            ("PUB", "Público"),
            ("LAB", "Laboral"),
            ("CIV", "Civil"),
            ("FAM", "Familia"),
            ("ADM", "Administrativo"),
        ],
        required=True,
        label="Categoría",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    case_type = forms.ChoiceField(
        choices=[("", "-- Seleccionar --")],
        required=True,
        label="Tipo",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    assigned_student = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=True,
        label="Estudiante asignado",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    notes = forms.CharField(
        required=False,
        label="Notas",
        widget=forms.Textarea(attrs={
            "class": "form-textarea",
            "rows": 3,
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 🔥 IMPORTANTE: carga dinámica de estudiantes
        self.fields["assigned_student"].queryset = User.objects.filter(
            role=User.Role.ESTUDIANTE,
            is_active=True
        ).order_by("first_name", "last_name")

    def clean_category(self):
        category = self.cleaned_data.get("category")
        if not category:
            raise forms.ValidationError("Seleccione una categoría.")
        return category

    def clean_case_type(self):
        case_type = self.cleaned_data.get("case_type")
        if not case_type:
            raise forms.ValidationError("Seleccione un tipo.")
        return case_type

    def clean_assigned_student(self):
        student = self.cleaned_data.get("assigned_student")

        if not student:
            raise forms.ValidationError("Debe seleccionar un estudiante.")

        if student.role != User.Role.ESTUDIANTE:
            raise forms.ValidationError("El usuario no es estudiante.")

        if not student.is_active:
            raise forms.ValidationError("El estudiante no está activo.")

        return student