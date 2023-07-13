from django.db import models
from users.models import User


class Asignatura(models.Model):
    clave_asignatura = models.SmallIntegerField(primary_key=True)
    denominacion = models.CharField(max_length=80)
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

    class Meta:
        ordering = ['semestre']
    def __str__(self):
        return self.denominacion


class Grupo(models.Model):
    clave_grupo = models.SmallIntegerField(primary_key=True)
    descripcion = models.CharField(max_length=100)
    asignaturas = models.ManyToManyField(
        Asignatura,
        related_name='asignaturas')

    def __str__(self):
        return str(self.clave_grupo)


class Inscripcion(models.Model):
    id = models.AutoField
    numero_cuenta = models.OneToOneField(User,
                                         on_delete=models.CASCADE,
                                         related_name='alumno')
    asignatura = models.ManyToManyField(Asignatura, blank=False)

    class Meta:
        verbose_name = 'Inscripcion'
        verbose_name_plural = 'Inscripciones'


    def __str__(self):
        return str(self.numero_cuenta)
        
