from django.contrib import admin
from users.models import User  # Asegúrate de importar el modelo User de la aplicación 'users'
from django.contrib import admin
from inscripcion.models import Inscripcion, Grupo, Asignatura, HistorialInscripcion



class SemestreFilter(admin.SimpleListFilter):
    title = 'Semestre'
    parameter_name = 'semestre_actual'

    def lookups(self, request, model_admin):
        # Obtener todos los semestres disponibles en la base de datos
        semestres = User.objects.values_list('semestre_actual', flat=True).distinct()
        choices = [(semestre, f'Semestre {semestre}') for semestre in semestres]
        return choices

    def queryset(self, request, queryset):
        if self.value():
            # Obtener los usuarios con el semestre seleccionado
            usuarios_con_semestre = User.objects.filter(semestre_actual=self.value())

            # Filtrar las inscripciones correspondientes a los usuarios con el semestre seleccionado
            inscripciones_filtradas = queryset.filter(numero_cuenta__in=usuarios_con_semestre)
            return inscripciones_filtradas

class InscripcionAdmin(admin.ModelAdmin):
    list_display = ('get_apellido', 'get_nombre', 'get_asignaturas', 'get_grupos')

    def get_apellido(self, obj):
        return obj.numero_cuenta.last_name
    get_apellido.short_description = 'Apellido'
    get_apellido.admin_order_field = 'numero_cuenta__last_name'

    def get_nombre(self, obj):
        return obj.numero_cuenta.first_name
    get_nombre.short_description = 'Nombre'
    get_nombre.admin_order_field = 'numero_cuenta__first_name'

    def get_asignaturas(self, obj):
        return ", ".join([asignatura.denominacion for asignatura in obj.asignatura.all()])
    get_asignaturas.short_description = 'Asignaturas'

    def get_grupos(self, obj):
        # Iterar sobre los grupos y obtener el atributo clave de cada uno
        return ", ".join([str(grupo.clave_grupo) for grupo in obj.grupo.all()])
    get_grupos.short_description = 'Grupos'

    list_filter = (SemestreFilter,)
    actions = ['inscribir_usuarios']

    def inscribir_usuarios(self, request, queryset):
        # Obtener las asignaturas cuyo semestre sea 3
        asignaturas_a_inscribir = Asignatura.objects.filter(semestre=3)

        # Crear la inscripción para cada usuario seleccionado y asignar las asignaturas
        for usuario in queryset:
            inscripcion, created = Inscripcion.objects.get_or_create(numero_cuenta=usuario)
            inscripcion.asignatura.set(asignaturas_a_inscribir)

        self.message_user(request, f"Se ha realizado la inscripción para {queryset.count()} usuarios.")
    inscribir_usuarios.short_description = "Inscribir usuarios seleccionados"

    ordering = ['numero_cuenta__last_name']

admin.site.register(Inscripcion, InscripcionAdmin)
admin.site.register(Asignatura)
admin.site.register(Grupo)

class HistorialInscripcionAdmin(admin.ModelAdmin):
    list_display = ['numero_cuenta', 'periodo', 'fecha_inscripcion', 'activa', 'get_asignaturas_count', 'get_grupos_count']
    list_filter = ['activa', 'periodo', 'fecha_inscripcion']
    search_fields = ['numero_cuenta__numero_cuenta', 'numero_cuenta__first_name', 'numero_cuenta__last_name']
    readonly_fields = ['fecha_inscripcion', 'fecha_modificacion', 'asignaturas_snapshot', 'grupos_snapshot']
    ordering = ['-fecha_inscripcion']
    
    def get_asignaturas_count(self, obj):
        import json
        try:
            data = json.loads(obj.asignaturas_snapshot)
            return len(data)
        except:
            return 0
    get_asignaturas_count.short_description = 'Asignaturas'
    
    def get_grupos_count(self, obj):
        import json
        try:
            data = json.loads(obj.grupos_snapshot)
            return len(data)
        except:
            return 0
    get_grupos_count.short_description = 'Grupos'

admin.site.register(HistorialInscripcion, HistorialInscripcionAdmin)
