from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    numero_cuenta = models.CharField(max_length=9, unique=True, null=False)
    semestre_actual = models.IntegerField(null=True)
    USERNAME_FIELD = 'numero_cuenta'
    REQUIRED_FIELDS = ['username','password']

    

    def __str__(self):
        return f'{self.first_name},{self.numero_cuenta}'