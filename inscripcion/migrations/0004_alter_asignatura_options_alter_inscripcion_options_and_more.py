# Generated by Django 4.1 on 2023-07-14 02:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscripcion', '0003_alter_inscripcion_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='asignatura',
            options={'ordering': ['semestre']},
        ),
        migrations.AlterModelOptions(
            name='inscripcion',
            options={'verbose_name': 'Inscripcion', 'verbose_name_plural': 'Inscripciones'},
        ),
        migrations.RemoveField(
            model_name='grupo',
            name='descripcion',
        ),
        migrations.AddField(
            model_name='grupo',
            name='semestre',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Primer Semestre'), (2, 'Segundo Semestre'), (3, 'Tercer Semestre'), (4, 'Cuarto Semestre'), (5, 'Quinto Semestre'), (6, 'Sexto Semestre'), (7, 'Séptimo Semestre'), (8, 'Octavo Semestre'), (9, 'Noveno Semestre')], default=None),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='asignatura',
            name='semestre',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Primer Semestre'), (2, 'Segundo Semestre'), (3, 'Tercer Semestre'), (4, 'Cuarto Semestre'), (5, 'Quinto Semestre'), (6, 'Sexto Semestre'), (7, 'Séptimo Semestre'), (8, 'Octavo Semestre'), (9, 'Noveno Semestre')]),
        ),
    ]
