from django.db import models
from users.models import User
import json
from django.utils import timezone


class Asignatura(models.Model):
    clave_asignatura = models.SmallIntegerField(primary_key=True)
    denominacion = models.CharField(max_length=80)
    
    options = ((1,'Obligatoria'),
             (2,'Optativa'))
    
    caracter = models.PositiveSmallIntegerField(choices= options, default = 1)
    
    def get_caracter_display(self):
        return dict(self.options).get(self.caracter, '')
    opciones = (
        (0, 'Optativa'),
        (1, 'Primer Semestre'),
        (2, 'Segundo Semestre'),
        (3, 'Tercer Semestre'),
        (4, 'Cuarto Semestre'),
        (5, 'Quinto Semestre'),
        (6, 'Sexto Semestre'),
        (7, 'Séptimo Semestre'),
        (8, 'Octavo Semestre'),
        
    )
    semestre = models.PositiveSmallIntegerField(choices= opciones, default = 1)
    opciones_eje = ((1,'A'),
                    (2,'B'),
                    (3,'M'),
                    (4,'T')
                    )
    creditos = models.PositiveSmallIntegerField(default=0)
    eje = models.PositiveSmallIntegerField(choices= opciones_eje, default = 1)
  
    class Meta:
        ordering = ['semestre', 'clave_asignatura']
    def __str__(self):
        return f"{self.clave_asignatura} - {self.denominacion}"


class Grupo(models.Model):
    clave_grupo = models.SmallIntegerField(primary_key=True)
    opciones = (
        (1, 'Primer Semestre'),
        (2, 'Segundo Semestre'),
        (3, 'Tercer Semestre'),
        (4, 'Cuarto Semestre'),
        (5, 'Quinto Semestre'),
        (6, 'Sexto Semestre'),
        (7, 'Séptimo Semestre'),
        (8, 'Octavo Semestre'),
        (9, 'Noveno Semestre'),
    )
    semestre = models.PositiveSmallIntegerField(choices= opciones)
    asignaturas = models.ManyToManyField(Asignatura,related_name='asignaturas')
    
 

    def __str__(self):
        return str(self.clave_grupo)


# models.py

class Periodo(models.Model):
    codigo = models.CharField(max_length=7, unique=True)  # Ej. "2023-1", "2023-2"
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activo = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Desactivar los demás periodos
        if self.activo:
            Periodo.objects.exclude(pk=self.pk).update(activo=False)
        super(Periodo, self).save(*args, **kwargs)


    def __str__(self):
        return self.codigo

class Inscripcion(models.Model):
    id = models.AutoField(primary_key=True)
    numero_cuenta = models.OneToOneField(User,on_delete=models.CASCADE, related_name='alumno')
    asignatura = models.ManyToManyField(Asignatura, blank=False)
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, default=1)  # Asigna el id de un periodo existente
    grupo = models.ManyToManyField(Grupo, related_name='inscripciones')  # Mantener ManyToManyField
    


    class Meta:
        verbose_name = 'Inscripcion'
        verbose_name_plural = 'Inscripciones'
        unique_together = ('numero_cuenta', 'periodo')
      

    def __str__(self):
        return str(self.numero_cuenta)


class HistorialInscripcion(models.Model):
    """Modelo para mantener un historial completo de todas las inscripciones"""
    id = models.AutoField(primary_key=True)
    numero_cuenta = models.ForeignKey(User, on_delete=models.CASCADE, related_name='historial_inscripciones')
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    activa = models.BooleanField(default=True, help_text="Indica si esta inscripción está activa o fue reemplazada")
    
    # Campos para guardar snapshot de las materias y grupos al momento de la inscripción
    asignaturas_snapshot = models.TextField(blank=True, help_text="JSON con las asignaturas inscritas")
    grupos_snapshot = models.TextField(blank=True, help_text="JSON con los grupos asignados")
    
    class Meta:
        verbose_name = 'Historial de Inscripción'
        verbose_name_plural = 'Historial de Inscripciones'
        ordering = ['-fecha_inscripcion']
    
    def __str__(self):
        return f"{self.numero_cuenta} - {self.periodo} - {self.fecha_inscripcion.strftime('%d/%m/%Y %H:%M')}"
    
    def guardar_en_historial(self):
        """Guarda la inscripción actual en el historial antes de modificarla"""
        # Desactivar inscripciones anteriores del mismo período
        HistorialInscripcion.objects.filter(
            numero_cuenta=self.numero_cuenta,
            periodo=self.periodo
        ).update(activa=False)
        
        # Crear snapshot de asignaturas y grupos
        asignaturas_data = []
        for asignatura in self.asignatura.all():
            asignaturas_data.append({
                'clave': asignatura.clave_asignatura,
                'denominacion': asignatura.denominacion,
                'semestre': asignatura.semestre,
                'creditos': asignatura.creditos
            })
        
        grupos_data = []
        for grupo in self.grupo.all():
            grupos_data.append({
                'clave': grupo.clave_grupo,
                'semestre': grupo.semestre
            })
        
        # Crear registro en el historial
        historial = HistorialInscripcion.objects.create(
            numero_cuenta=self.numero_cuenta,
            periodo=self.periodo,
            asignaturas_snapshot=json.dumps(asignaturas_data, ensure_ascii=False),
            grupos_snapshot=json.dumps(grupos_data, ensure_ascii=False),
            activa=True
        )
        
        return historial