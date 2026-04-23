from datetime import timedelta
from io import BytesIO

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils import timezone

from accounts.models import CaseDeadline, Notification, User
from accounts.services import run_deadline_check, run_inactivity_check
from cases.models import BitacoraEntry, Case, CaseDocument


class Command(BaseCommand):
    help = "Crea datos demo para probar usuarios, casos, bitácora, deadlines y notificaciones."

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Creando datos demo..."))

        # -------------------------------------------------
        # LIMPIEZA SEGURA DE DATOS DEMO
        # -------------------------------------------------
        Notification.objects.all().delete()
        CaseDeadline.objects.all().delete()
        BitacoraEntry.objects.all().delete()
        CaseDocument.objects.all().delete()
        Case.objects.all().delete()

        User.objects.filter(
            document_number__in=[
                "1001", "1002",   # secretarias
                "2001", "2002",   # asesores
                "3001", "3002", "3003", "3004", "3005",   # estudiantes
                "4001", "4002", "4003", "4004", "4005", "4006", "4007", "4008", "4009", "4010", "4011", "4012",  # beneficiarios
            ]
        ).delete()

        # -------------------------------------------------
        # USUARIOS
        # -------------------------------------------------
        secretaria1 = User.objects.create_user(
            document_number="1001",
            password="1234",
            first_name="Ana",
            last_name="Lopez",
            email="ana.secretaria@example.com",
            role=User.Role.SECRETARIA,
            is_active=True,
            is_staff=True,
        )

        secretaria2 = User.objects.create_user(
            document_number="1002",
            password="1234",
            first_name="Laura",
            last_name="Gomez",
            email="laura.secretaria@example.com",
            role=User.Role.SECRETARIA,
            is_active=True,
            is_staff=True,
        )

        asesor1 = User.objects.create_user(
            document_number="2001",
            password="1234",
            first_name="Roberto",
            last_name="Martinez",
            email="roberto.asesor@example.com",
            role=User.Role.ASESOR,
            is_active=True,
        )

        asesor2 = User.objects.create_user(
            document_number="2002",
            password="1234",
            first_name="Diana",
            last_name="Torres",
            email="diana.asesor@example.com",
            role=User.Role.ASESOR,
            is_active=True,
        )

        estudiante1 = User.objects.create_user(
            document_number="3001",
            password="1234",
            first_name="Carlos",
            last_name="Ramirez",
            email="carlos.estudiante@example.com",
            role=User.Role.ESTUDIANTE,
            is_active=True,
        )

        estudiante2 = User.objects.create_user(
            document_number="3002",
            password="1234",
            first_name="Valentina",
            last_name="Rojas",
            email="valentina.estudiante@example.com",
            role=User.Role.ESTUDIANTE,
            is_active=True,
        )
        
        estudiante3 = User.objects.create_user(
            document_number="3003",
            password="1234",
            first_name="Mateo",
            last_name="Silva",
            email="mateo.estudiante@example.com",
            role=User.Role.ESTUDIANTE,
            is_active=True,
        )

        estudiante4 = User.objects.create_user(
            document_number="3004",
            password="1234",
            first_name="Andrea",
            last_name="Moreno",
            email="andrea.estudiante@example.com",
            role=User.Role.ESTUDIANTE,
            is_active=True,
        )

        estudiante5 = User.objects.create_user(
            document_number="3005",
            password="1234",
            first_name="Felipe",
            last_name="Gutierrez",
            email="felipe.estudiante@example.com",
            role=User.Role.ESTUDIANTE,
            is_active=True,
        )

        beneficiario1 = User.objects.create_user(
            document_number="4001",
            password="1234",
            first_name="Maria",
            last_name="Perez",
            email="maria.beneficiario@example.com",
            role=User.Role.BENEFICIARIO,
            is_active=True,
        )

        beneficiario2 = User.objects.create_user(
            document_number="4002",
            password="1234",
            first_name="Juan",
            last_name="Castro",
            email="juan.beneficiario@example.com",
            role=User.Role.BENEFICIARIO,
            is_active=True,
        )

        beneficiario3 = User.objects.create_user(
            document_number="4003",
            password="1234",
            first_name="Elena",
            last_name="Moreno",
            email="elena.beneficiario@example.com",
            role=User.Role.BENEFICIARIO,
            is_active=True,
        )

        beneficiario4 = User.objects.create_user(
            document_number="4004",
            password="1234",
            first_name="Carlos",
            last_name="Lopez",
            email="carlos.beneficiario@example.com",
            role=User.Role.BENEFICIARIO,
            is_active=True,
        )

        beneficiario5 = User.objects.create_user(
            document_number="4005",
            password="1234",
            first_name="Teresa",
            last_name="Diaz",
            email="teresa.beneficiario@example.com",
            role=User.Role.BENEFICIARIO,
            is_active=True,
        )

        beneficiario6 = User.objects.create_user(
            document_number="4006",
            password="1234",
            first_name="Antonio",
            last_name="Rodriguez",
            email="antonio.beneficiario@example.com",
            role=User.Role.BENEFICIARIO,
            is_active=True,
        )

        beneficiario7 = User.objects.create_user(
            document_number="4007",
            password="1234",
            first_name="Patricia",
            last_name="Garcia",
            email="patricia.beneficiario@example.com",
            role=User.Role.BENEFICIARIO,
            is_active=True,
        )

        beneficiario8 = User.objects.create_user(
            document_number="4008",
            password="1234",
            first_name="Diego",
            last_name="Martinez",
            email="diego.beneficiario@example.com",
            role=User.Role.BENEFICIARIO,
            is_active=True,
        )

        beneficiario9 = User.objects.create_user(
            document_number="4009",
            password="1234",
            first_name="Sofia",
            last_name="Flores",
            email="sofia.beneficiario@example.com",
            role=User.Role.BENEFICIARIO,
            is_active=True,
        )

        beneficiario10 = User.objects.create_user(
            document_number="4010",
            password="1234",
            first_name="David",
            last_name="Jimenez",
            email="david.beneficiario@example.com",
            role=User.Role.BENEFICIARIO,
            is_active=True,
        )

        beneficiario11 = User.objects.create_user(
            document_number="4011",
            password="1234",
            first_name="Isabella",
            last_name="Vargas",
            email="isabella.beneficiario@example.com",
            role=User.Role.BENEFICIARIO,
            is_active=True,
        )

        beneficiario12 = User.objects.create_user(
            document_number="4012",
            password="1234",
            first_name="Roberto",
            last_name="Soto",
            email="roberto.beneficiario@example.com",
            role=User.Role.BENEFICIARIO,
            is_active=True,
        )

        # -------------------------------------------------
        # CASOS
        # -------------------------------------------------
        # CASOS EXISTENTES (compatibilidad)
        caso1 = Case.objects.create(
            case_number="00001",
            beneficiary=beneficiario1,
            assigned_student=estudiante1,
            advisor=asesor1,
            secretary=secretaria1,
            title="Caso laboral por despido",
            description="Consulta por posible despido sin justa causa.",
            category=Case.CaseCategory.LABORAL,
            case_type_specific=Case.LaboralType.PROCESOS,
            case_type=Case.CaseType.LABORAL,
            status=Case.CaseStatus.ASIGNADO,
            current_stage=Case.CaseStage.ASSIGNMENT,
            phone="3000000001",
            address="Cali, Valle",
        )

        caso2 = Case.objects.create(
            case_number="00002",
            beneficiary=beneficiario2,
            assigned_student=estudiante2,
            advisor=asesor2,
            secretary=secretaria2,
            title="Caso de familia - custodia",
            description="Solicitud de orientación por custodia compartida.",
            category=Case.CaseCategory.FAMILIA,
            case_type_specific=Case.FamiliaType.PROCESOS,
            case_type=Case.CaseType.FAMILIA,
            status=Case.CaseStatus.EN_PROCESO,
            current_stage=Case.CaseStage.INFORMATION_GATHERING,
            phone="3000000002",
            address="Palmira, Valle",
        )

        caso3 = Case.objects.create(
            case_number="00003",
            beneficiary=beneficiario1,
            assigned_student=None,
            advisor=asesor1,
            secretary=secretaria1,
            title="Caso civil pendiente",
            description="Consulta sobre incumplimiento contractual.",
            category=Case.CaseCategory.CIVIL,
            case_type_specific=Case.CivilType.CONCEPTOS,
            case_type=Case.CaseType.CIVIL,
            status=Case.CaseStatus.SIN_ASIGNAR,
            current_stage=Case.CaseStage.UNASSIGNED,
            phone="3000000003",
            address="Yumbo, Valle",
        )

        caso4 = Case.objects.create(
            case_number="00004",
            beneficiary=beneficiario2,
            assigned_student=estudiante1,
            advisor=asesor1,
            secretary=secretaria2,
            title="Caso penal con documentación",
            description="Consulta penal con etapa de documentación.",
            category=Case.CaseCategory.PENAL,
            case_type_specific=Case.PenalType.PENAL,
            case_type=Case.CaseType.PENAL,
            status=Case.CaseStatus.EN_PROCESO,
            current_stage=Case.CaseStage.INFORMATION_GATHERING,
            phone="3000000004",
            address="Jamundí, Valle",
        )

        # -------------------------------------------------
        # 4 CASOS COMPLETOS SIN ASIGNAR (PARA REPARTO MANUAL)
        # -------------------------------------------------
        caso_completo_1 = Case.objects.create(
            case_number="00005",
            beneficiary=beneficiario3,
            assigned_student=None,
            advisor=asesor1,
            secretary=secretaria1,
            title="Demanda civil por escrituración de propiedad",
            description="Caso civil completo sobre incumplimiento en escrituración de propiedad inmueble. Todas las pruebas disponibles.",
            category=Case.CaseCategory.CIVIL,
            case_type_specific=Case.CivilType.PROCESOS,
            case_type=Case.CaseType.CIVIL,
            status=Case.CaseStatus.SIN_ASIGNAR,
            current_stage=Case.CaseStage.UNASSIGNED,
            phone="3001112233",
            address="Cali, Barrio Granada",
        )

        caso_completo_2 = Case.objects.create(
            case_number="00006",
            beneficiary=beneficiario4,
            assigned_student=None,
            advisor=asesor2,
            secretary=secretaria2,
            title="Caso laboral por acoso en el trabajo",
            description="Demanda laboral por ambiente hostil y acoso. Documentación completa aportada.",
            category=Case.CaseCategory.LABORAL,
            case_type_specific=Case.LaboralType.TUTELAS,
            case_type=Case.CaseType.LABORAL,
            status=Case.CaseStatus.SIN_ASIGNAR,
            current_stage=Case.CaseStage.UNASSIGNED,
            phone="3002223344",
            address="Cali, Barrio San Alejo",
        )

        caso_completo_3 = Case.objects.create(
            case_number="00007",
            beneficiary=beneficiario5,
            assigned_student=None,
            advisor=asesor1,
            secretary=secretaria1,
            title="Consulta de derecho penal - defensa en juicio",
            description="Caso penal con todos los documentos y pruebas disponibles para defensa.",
            category=Case.CaseCategory.PENAL,
            case_type_specific=Case.PenalType.PENAL,
            case_type=Case.CaseType.PENAL,
            status=Case.CaseStatus.SIN_ASIGNAR,
            current_stage=Case.CaseStage.UNASSIGNED,
            phone="3003334455",
            address="Palmira, Centro",
        )

        caso_completo_4 = Case.objects.create(
            case_number="00008",
            beneficiary=beneficiario6,
            assigned_student=None,
            advisor=asesor2,
            secretary=secretaria2,
            title="Asunto de derecho administrativo - derecho de petición",
            description="Caso administrativo con documentación completa para solicitud ante entidad pública.",
            category=Case.CaseCategory.ADMINISTRATIVO,
            case_type_specific=Case.AdministrativoType.ASIGNADOS,
            case_type=Case.CaseType.OTRO,
            status=Case.CaseStatus.SIN_ASIGNAR,
            current_stage=Case.CaseStage.UNASSIGNED,
            phone="3004445566",
            address="Yumbo, Sur",
        )

        # 4 CASOS COMPLETOS ADICIONALES SIN ASIGNAR
        # -------------------------------------------------
        caso_completo_5 = Case.objects.create(
            case_number="00009",
            beneficiary=beneficiario11,
            assigned_student=None,
            advisor=asesor1,
            secretary=secretaria1,
            title="Demanda por incumplimiento de contrato comercial",
            description="Caso civil con documentación completa incluyendo contrato, facturas y pruebas de incumplimiento.",
            category=Case.CaseCategory.CIVIL,
            case_type_specific=Case.CivilType.CONCEPTOS,
            case_type=Case.CaseType.CIVIL,
            status=Case.CaseStatus.SIN_ASIGNAR,
            current_stage=Case.CaseStage.UNASSIGNED,
            phone="3009990011",
            address="Cali, Barrio Centro",
        )

        caso_completo_6 = Case.objects.create(
            case_number="00010",
            beneficiary=beneficiario12,
            assigned_student=None,
            advisor=asesor2,
            secretary=secretaria1,
            title="Caso laboral - liquidación de beneficios",
            description="Demanda por liquidación de prestaciones sociales. Documentación completa disponible.",
            category=Case.CaseCategory.LABORAL,
            case_type_specific=Case.LaboralType.LIQUIDACIONES,
            case_type=Case.CaseType.LABORAL,
            status=Case.CaseStatus.SIN_ASIGNAR,
            current_stage=Case.CaseStage.UNASSIGNED,
            phone="3009991111",
            address="Palmira, Barrio Santa Isabel",
        )

        caso_completo_7 = Case.objects.create(
            case_number="00011",
            beneficiary=beneficiario3,
            assigned_student=None,
            advisor=asesor1,
            secretary=secretaria2,
            title="Asunto de migración - solicitud de permiso de residencia",
            description="Caso de derecho público sobre derechos de migrantes con documentación de migración.",
            category=Case.CaseCategory.PUBLICO,
            case_type_specific=Case.PublicoType.MIGRANTES,
            case_type=Case.CaseType.OTRO,
            status=Case.CaseStatus.SIN_ASIGNAR,
            current_stage=Case.CaseStage.UNASSIGNED,
            phone="3009992222",
            address="Cali, Barrio Puerto",
        )

        caso_completo_8 = Case.objects.create(
            case_number="00012",
            beneficiary=beneficiario4,
            assigned_student=None,
            advisor=asesor2,
            secretary=secretaria2,
            title="Consulta de derecho penal - defensa preventiva",
            description="Caso penal preventivo con análisis jurídico completo y documentación de apoyo.",
            category=Case.CaseCategory.PENAL,
            case_type_specific=Case.PenalType.DERECHO_DISCIPLINARIO,
            case_type=Case.CaseType.PENAL,
            status=Case.CaseStatus.SIN_ASIGNAR,
            current_stage=Case.CaseStage.UNASSIGNED,
            phone="3009993333",
            address="Jamundí, Centro",
        )

        caso_completo_9 = Case.objects.create(
            case_number="00013",
            beneficiary=beneficiario1,
            assigned_student=None,
            advisor=asesor1,
            secretary=secretaria1,
            title="Consulta de propiedad intelectual - derechos de autor",
            description="Caso sobre protección de derechos de autor con documentación completa.",
            category=Case.CaseCategory.CIVIL,
            case_type_specific=Case.CivilType.PROCESOS,
            case_type=Case.CaseType.CIVIL,
            status=Case.CaseStatus.SIN_ASIGNAR,
            current_stage=Case.CaseStage.UNASSIGNED,
            phone="3001114444",
            address="Cali, Barrio Granada",
        )

        caso_completo_10 = Case.objects.create(
            case_number="00014",
            beneficiary=beneficiario2,
            assigned_student=None,
            advisor=asesor2,
            secretary=secretaria2,
            title="Consulta de acceso a información pública",
            description="Caso de accountability basado en solicitud de acceso a información.",
            category=Case.CaseCategory.ADMINISTRATIVO,
            case_type_specific=Case.AdministrativoType.ASIGNADOS,
            case_type=Case.CaseType.OTRO,
            status=Case.CaseStatus.SIN_ASIGNAR,
            current_stage=Case.CaseStage.UNASSIGNED,
            phone="3002225555",
            address="Cali, Barrio El Peñol",
        )

        caso_completo_11 = Case.objects.create(
            case_number="00015",
            beneficiary=beneficiario3,
            assigned_student=None,
            advisor=asesor1,
            secretary=secretaria1,
            title="Consulta de violencia intrafamiliar - medidas de protección",
            description="Caso de violencia intrafamiliar con solicitud de medidas cautelares.",
            category=Case.CaseCategory.FAMILIA,
            case_type_specific=Case.FamiliaType.PROCESOS,
            case_type=Case.CaseType.FAMILIA,
            status=Case.CaseStatus.SIN_ASIGNAR,
            current_stage=Case.CaseStage.UNASSIGNED,
            phone="3003336666",
            address="Cali, Barrio Javeriana",
        )

        caso_completo_12 = Case.objects.create(
            case_number="00016",
            beneficiary=beneficiario4,
            assigned_student=None,
            advisor=asesor2,
            secretary=secretaria2,
            title="Consulta de sucesión hereditaria - división de bienes",
            description="Caso de sucesión con documentación completa de bienes e inventarios.",
            category=Case.CaseCategory.CIVIL,
            case_type_specific=Case.CivilType.PROCESOS,
            case_type=Case.CaseType.CIVIL,
            status=Case.CaseStatus.SIN_ASIGNAR,
            current_stage=Case.CaseStage.UNASSIGNED,
            phone="3004447777",
            address="Cali, Barrio San Fernando",
        )

        caso_completo_13 = Case.objects.create(
            case_number="00017",
            beneficiary=beneficiario5,
            assigned_student=None,
            advisor=asesor1,
            secretary=secretaria1,
            title="Consulta de tutela constitucional - derechos fundamentales",
            description="Caso de tutela con fundamentos legales y pruebas documentales.",
            category=Case.CaseCategory.PUBLICO,
            case_type_specific=Case.PublicoType.DERECHO_ADMINISTRATIVO,
            case_type=Case.CaseType.OTRO,
            status=Case.CaseStatus.SIN_ASIGNAR,
            current_stage=Case.CaseStage.UNASSIGNED,
            phone="3005558888",
            address="Cali, Barrio El Lili",
        )

        caso_completo_14 = Case.objects.create(
            case_number="00018",
            beneficiary=beneficiario6,
            assigned_student=None,
            advisor=asesor2,
            secretary=secretaria2,
            title="Consulta de derecho laboral - despido injustificado",
            description="Caso laboral por despido con documentación de contrato y comunicaciones.",
            category=Case.CaseCategory.LABORAL,
            case_type_specific=Case.LaboralType.LIQUIDACIONES,
            case_type=Case.CaseType.LABORAL,
            status=Case.CaseStatus.SIN_ASIGNAR,
            current_stage=Case.CaseStage.UNASSIGNED,
            phone="3006669999",
            address="Cali, Barrio Santa Teresita",
        )

        caso_completo_15 = Case.objects.create(
            case_number="00019",
            beneficiary=beneficiario7,
            assigned_student=None,
            advisor=asesor1,
            secretary=secretaria1,
            title="Consulta penal - querella por difamación",
            description="Caso penal con pruebas de comunicaciones y testimonios documentados.",
            category=Case.CaseCategory.PENAL,
            case_type_specific=Case.PenalType.PENAL,
            case_type=Case.CaseType.PENAL,
            status=Case.CaseStatus.SIN_ASIGNAR,
            current_stage=Case.CaseStage.UNASSIGNED,
            phone="3007770000",
            address="Cali, Barrio Pensiones",
        )

        caso_completo_16 = Case.objects.create(
            case_number="00020",
            beneficiary=beneficiario1,
            assigned_student=None,
            advisor=asesor2,
            secretary=secretaria2,
            title="Consulta de compraventa de inmueble",
            description="Caso civil de compraventa con documentación de pago y transferencia.",
            category=Case.CaseCategory.CIVIL,
            case_type_specific=Case.CivilType.PROCESOS,
            case_type=Case.CaseType.CIVIL,
            status=Case.CaseStatus.SIN_ASIGNAR,
            current_stage=Case.CaseStage.UNASSIGNED,
            phone="3001111111",
            address="Cali, Barrio Cristóbal Colón",
        )

        caso_completo_17 = Case.objects.create(
            case_number="00021",
            beneficiary=beneficiario2,
            assigned_student=None,
            advisor=asesor1,
            secretary=secretaria1,
            title="Consulta de tutela por salud - medicamentos",
            description="Caso de tutela por derecho a la salud con prescripciones médicas.",
            category=Case.CaseCategory.PUBLICO,
            case_type_specific=Case.PublicoType.DERECHO_ADMINISTRATIVO,
            case_type=Case.CaseType.OTRO,
            status=Case.CaseStatus.SIN_ASIGNAR,
            current_stage=Case.CaseStage.UNASSIGNED,
            phone="3002222222",
            address="Cali, Barrio Floralia",
        )

        caso_completo_18 = Case.objects.create(
            case_number="00022",
            beneficiary=beneficiario3,
            assigned_student=None,
            advisor=asesor2,
            secretary=secretaria2,
            title="Consulta laboral - acoso sexual en el trabajo",
            description="Caso laboral por acoso sexual con testimonios y pruebas documentadas.",
            category=Case.CaseCategory.LABORAL,
            case_type_specific=Case.LaboralType.PROCESOS,
            case_type=Case.CaseType.LABORAL,
            status=Case.CaseStatus.SIN_ASIGNAR,
            current_stage=Case.CaseStage.UNASSIGNED,
            phone="3003333333",
            address="Cali, Barrio San Alejo",
        )

        caso_completo_19 = Case.objects.create(
            case_number="00023",
            beneficiary=beneficiario4,
            assigned_student=None,
            advisor=asesor1,
            secretary=secretaria1,
            title="Consulta penal - fraude electrónico",
            description="Caso de fraude electrónico con pruebas de transacciones irregulares.",
            category=Case.CaseCategory.PENAL,
            case_type_specific=Case.PenalType.PENAL,
            case_type=Case.CaseType.PENAL,
            status=Case.CaseStatus.SIN_ASIGNAR,
            current_stage=Case.CaseStage.UNASSIGNED,
            phone="3004444444",
            address="Cali, Barrio Meléndez",
        )

        caso_completo_20 = Case.objects.create(
            case_number="00024",
            beneficiary=beneficiario5,
            assigned_student=None,
            advisor=asesor2,
            secretary=secretaria2,
            title="Consulta de divorcio y custodia de menores",
            description="Caso de divorcio con solución de custodia e información de hijos.",
            category=Case.CaseCategory.FAMILIA,
            case_type_specific=Case.FamiliaType.CONCEPTOS,
            case_type=Case.CaseType.FAMILIA,
            status=Case.CaseStatus.SIN_ASIGNAR,
            current_stage=Case.CaseStage.UNASSIGNED,
            phone="3005555555",
            address="Cali, Barrio Chipichape",
        )

        caso_completo_21 = Case.objects.create(
            case_number="00025",
            beneficiary=beneficiario6,
            assigned_student=None,
            advisor=asesor1,
            secretary=secretaria1,
            title="Consulta de desalojo por falta de pago",
            description="Caso de desalojo con documentación de contratos de arrendamiento y deudas.",
            category=Case.CaseCategory.CIVIL,
            case_type_specific=Case.CivilType.PROCESOS,
            case_type=Case.CaseType.CIVIL,
            status=Case.CaseStatus.SIN_ASIGNAR,
            current_stage=Case.CaseStage.UNASSIGNED,
            phone="3006666666",
            address="Cali, Barrio Ciudadela Comfandi",
        )

        caso_completo_22 = Case.objects.create(
            case_number="00026",
            beneficiary=beneficiario7,
            assigned_student=None,
            advisor=asesor2,
            secretary=secretaria2,
            title="Consulta de reconocimiento de paternidad",
            description="Caso de reconocimiento de paternidad con pruebas biológicas y documentos.",
            category=Case.CaseCategory.FAMILIA,
            case_type_specific=Case.FamiliaType.PROCESOS,
            case_type=Case.CaseType.FAMILIA,
            status=Case.CaseStatus.SIN_ASIGNAR,
            current_stage=Case.CaseStage.UNASSIGNED,
            phone="3007777777",
            address="Cali, Barrio Eduardo Santos",
        )

        caso_completo_23 = Case.objects.create(
            case_number="00031",
            beneficiary=beneficiario1,
            assigned_student=None,
            advisor=asesor1,
            secretary=secretaria1,
            title="Consulta de negligencia médica",
            description="Caso de negligencia médica con informes clínicos e históricos médicos.",
            category=Case.CaseCategory.PENAL,
            case_type_specific=Case.PenalType.PENAL,
            case_type=Case.CaseType.PENAL,
            status=Case.CaseStatus.SIN_ASIGNAR,
            current_stage=Case.CaseStage.UNASSIGNED,
            phone="3008888888",
            address="Cali, Barrio El Peñol",
        )

        caso_completo_24 = Case.objects.create(
            case_number="00032",
            beneficiary=beneficiario2,
            assigned_student=None,
            advisor=asesor2,
            secretary=secretaria2,
            title="Consulta de reparación de daño ambiental",
            description="Caso de daño ambiental con peritos ambientales y reportes técnicos.",
            category=Case.CaseCategory.PUBLICO,
            case_type_specific=Case.PublicoType.DERECHO_ADMINISTRATIVO,
            case_type=Case.CaseType.OTRO,
            status=Case.CaseStatus.SIN_ASIGNAR,
            current_stage=Case.CaseStage.UNASSIGNED,
            phone="3009999999",
            address="Cali, Barrio El Calvario",
        )

        # -------------------------------------------------
        # 4 CASOS INCOMPLETOS SIN ASIGNAR (PARA ENVIAR A REVISION)
        # -------------------------------------------------
        caso_incompleto_1 = Case.objects.create(
            case_number="00027",
            beneficiary=beneficiario7,
            assigned_student=None,
            advisor=asesor1,
            secretary=secretaria1,
            title="Consulta familia - pensión alimentaria",
            description="Caso de pensión alimentaria sin documentación completa.",
            category=Case.CaseCategory.FAMILIA,
            case_type_specific=Case.FamiliaType.PROCESOS,
            case_type=Case.CaseType.FAMILIA,
            status=Case.CaseStatus.SIN_ASIGNAR,
            current_stage=Case.CaseStage.UNASSIGNED,
            phone="3005556677",
            address="Jamundí",
        )

        caso_incompleto_2 = Case.objects.create(
            case_number="00028",
            beneficiary=beneficiario8,
            assigned_student=None,
            advisor=asesor2,
            secretary=secretaria2,
            title="Caso laboral en etapa inicial",
            description="Demanda laboral que requiere más documentación del empleador.",
            category=Case.CaseCategory.LABORAL,
            case_type_specific=Case.LaboralType.PROCESOS,
            case_type=Case.CaseType.LABORAL,
            status=Case.CaseStatus.SIN_ASIGNAR,
            current_stage=Case.CaseStage.UNASSIGNED,
            phone="3006667788",
            address="Cali, Barrio Ciudad 2000",
        )

        caso_incompleto_3 = Case.objects.create(
            case_number="00029",
            beneficiary=beneficiario9,
            assigned_student=None,
            advisor=asesor1,
            secretary=secretaria1,
            title="Consulta civil - herencia sin liquidar",
            description="Caso civil sobre herencia que necesita documentos del notario.",
            category=Case.CaseCategory.CIVIL,
            case_type_specific=Case.CivilType.CONCEPTOS,
            case_type=Case.CaseType.CIVIL,
            status=Case.CaseStatus.SIN_ASIGNAR,
            current_stage=Case.CaseStage.UNASSIGNED,
            phone="3007778899",
            address="Palmira, Barrio El Pilar",
        )

        caso_incompleto_4 = Case.objects.create(
            case_number="00030",
            beneficiary=beneficiario10,
            assigned_student=None,
            advisor=asesor2,
            secretary=secretaria2,
            title="Caso público - derechos de migrantes",
            description="Caso de migración en proceso inicial, falta documentación de identidad.",
            category=Case.CaseCategory.PUBLICO,
            case_type_specific=Case.PublicoType.MIGRANTES,
            case_type=Case.CaseType.OTRO,
            status=Case.CaseStatus.SIN_ASIGNAR,
            current_stage=Case.CaseStage.UNASSIGNED,
            phone="3008889900",
            address="Cali, Puerto",
        )

        now = timezone.now()

        # -------------------------------------------------
        # DOCUMENTOS PARA CASOS COMPLETOS
        # -------------------------------------------------
        # Helper function para crear archivos demo
        def create_demo_file(name, content):
            return ContentFile(content.encode('utf-8'), name=name)

        # Documentos para caso_completo_1
        for doc_type, doc_name in [
            (CaseDocument.DocumentType.DOCUMENTO, "escritura_propiedad.pdf"),
            (CaseDocument.DocumentType.RECIBO_SERVICIOS, "recibo_asesoramiento.pdf"),
            (CaseDocument.DocumentType.FOTO, "prueba_fisica.jpg"),
        ]:
            doc = CaseDocument.objects.create(
                case=caso_completo_1,
                document_type=doc_type,
                file=create_demo_file(doc_name, f"Contenido demo para {doc_name}"),
                original_name=doc_name,
                is_valid=True,
                uploaded_by=secretaria1,
            )

        # Documentos para caso_completo_2
        for doc_type, doc_name in [
            (CaseDocument.DocumentType.DOCUMENTO, "contrato_laboral.pdf"),
            (CaseDocument.DocumentType.RECIBO_SERVICIOS, "recibo_consulta.pdf"),
            (CaseDocument.DocumentType.FOTO, "evidencia_acoso.jpg"),
        ]:
            doc = CaseDocument.objects.create(
                case=caso_completo_2,
                document_type=doc_type,
                file=create_demo_file(doc_name, f"Contenido demo para {doc_name}"),
                original_name=doc_name,
                is_valid=True,
                uploaded_by=secretaria2,
            )

        # Documentos para caso_completo_3
        for doc_type, doc_name in [
            (CaseDocument.DocumentType.DOCUMENTO, "denuncia_penal.pdf"),
            (CaseDocument.DocumentType.RECIBO_SERVICIOS, "recibo_defensa.pdf"),
            (CaseDocument.DocumentType.FOTO, "prueba_fisica_penal.jpg"),
        ]:
            doc = CaseDocument.objects.create(
                case=caso_completo_3,
                document_type=doc_type,
                file=create_demo_file(doc_name, f"Contenido demo para {doc_name}"),
                original_name=doc_name,
                is_valid=True,
                uploaded_by=secretaria1,
            )

        # Documentos para caso_completo_4
        for doc_type, doc_name in [
            (CaseDocument.DocumentType.DOCUMENTO, "derechos_de_peticion.pdf"),
            (CaseDocument.DocumentType.RECIBO_SERVICIOS, "recibo_gestion.pdf"),
            (CaseDocument.DocumentType.FOTO, "certificado_entidad.jpg"),
        ]:
            doc = CaseDocument.objects.create(
                case=caso_completo_4,
                document_type=doc_type,
                file=create_demo_file(doc_name, f"Contenido demo para {doc_name}"),
                original_name=doc_name,
                is_valid=True,
                uploaded_by=secretaria2,
            )

        # Documentos para caso_completo_5
        for doc_type, doc_name in [
            (CaseDocument.DocumentType.DOCUMENTO, "contrato_comercial.pdf"),
            (CaseDocument.DocumentType.RECIBO_SERVICIOS, "recibo_contractual.pdf"),
            (CaseDocument.DocumentType.FOTO, "prueba_incumplimiento.jpg"),
        ]:
            doc = CaseDocument.objects.create(
                case=caso_completo_5,
                document_type=doc_type,
                file=create_demo_file(doc_name, f"Contenido demo para {doc_name}"),
                original_name=doc_name,
                is_valid=True,
                uploaded_by=secretaria1,
            )

        # Documentos para caso_completo_6
        for doc_type, doc_name in [
            (CaseDocument.DocumentType.DOCUMENTO, "acta_liquidacion.pdf"),
            (CaseDocument.DocumentType.RECIBO_SERVICIOS, "recibo_liquidacion.pdf"),
            (CaseDocument.DocumentType.FOTO, "comprobante_beneficios.jpg"),
        ]:
            doc = CaseDocument.objects.create(
                case=caso_completo_6,
                document_type=doc_type,
                file=create_demo_file(doc_name, f"Contenido demo para {doc_name}"),
                original_name=doc_name,
                is_valid=True,
                uploaded_by=secretaria1,
            )

        # Documentos para caso_completo_7
        for doc_type, doc_name in [
            (CaseDocument.DocumentType.DOCUMENTO, "solicitud_migracion.pdf"),
            (CaseDocument.DocumentType.RECIBO_SERVICIOS, "recibo_migracion.pdf"),
            (CaseDocument.DocumentType.FOTO, "documento_identidad.jpg"),
        ]:
            doc = CaseDocument.objects.create(
                case=caso_completo_7,
                document_type=doc_type,
                file=create_demo_file(doc_name, f"Contenido demo para {doc_name}"),
                original_name=doc_name,
                is_valid=True,
                uploaded_by=secretaria2,
            )

        # Documentos para caso_completo_8
        for doc_type, doc_name in [
            (CaseDocument.DocumentType.DOCUMENTO, "defensa_penal.pdf"),
            (CaseDocument.DocumentType.RECIBO_SERVICIOS, "recibo_defensa.pdf"),
            (CaseDocument.DocumentType.FOTO, "prueba_defensa.jpg"),
        ]:
            doc = CaseDocument.objects.create(
                case=caso_completo_8,
                document_type=doc_type,
                file=create_demo_file(doc_name, f"Contenido demo para {doc_name}"),
                original_name=doc_name,
                is_valid=True,
                uploaded_by=secretaria2,
            )

        # Documentos para caso_completo_9
        for doc_type, doc_name in [
            (CaseDocument.DocumentType.DOCUMENTO, "derechos_autor.pdf"),
            (CaseDocument.DocumentType.RECIBO_SERVICIOS, "recibo_autor.pdf"),
            (CaseDocument.DocumentType.FOTO, "evidencia_autor.jpg"),
        ]:
            doc = CaseDocument.objects.create(
                case=caso_completo_9,
                document_type=doc_type,
                file=create_demo_file(doc_name, f"Contenido demo para {doc_name}"),
                original_name=doc_name,
                is_valid=True,
                uploaded_by=secretaria1,
            )

        # Documentos para caso_completo_10
        for doc_type, doc_name in [
            (CaseDocument.DocumentType.DOCUMENTO, "solicitud_info.pdf"),
            (CaseDocument.DocumentType.RECIBO_SERVICIOS, "recibo_info.pdf"),
            (CaseDocument.DocumentType.FOTO, "prueba_info.jpg"),
        ]:
            doc = CaseDocument.objects.create(
                case=caso_completo_10,
                document_type=doc_type,
                file=create_demo_file(doc_name, f"Contenido demo para {doc_name}"),
                original_name=doc_name,
                is_valid=True,
                uploaded_by=secretaria2,
            )

        # Documentos para caso_completo_11
        for doc_type, doc_name in [
            (CaseDocument.DocumentType.DOCUMENTO, "violencia_intrafamiliar.pdf"),
            (CaseDocument.DocumentType.RECIBO_SERVICIOS, "recibo_violencia.pdf"),
            (CaseDocument.DocumentType.FOTO, "prueba_violencia.jpg"),
        ]:
            doc = CaseDocument.objects.create(
                case=caso_completo_11,
                document_type=doc_type,
                file=create_demo_file(doc_name, f"Contenido demo para {doc_name}"),
                original_name=doc_name,
                is_valid=True,
                uploaded_by=secretaria1,
            )

        # Documentos para caso_completo_12
        for doc_type, doc_name in [
            (CaseDocument.DocumentType.DOCUMENTO, "sucesion_hereditaria.pdf"),
            (CaseDocument.DocumentType.RECIBO_SERVICIOS, "recibo_sucesion.pdf"),
            (CaseDocument.DocumentType.FOTO, "inventario_bienes.jpg"),
        ]:
            doc = CaseDocument.objects.create(
                case=caso_completo_12,
                document_type=doc_type,
                file=create_demo_file(doc_name, f"Contenido demo para {doc_name}"),
                original_name=doc_name,
                is_valid=True,
                uploaded_by=secretaria2,
            )

        # Documentos para caso_completo_13
        for doc_type, doc_name in [
            (CaseDocument.DocumentType.DOCUMENTO, "tutela_constitucional.pdf"),
            (CaseDocument.DocumentType.RECIBO_SERVICIOS, "recibo_tutela.pdf"),
            (CaseDocument.DocumentType.FOTO, "prueba_tutela.jpg"),
        ]:
            doc = CaseDocument.objects.create(
                case=caso_completo_13,
                document_type=doc_type,
                file=create_demo_file(doc_name, f"Contenido demo para {doc_name}"),
                original_name=doc_name,
                is_valid=True,
                uploaded_by=secretaria1,
            )

        # Documentos para caso_completo_14
        for doc_type, doc_name in [
            (CaseDocument.DocumentType.DOCUMENTO, "despido_injustificado.pdf"),
            (CaseDocument.DocumentType.RECIBO_SERVICIOS, "recibo_laboral.pdf"),
            (CaseDocument.DocumentType.FOTO, "contrato_laboral.jpg"),
        ]:
            doc = CaseDocument.objects.create(
                case=caso_completo_14,
                document_type=doc_type,
                file=create_demo_file(doc_name, f"Contenido demo para {doc_name}"),
                original_name=doc_name,
                is_valid=True,
                uploaded_by=secretaria2,
            )

        # Documentos para caso_completo_15
        for doc_type, doc_name in [
            (CaseDocument.DocumentType.DOCUMENTO, "querella_difamacion.pdf"),
            (CaseDocument.DocumentType.RECIBO_SERVICIOS, "recibo_penal.pdf"),
            (CaseDocument.DocumentType.FOTO, "prueba_penal.jpg"),
        ]:
            doc = CaseDocument.objects.create(
                case=caso_completo_15,
                document_type=doc_type,
                file=create_demo_file(doc_name, f"Contenido demo para {doc_name}"),
                original_name=doc_name,
                is_valid=True,
                uploaded_by=secretaria1,
            )

        # Documentos para caso_completo_16
        for doc_type, doc_name in [
            (CaseDocument.DocumentType.DOCUMENTO, "compraventa_inmueble.pdf"),
            (CaseDocument.DocumentType.RECIBO_SERVICIOS, "recibo_compraventa.pdf"),
            (CaseDocument.DocumentType.FOTO, "titulo_propiedad.jpg"),
        ]:
            doc = CaseDocument.objects.create(
                case=caso_completo_16,
                document_type=doc_type,
                file=create_demo_file(doc_name, f"Contenido demo para {doc_name}"),
                original_name=doc_name,
                is_valid=True,
                uploaded_by=secretaria2,
            )

        # Documentos para caso_completo_17
        for doc_type, doc_name in [
            (CaseDocument.DocumentType.DOCUMENTO, "tutela_salud.pdf"),
            (CaseDocument.DocumentType.RECIBO_SERVICIOS, "recibo_salud.pdf"),
            (CaseDocument.DocumentType.FOTO, "prescripcion_medica.jpg"),
        ]:
            doc = CaseDocument.objects.create(
                case=caso_completo_17,
                document_type=doc_type,
                file=create_demo_file(doc_name, f"Contenido demo para {doc_name}"),
                original_name=doc_name,
                is_valid=True,
                uploaded_by=secretaria1,
            )

        # Documentos para caso_completo_18
        for doc_type, doc_name in [
            (CaseDocument.DocumentType.DOCUMENTO, "acoso_sexual.pdf"),
            (CaseDocument.DocumentType.RECIBO_SERVICIOS, "recibo_acoso.pdf"),
            (CaseDocument.DocumentType.FOTO, "testimonio_acoso.jpg"),
        ]:
            doc = CaseDocument.objects.create(
                case=caso_completo_18,
                document_type=doc_type,
                file=create_demo_file(doc_name, f"Contenido demo para {doc_name}"),
                original_name=doc_name,
                is_valid=True,
                uploaded_by=secretaria2,
            )

        # Documentos para caso_completo_19
        for doc_type, doc_name in [
            (CaseDocument.DocumentType.DOCUMENTO, "fraude_electronico.pdf"),
            (CaseDocument.DocumentType.RECIBO_SERVICIOS, "recibo_fraude.pdf"),
            (CaseDocument.DocumentType.FOTO, "transacciones_fraude.jpg"),
        ]:
            doc = CaseDocument.objects.create(
                case=caso_completo_19,
                document_type=doc_type,
                file=create_demo_file(doc_name, f"Contenido demo para {doc_name}"),
                original_name=doc_name,
                is_valid=True,
                uploaded_by=secretaria1,
            )

        # Documentos para caso_completo_20
        for doc_type, doc_name in [
            (CaseDocument.DocumentType.DOCUMENTO, "divorcio_custodia.pdf"),
            (CaseDocument.DocumentType.RECIBO_SERVICIOS, "recibo_familia.pdf"),
            (CaseDocument.DocumentType.FOTO, "acta_nacimiento.jpg"),
        ]:
            doc = CaseDocument.objects.create(
                case=caso_completo_20,
                document_type=doc_type,
                file=create_demo_file(doc_name, f"Contenido demo para {doc_name}"),
                original_name=doc_name,
                is_valid=True,
                uploaded_by=secretaria2,
            )

        # Documentos para caso_completo_21
        for doc_type, doc_name in [
            (CaseDocument.DocumentType.DOCUMENTO, "desalojo_pago.pdf"),
            (CaseDocument.DocumentType.RECIBO_SERVICIOS, "recibo_desalojo.pdf"),
            (CaseDocument.DocumentType.FOTO, "contrato_arrendamiento.jpg"),
        ]:
            doc = CaseDocument.objects.create(
                case=caso_completo_21,
                document_type=doc_type,
                file=create_demo_file(doc_name, f"Contenido demo para {doc_name}"),
                original_name=doc_name,
                is_valid=True,
                uploaded_by=secretaria1,
            )

        # Documentos para caso_completo_22
        for doc_type, doc_name in [
            (CaseDocument.DocumentType.DOCUMENTO, "reconocimiento_paternidad.pdf"),
            (CaseDocument.DocumentType.RECIBO_SERVICIOS, "recibo_paternidad.pdf"),
            (CaseDocument.DocumentType.FOTO, "prueba_biologica.jpg"),
        ]:
            doc = CaseDocument.objects.create(
                case=caso_completo_22,
                document_type=doc_type,
                file=create_demo_file(doc_name, f"Contenido demo para {doc_name}"),
                original_name=doc_name,
                is_valid=True,
                uploaded_by=secretaria2,
            )

        # Documentos para caso_completo_23
        for doc_type, doc_name in [
            (CaseDocument.DocumentType.DOCUMENTO, "negligencia_medica.pdf"),
            (CaseDocument.DocumentType.RECIBO_SERVICIOS, "recibo_medico.pdf"),
            (CaseDocument.DocumentType.FOTO, "historial_clinico.jpg"),
        ]:
            doc = CaseDocument.objects.create(
                case=caso_completo_23,
                document_type=doc_type,
                file=create_demo_file(doc_name, f"Contenido demo para {doc_name}"),
                original_name=doc_name,
                is_valid=True,
                uploaded_by=secretaria1,
            )

        # Documentos para caso_completo_24
        for doc_type, doc_name in [
            (CaseDocument.DocumentType.DOCUMENTO, "daño_ambiental.pdf"),
            (CaseDocument.DocumentType.RECIBO_SERVICIOS, "recibo_ambiental.pdf"),
            (CaseDocument.DocumentType.FOTO, "reporte_pericial.jpg"),
        ]:
            doc = CaseDocument.objects.create(
                case=caso_completo_24,
                document_type=doc_type,
                file=create_demo_file(doc_name, f"Contenido demo para {doc_name}"),
                original_name=doc_name,
                is_valid=True,
                uploaded_by=secretaria2,
            )

        # Documentos incompletos para casos incompletos (solo 1-2 documentos)
        # caso_incompleto_1: solo documento y foto (falta recibo)
        CaseDocument.objects.create(
            case=caso_incompleto_1,
            document_type=CaseDocument.DocumentType.DOCUMENTO,
            file=create_demo_file("solicitud.pdf", "Contenido demo"),
            original_name="solicitud.pdf",
            is_valid=True,
            uploaded_by=secretaria1,
        )
        CaseDocument.objects.create(
            case=caso_incompleto_1,
            document_type=CaseDocument.DocumentType.FOTO,
            file=create_demo_file("prueba.jpg", "Contenido demo"),
            original_name="prueba.jpg",
            is_valid=True,
            uploaded_by=secretaria1,
        )

        # caso_incompleto_2: solo documento (faltan recibo y foto)
        CaseDocument.objects.create(
            case=caso_incompleto_2,
            document_type=CaseDocument.DocumentType.DOCUMENTO,
            file=create_demo_file("demanda.pdf", "Contenido demo"),
            original_name="demanda.pdf",
            is_valid=True,
            uploaded_by=secretaria2,
        )

        # caso_incompleto_3: documento y recibo (falta foto)
        CaseDocument.objects.create(
            case=caso_incompleto_3,
            document_type=CaseDocument.DocumentType.DOCUMENTO,
            file=create_demo_file("testamento.pdf", "Contenido demo"),
            original_name="testamento.pdf",
            is_valid=True,
            uploaded_by=secretaria1,
        )
        CaseDocument.objects.create(
            case=caso_incompleto_3,
            document_type=CaseDocument.DocumentType.RECIBO_SERVICIOS,
            file=create_demo_file("recibo.pdf", "Contenido demo"),
            original_name="recibo.pdf",
            is_valid=True,
            uploaded_by=secretaria1,
        )

        # caso_incompleto_4: solo documento (faltan recibo y foto)
        CaseDocument.objects.create(
            case=caso_incompleto_4,
            document_type=CaseDocument.DocumentType.DOCUMENTO,
            file=create_demo_file("pasaporte.pdf", "Contenido demo"),
            original_name="pasaporte.pdf",
            is_valid=True,
            uploaded_by=secretaria2,
        )

        # -------------------------------------------------
        # BITÁCORA
        # -------------------------------------------------
        entrada1 = BitacoraEntry.objects.create(
            case=caso1,
            author=secretaria1,
            entry_type=BitacoraEntry.EntryType.ASIGNACION,
            content="Caso asignado al estudiante Carlos Ramírez.",
            notify=False,
        )

        entrada2 = BitacoraEntry.objects.create(
            case=caso2,
            author=estudiante2,
            entry_type=BitacoraEntry.EntryType.ACTUALIZACION,
            content="Se realizó entrevista inicial con el beneficiario.",
            notify=False,
        )

        entrada3 = BitacoraEntry.objects.create(
            case=caso4,
            author=asesor1,
            entry_type=BitacoraEntry.EntryType.DOCUMENTO,
            content="Se revisó documentación inicial aportada.",
            notify=False,
        )

        # Forzar fechas viejas / recientes
        BitacoraEntry.objects.filter(id=entrada1.id).update(created_at=now - timedelta(days=10))
        BitacoraEntry.objects.filter(id=entrada2.id).update(created_at=now - timedelta(days=1))
        BitacoraEntry.objects.filter(id=entrada3.id).update(created_at=now - timedelta(days=8))

        Case.objects.filter(id=caso1.id).update(updated_at=now - timedelta(days=10))
        Case.objects.filter(id=caso2.id).update(updated_at=now - timedelta(days=1))
        Case.objects.filter(id=caso3.id).update(updated_at=now - timedelta(days=2))
        Case.objects.filter(id=caso4.id).update(updated_at=now - timedelta(days=8))

        caso1.refresh_from_db()
        caso2.refresh_from_db()
        caso3.refresh_from_db()
        caso4.refresh_from_db()

        # -------------------------------------------------
        # FECHAS LÍMITE
        # -------------------------------------------------
        CaseDeadline.objects.create(
            case=caso1,
            created_by=secretaria1,
            title="Entrega de documentos laborales",
            description="Debe entregarse soporte documental del despido.",
            due_date=now + timedelta(days=1),
            is_completed=False,
        )

        CaseDeadline.objects.create(
            case=caso2,
            created_by=asesor2,
            title="Audiencia preliminar",
            description="Preparación para audiencia preliminar.",
            due_date=now,
            is_completed=False,
        )

        CaseDeadline.objects.create(
            case=caso4,
            created_by=secretaria2,
            title="Término procesal vencido",
            description="Fecha procesal ya vencida para pruebas.",
            due_date=now - timedelta(days=2),
            is_completed=False,
        )

        # -------------------------------------------------
        # GENERAR NOTIFICACIONES
        # -------------------------------------------------
        run_inactivity_check()
        run_deadline_check()

        # -------------------------------------------------
        # RESUMEN
        # -------------------------------------------------
        self.stdout.write(self.style.SUCCESS("Datos demo creados correctamente."))
        self.stdout.write("")
        self.stdout.write("USUARIOS (Login):") 
        self.stdout.write("  Secretaría 1     -> 1001 / 1234")
        self.stdout.write("  Secretaría 2     -> 1002 / 1234")
        self.stdout.write("  Asesor 1         -> 2001 / 1234")
        self.stdout.write("  Asesor 2         -> 2002 / 1234")
        self.stdout.write("  Estudiante 1     -> 3001 / 1234")
        self.stdout.write("  Estudiante 2     -> 3002 / 1234")
        self.stdout.write("  Estudiante 3     -> 3003 / 1234")
        self.stdout.write("  Estudiante 4     -> 3004 / 1234")
        self.stdout.write("  Estudiante 5     -> 3005 / 1234")
        self.stdout.write("  Beneficiario 1   -> 4001 / 1234")
        self.stdout.write("")
        self.stdout.write("CASOS PARA REPARTO MANUAL:")
        self.stdout.write("  ✓ 24 CASOS COMPLETOS (SIN ASIGNAR):")
        self.stdout.write("    - CASO-2026-010: Demanda civil por escrituración")
        self.stdout.write("    - CASO-2026-020: Caso laboral por acoso")
        self.stdout.write("    - CASO-2026-030: Defensa penal")
        self.stdout.write("    - CASO-2026-040: Derecho administrativo")
        self.stdout.write("    - CASO-2026-090: Incumplimiento de contrato")
        self.stdout.write("    - CASO-2026-100: Liquidación de beneficios")
        self.stdout.write("    - CASO-2026-110: Solicitud de migración")
        self.stdout.write("    - CASO-2026-120: Defensa penal disciplinaria")
        self.stdout.write("    - CASO-2026-130: Propiedad intelectual - derechos de autor")
        self.stdout.write("    - CASO-2026-140: Acceso a información pública")
        self.stdout.write("    - CASO-2026-150: Violencia intrafamiliar")
        self.stdout.write("    - CASO-2026-160: Sucesión hereditaria - división de bienes")
        self.stdout.write("    - CASO-2026-170: Tutela constitucional - derechos fundamentales")
        self.stdout.write("    - CASO-2026-180: Derecho laboral - despido injustificado")
        self.stdout.write("    - CASO-2026-190: Penal - querella por difamación")
        self.stdout.write("    - CASO-2026-200: Compraventa de inmueble")
        self.stdout.write("    - CASO-2026-210: Tutela por salud - medicamentos")
        self.stdout.write("    - CASO-2026-220: Laboral - acoso sexual en el trabajo")
        self.stdout.write("    - CASO-2026-230: Penal - fraude electrónico")
        self.stdout.write("    - CASO-2026-240: Familia - divorcio y custodia de menores")
        self.stdout.write("    - CASO-2026-250: Desalojo por falta de pago")
        self.stdout.write("    - CASO-2026-260: Reconocimiento de paternidad")
        self.stdout.write("    - CASO-2026-270: Negligencia médica")
        self.stdout.write("    - CASO-2026-280: Reparación de daño ambiental")
        self.stdout.write("")
        self.stdout.write("  ⚠ 4 CASOS INCOMPLETOS (SIN ASIGNAR - PARA ENVIAR A REVISIÓN):")
        self.stdout.write("    - CASO-2026-050: Pensión alimentaria (falta recibo)")
        self.stdout.write("    - CASO-2026-060: Laboral en etapa inicial (faltan recibo y foto)")
        self.stdout.write("    - CASO-2026-070: Herencia (falta foto)")
        self.stdout.write("    - CASO-2026-080: Derechos de migrantes (faltan recibo y foto)")
        self.stdout.write("")

        # -------------------------------------------------
        # ASIGNAR NÚMEROS SECUENCIALES
        # -------------------------------------------------
        # Asignar sequence_number basado en case_number ordenado
        cases_ordered = Case.objects.all().order_by('case_number')
        for seq_num, case in enumerate(cases_ordered, start=1):
            case.sequence_number = seq_num
            case.save(update_fields=['sequence_number'])

        self.stdout.write(f"Resumen: {Case.objects.count()} casos creados")
        self.stdout.write(f"  - {CaseDocument.objects.count()} documentos")
        self.stdout.write(f"  - {BitacoraEntry.objects.count()} bitácoras")
        self.stdout.write(f"  - {CaseDeadline.objects.count()} deadlines")
        self.stdout.write(f"  - {Notification.objects.count()} notificaciones")