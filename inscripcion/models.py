from django.db import models

class Alumno(models.Model):
    numero_cuenta = models.IntegerField(primary_key= True)
    nombre = models.CharField(max_length=50, help_text= "Nombre o nombres")
    apellido_paterno = models.CharField(max_length=50, help_text= "Apellido Paterno")
    apellido_materno = models.CharField(max_length=50, help_text= "Apellido Materno") 
    edad = models.IntegerField(help_text="Edad")
    fecha_ingreso = models.DateField()
    semestre_actual = models.CharField(max_length=20)
    genero = [
        ('F', 'Femenino'),
        ('M', 'Masculino'),
        ('O', 'Otro'),]
    genero = models.CharField(max_length=1, choices=genero) 
    foto = models.ImageField(upload_to='fotos_alumnos/', null= True)
    

    def __str__(self):
        nombre_completo = "{0} {1} {2}"
        return nombre_completo.format(self.numero_cuenta,self.nombre,self.apellido_paterno,self.apellido_materno)
    
    
    
    

class Asignatura(models.Model):
    clave_asignatura = models.SmallIntegerField(primary_key=True)
    denominacion = models.CharField(max_length=80)
    semestre = models.PositiveIntegerField()
    creditos = models.PositiveIntegerField(default=None)
  
    
    def __str__(self):
        return self.denominacion
    




class Grupo(models.Model):
    clave_grupo = models.SmallIntegerField(primary_key= True)
    descripcion = models.CharField(max_length=100)
    asignaturas = models.ManyToManyField(Asignatura)

    def __str__(self):
        return str(self.clave_grupo)
    



class Inscripcion(models.Model):
    id = models.AutoField
    numero_cuenta = models.ForeignKey(Alumno, null=False, blank=False, on_delete=models.CASCADE)
    asignatura =models.ManyToManyField(Asignatura)
     

    def __str__(self):
        numero_de_cuenta = "{0}"
        return numero_de_cuenta.format(self.numero_cuenta)



    

    
    
    

    
   
    

