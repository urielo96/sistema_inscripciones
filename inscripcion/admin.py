from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib import admin
from users.models import User  # Asegúrate de importar el modelo User de la aplicación 'users'
from .models import Asignatura, Inscripcion

from django.contrib import admin
from inscripcion.models import Inscripcion

class InscripcionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'get_asignaturas')

    def get_asignaturas(self, obj):
        return ", ".join([asignatura.denominacion for asignatura in obj.asignatura.all()])

    get_asignaturas.short_description = 'Asignaturas'

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

admin.site.register(Inscripcion, InscripcionAdmin)


admin.site.register(Asignatura)



