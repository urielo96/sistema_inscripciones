from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    numero_cuenta = models.CharField(max_length=10, unique=True, null=False)
    email_requerido = models.EmailField(max_length=254, blank=True, null=True, help_text="Email del alumno")
    email_completado = models.BooleanField(default=False, help_text="Indica si el alumno ya proporcionó su email")
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
    semestre_actual = models.IntegerField(choices=opciones, default=1)

    USERNAME_FIELD = 'numero_cuenta'
    REQUIRED_FIELDS = ['username','password']
    
    class Meta:
        verbose_name = 'Alumnos'
        verbose_name_plural = 'Alumnos'
    

    def __str__(self):
        return f' {self.last_name} {self.first_name},{self.numero_cuenta}'