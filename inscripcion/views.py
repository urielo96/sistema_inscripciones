from django.http import HttpResponse
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.models import User
from inscripcion.models import Asignatura, Inscripcion, Grupo, Periodo
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
from django.views import View
from django.db.models import Q
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.platypus import Image
from django.templatetags.static import static
from datetime import datetime
import qrcode

from django.http import FileResponse
from django.template.loader import render_to_string
from django.utils.text import slugify


def user_authenticated(user):
    return user.is_authenticated


def is_alumno(user):
    return user.is_authenticated and user.groups.filter(name='Alumnos').exists()


@login_required
@user_passes_test(is_alumno, login_url='/users/login')
def index(request):
    # Obtener el alumno actualmente autenticado desde la sesión
    alumno = request.user
    numero_cuenta = alumno.numero_cuenta
    
    periodo = Periodo.objects.get(activo=True)

    # Obtener el semestre actual del alumno
    semestre_actual = alumno.semestre_actual
    
    # Obtener las asignaturas inscritas del usuario actual
    asignaturas_inscritas = alumno.alumno.asignatura.all()
    
    # Obtener todos los cursos que pertenecen al semestre actual del alumno
    cursos_listados = Asignatura.objects.filter(
        Q(semestre=semestre_actual) | Q(semestre=0))
    
    mostrar_boton_comprobante = False

    return render(request, "index.html", context={
        'cursos_listados': cursos_listados,
        'asignaturas_inscritas': asignaturas_inscritas,
        'mostrar_boton_comprobante': mostrar_boton_comprobante,
        'periodo': periodo,
    })


def redirect_to_login_if_expired(view_func):
    decorated_view_func = user_passes_test(
        user_authenticated, login_url='/users/login')(view_func)

    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.session.get_expiry_age() <= 0:
            return redirect('/users/login')
        return decorated_view_func(request, *args, **kwargs)

    return wrapper


index = redirect_to_login_if_expired(index)

@login_required
def inscribir_asignatura(request):
    if request.method == 'POST':
        asignatura_id = request.POST.get('asignatura_id')

        # Obtener el usuario actualmente autenticado
        usuario = request.user

        # Obtener la asignatura a partir del ID
        asignatura = Asignatura.objects.get(clave_asignatura=asignatura_id)

        # Obtener la instancia de Inscripcion del usuario
        inscripcion = usuario.alumno

        # Agregar la asignatura a la relación muchos a muchos utilizando el método set()
        inscripcion.asignatura.add(asignatura)

        return redirect('index')

@login_required
def eliminar_asignatura(request, asignatura_id):
    if request.method == 'POST':
        # Obtener el usuario actualmente autenticado
        usuario = request.user

        # Obtener la instancia de Inscripcion del usuario
        inscripcion = get_object_or_404(Inscripcion, numero_cuenta=usuario)

        # Obtener la asignatura a partir de la clave_asignatura
        asignatura = get_object_or_404(
            Asignatura, clave_asignatura=asignatura_id)

        # Verificar si la asignatura está en la relación muchos a muchos
        if asignatura in inscripcion.asignatura.all():
            # Eliminar la asignatura de la relación muchos a muchos utilizando el método remove()
            inscripcion.asignatura.remove(asignatura)

    return redirect('index')



def is_administrativo(user):
    return user.is_authenticated and user.groups.filter(name='Administrativos').exists()


@login_required
@user_passes_test(is_administrativo, login_url='/inscripcion/grupos')
def usuarios_inscritos_grupo(request):
    
    grupos = Grupo.objects.all()
    
    grupo_seleccionado = None
    usuarios_inscritos = []

    grupo_clave_str = request.GET.get('grupo', '')  # Obtener el valor del parámetro 'grupo' con un valor predeterminado de ''
    

    if grupo_clave_str:
        try:

            grupo_clave = int(grupo_clave_str)
            print(f' Es es el grupo que se le esta pasando para hacer la consulta {grupo_clave}')
            grupo_seleccionado = Grupo.objects.get(clave_grupo=grupo_clave)
            print(f' Este es el grupo seleccionado {grupo_seleccionado}')
            asignaturas_grupo = grupo_seleccionado.asignaturas.all()
            print(asignaturas_grupo)
            usuarios_inscritos = User.objects.filter(
                alumno__asignatura__in=asignaturas_grupo,
                alumno__grupo=grupo_seleccionado
            ).distinct()
            print(usuarios_inscritos)
        
        except (ValueError, Grupo.DoesNotExist):
            grupo_seleccionado = None  # Manejar el caso en que el grupo no existe o el valor no es un entero válido

    context = {
        'grupos': grupos,
        'grupo_seleccionado': grupo_seleccionado,
        'usuarios': usuarios_inscritos
    }

    return render(request, 'usuarios_inscritos_grupo.html', context)

@login_required
def generar_archivo_txt(request, grupo_clave):
    grupo_seleccionado = Grupo.objects.get(clave_grupo=grupo_clave)
    contenido = ""

    # Iterar sobre todas las asignaturas del grupo seleccionado
    for asignatura in grupo_seleccionado.asignaturas.all():
        # Aseguramos que la clave de la asignatura tenga siempre 4 dígitos con ceros a la izquierda
        clave_asignatura_padded = str(asignatura.clave_asignatura).zfill(4)
        clave_grupo_padded = str(grupo_seleccionado.clave_grupo).zfill(4)
        
        # Obtener todos los usuarios inscritos en la asignatura actual
        usuarios_inscritos = User.objects.filter(
            alumno__asignatura=asignatura,
            alumno__grupo=grupo_seleccionado
        ).distinct()

        # Generar una línea para cada usuario inscrito en la asignatura
        for usuario in usuarios_inscritos:
            linea = f"{usuario.numero_cuenta}2253{clave_asignatura_padded}{clave_grupo_padded}A\n"
            contenido += linea

    # Configurar la respuesta para la descarga del archivo
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="alumnos_grupo_general.txt"'
    response.write(contenido)

    return response



from django.shortcuts import render
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.lib.pagesizes import letter
from django.conf import settings
from reportlab.lib import utils
import os
from reportlab.platypus import SimpleDocTemplate, Image, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.platypus import Image
from io import BytesIO
import os
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Asignatura

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image
from io import BytesIO
import os
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Asignatura
from django.utils.html import escape

@login_required
def generar_comprobante(request, alumno_id):
    try:
        alumno_info = User.objects.get(numero_cuenta=alumno_id)
    except User.DoesNotExist:
        return HttpResponse("Alumno no encontrado", status=404)
    

    asignaturas_inscritas = Asignatura.objects.filter(inscripcion__numero_cuenta=alumno_info)
    periodo = Periodo.objects.get(activo = True)
    periodo = escape(str(periodo))
    


    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Obtener la ruta local de la imagen a la izquierda
    image_path_left = os.path.join(settings.BASE_DIR, 'static', 'img', 'logolcf.png')

    # Cargar la imagen a la izquierda
    logo_left = Image(image_path_left, width=50, height=70)
    logo_left.hAlign = 'LEFT'  # Alineamos la imagen a la izquierda

   

    image_path_right = os.path.join(settings.BASE_DIR, 'static', 'img', 'unam_logo_azul.png')

    # Cargar la imagen a la derecha
    logo_right = Image(image_path_right, width=60, height=70)
    logo_right.hAlign = 'RIGHT'  # Alineamos la imagen a la derecha

    

    # Agregar párrafos de texto en el encabezado del PDF
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=getSampleStyleSheet()['Title'],
        fontName='Helvetica-Bold',
        alignment=1,  # 0=Left, 1=Center, 2=Right
        fontSize=10
    )
    title_styles = ParagraphStyle(
        'TitleStyles',
        parent=getSampleStyleSheet()['Title'],
        fontName='Helvetica-Bold',
        alignment=1,  # 0=Left, 1=Center, 2=Right
        fontSize=11
    )
    datas = [
        [
            logo_left,  # Logotipo izquierdo
            Paragraph("UNIVERSIDAD NACIONAL AUTÓNOMA DE MÉXICO<br/>ESCUELA NACIONAL DE CIENCIAS FORENSES<br/>SECRETARÍA DE SERVICIOS ESCOLARES", title_styles),
            logo_right,  # Logotipo derecho

        ]
    ]
    table = Table(datas, colWidths=[60, 300, 60])
    
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
    ]))
    elements.append(table)

    # Agregar título "Comprobante de Inscripción"
    elements.append(Paragraph(" ", title_style))
    elements.append(Paragraph(" ", title_style))
    
    title = Paragraph("Comprobante de Inscripción", title_style)
    elements.append(title)

    # Crear una tabla para mostrar los elementos en la misma línea
    styles = getSampleStyleSheet()
    data = [
    [
        Paragraph("<b>Nombre del alumno:</b>", styles['Normal']),
        Paragraph(f"{alumno_info.first_name} {alumno_info.last_name}", styles['Normal']),
    ],
    [
        Paragraph("<b>Número de cuenta:</b>", styles['Normal']),
        Paragraph(f"{alumno_info.numero_cuenta}", styles['Normal']),
    ],
    [
        Paragraph("<b>Plan:</b>", styles['Normal']),
        Paragraph("2253", styles['Normal']),  # Aquí puedes poner el valor del plan si es dinámico
    ],
    [
        Paragraph("<b>Periodo:</b>", styles['Normal']),
        Paragraph(periodo, styles['Normal']),  # Aquí puedes poner el valor del periodo si es dinámico
    ],
    [
        Paragraph("<b>Semestre:</b>", styles['Normal']),
        Paragraph(f"{alumno_info.semestre_actual}", styles['Normal']),  # Aquí puedes poner el valor del periodo si es dinámico
    ],
]
    table = Table(data, colWidths=[210,210])
    
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
    ]))

    
    elements.append(table)
    elements.append(Paragraph(" ", title_style))
    elements.append(Paragraph(" ", title_style))

    data = [["Clave", "Denominación", "Créditos"]]
    for asignatura in asignaturas_inscritas:
        data.append([str(asignatura.clave_asignatura).zfill(4), asignatura.denominacion, asignatura.creditos])

    table = Table(data, colWidths=[60,300,60])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
    
    # Asignar el ancho calculado a la tabla
    
    elements.append(table)

    
      # Obtener la fecha y hora actual
    now = datetime.now()
    elements.append(Paragraph(" ", title_style))
    elements.append(Paragraph(" ", title_style))
    formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")

    
    # Crear el estilo para el párrafo de la fecha y hora
    date_style = ParagraphStyle(
    'DateStyle',
    parent=getSampleStyleSheet()['Normal'],
    fontName='Helvetica',
    leftIndent=20  # Agregamos el margen izquierdo de 20 puntos
)

    # Agregar la fecha y hora al PDF
    date_paragraph = Paragraph(f"<b>Fecha y hora de consulta:</b> {formatted_date}", date_style)
    date_paragraph.leftIndent = 100
    elements.append(date_paragraph)

   # ... (resto de tu código)

# Crear el código QR con la información del alumno y la URL de la vista de validación
    validation_url = reverse('validacion_alumno', args=[alumno_info.numero_cuenta])
    qr_data =f"{request.build_absolute_uri(validation_url)}"


    # ... (resto de tu código)


    # Agregar título "Código QR"
    elements.append(Paragraph(" ", title_style))
    elements.append(Paragraph(" ", title_style))
    
    qr_title = Paragraph("ESCUELA NACIONAL DE CIENCIAS FORENSES", title_style)
    elements.append(qr_title)

    # Crear código QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    # Crear una imagen del código QR
    qr_image = qr.make_image(fill_color="black", back_color="white")
    
    # Guardar la imagen del código QR en un buffer
    qr_image_buffer = BytesIO()
    qr_image.save(qr_image_buffer)
    
    # Regresar al inicio del buffer antes de escribir
    qr_image_buffer.seek(0)
    
    # Crear la imagen del código QR para reportlab
    qr_code = Image(qr_image_buffer, width=100, height=100)
    qr_code.hAlign = 'CENTER'
    elements.append(qr_code)

    doc.build(elements)

  
    # Obtener el contenido del PDF generado
    pdf_content = buffer.getvalue()
    buffer.close()

    # Devolver el contenido del PDF en la respuesta HTTP
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Comprobante-{alumno_info.numero_cuenta}.pdf"'
    response.write(pdf_content)
    return response


def validacion_alumno(request, alumno_id):
    try:
        alumno_info = User.objects.get(numero_cuenta=alumno_id)
        periodo = Periodo.objects.get(activo=True)
    except User.DoesNotExist:
        return HttpResponse("Alumno no encontrado", status=404)
    

    asignaturas_inscritas = Asignatura.objects.filter(inscripcion__numero_cuenta=alumno_info)

    return render(request, 'validacion_alumno_template.html', {'alumno_info': alumno_info,},{periodo: periodo})
