from io import BytesIO
import openpyxl
from django.db.models import Q
from .forms import UsuarioForm
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.auth.models import Group
from django.utils.timezone import localtime
from xhtml2pdf import pisa
from gestion_activos.utils.decoradores import grupo_requerido
# your app
from gestion_activos.forms import (
    ActivoForm, CategoriaForm, UbicacionForm, UsuarioForm
)
from gestion_activos.models import Categoria, Ubicacion, Activo
from django.core.mail import send_mail
from django.conf import settings


def es_admin_sistema(user):
    return user.groups.filter(name='Administrador del Sistema').exists()
# --- CRUD permisos de grupo ---
@login_required
@grupo_requerido('Administrador')
def lista_usuarios(request):
    busqueda = request.GET.get('busqueda', '').strip()
    usuarios = User.objects.all()
    if busqueda:
        usuarios = usuarios.filter(
            Q(username__icontains=busqueda) | Q(email__icontains=busqueda)
        )
    return render(request, 'gestion_activos/lista_usuarios.html', {
        'usuarios': usuarios,
    })

@login_required
@grupo_requerido('Administrador')
def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if form.cleaned_data['password']:
                user.set_password(form.cleaned_data['password'])
            user.save()
            grupo = form.cleaned_data['grupo']
            user.groups.set([grupo])
            return redirect('lista_usuarios')
    else:
        form = UsuarioForm()
    return render(request, 'gestion_activos/usuario_form.html', {'form': form, 'titulo': 'Crear Usuario'})

@login_required
@grupo_requerido('Administrador')
def editar_usuario(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            if form.cleaned_data['password']:
                user.set_password(form.cleaned_data['password'])
            user.save()
            grupo = form.cleaned_data['grupo']
            user.groups.set([grupo])
            return redirect('lista_usuarios')
    else:
        form = UsuarioForm(instance=user)
        if user.groups.exists():
            form.fields['grupo'].initial = user.groups.first()
    return render(request, 'gestion_activos/usuario_form.html', {'form': form, 'titulo': 'Editar Usuario'})

@login_required
@grupo_requerido('Administrador')
def eliminar_usuario(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        return redirect('lista_usuarios')
    return render(request, 'gestion_activos/usuario_confirm_delete.html', {'obj': user})

def sin_permisos(request):
    return render(request, 'gestion_activos/sin_permisos.html')

# --- CRUD login ---
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next') or 'lista_activos'
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'gestion_activos/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# --- CRUD Activos ---
@login_required
def lista_activos(request):
    activos = Activo.objects.select_related('categoria', 'ubicacion').all()
    categorias = Categoria.objects.all()
    ubicaciones = Ubicacion.objects.all()

    estado = request.GET.get('estado')
    categoria_id = request.GET.get('categoria')
    ubicacion_id = request.GET.get('ubicacion')

    if estado:
        activos = activos.filter(estado=estado)
    if categoria_id:
        activos = activos.filter(categoria_id=categoria_id)
    if ubicacion_id:
        activos = activos.filter(ubicacion_id=ubicacion_id)

    return render(request, 'gestion_activos/lista_activos.html', {
        'activos': activos,
        'categorias': categorias,
        'ubicaciones': ubicaciones,
        'estado_seleccionado': estado,
        'categoria_seleccionada': categoria_id,
        'ubicacion_seleccionada': ubicacion_id
    })
    # Verificación de grupo para mostrar botones de acciones
    es_admin = request.user.groups.filter(name="Administrador").exists()

    return render(request, 'gestion_activos/lista_activos.html', {
        'activos': activos,
        'categorias': categorias,
        'ubicaciones': ubicaciones,
        'estado_seleccionado': estado,
        'categoria_seleccionada': categoria_id,
        'ubicacion_seleccionada': ubicacion_id,
        'categoria_nombre': categoria_nombre,
        'ubicacion_nombre': ubicacion_nombre,
        'es_admin': es_admin,
    })

@login_required
@grupo_requerido("Técnico", "Administrador")
def registrar_activo(request):
    if request.method == 'POST':
        form = ActivoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_activos')
    else:
        form = ActivoForm()
    return render(request, 'gestion_activos/activo_form.html', {
        'form': form,
        'titulo': 'Registrar Activo'
    })

@login_required
@grupo_requerido("Técnico", "Administrador")
def editar_activo(request, pk):
    activo = get_object_or_404(Activo, pk=pk)
    if request.method == 'POST':
        form = ActivoForm(request.POST, instance=activo)
        if form.is_valid():
            form.save()
            return redirect('lista_activos')
    else:
        form = ActivoForm(instance=activo)
    return render(request, 'gestion_activos/activo_form.html', {
        'form': form,
        'titulo': f'Editar Activo: {activo.nombre}'
    })

@login_required
@grupo_requerido("Técnico", "Administrador")
def eliminar_activo(request, pk):
    activo = get_object_or_404(Activo, pk=pk)
    if request.method == 'POST':
        activo.delete()
        return redirect('lista_activos')
    return render(request, 'gestion_activos/activo_confirm_delete.html', {
        'obj': activo
    })


# --- CRUD Categorías ---
@login_required
@grupo_requerido('Administrador')
def lista_categorias(request):
    query = request.GET.get('busqueda', '')
    categorias = Categoria.objects.all()
    if query:
        categorias = categorias.filter(nombre__icontains=query)
    return render(request, 'gestion_activos/lista_categorias.html', {
        'categorias': categorias,
        'busqueda': query,
    })

@login_required
@grupo_requerido('Administrador')
def crear_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_categorias')
    else:
        form = CategoriaForm()
    return render(request, 'gestion_activos/categoria_form.html', {'form': form, 'titulo': 'Crear Categoría'})

@login_required
@grupo_requerido("Administrador")
def editar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            return redirect('lista_categorias')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'gestion_activos/categoria_form.html', {'form': form, 'titulo': 'Editar Categoría'})


@login_required
@grupo_requerido('Administrador')
def eliminar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        categoria.delete()
        return redirect('lista_categorias')
    return render(request, 'gestion_activos/categoria_confirm_delete.html', {'obj': categoria})


# --- CRUD Ubicaciones ---
@login_required
@grupo_requerido('Administrador')
def lista_ubicaciones(request):
    query = request.GET.get('busqueda', '')
    ubicaciones = Ubicacion.objects.all()
    if query:
        ubicaciones = ubicaciones.filter(nombre__icontains=query)
    return render(request, 'gestion_activos/lista_ubicaciones.html', {
        'ubicaciones': ubicaciones,
        'busqueda': query,
    })


@login_required
@grupo_requerido('Administrador')
def crear_ubicacion(request):
    if request.method == 'POST':
        form = UbicacionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_ubicaciones')
    else:
        form = UbicacionForm()
    return render(request, 'gestion_activos/ubicacion_form.html', {'form': form, 'titulo': 'Crear Ubicación'})


@login_required
@grupo_requerido("Administrador")
def editar_ubicacion(request, pk):
    ubicacion = get_object_or_404(Ubicacion, pk=pk)
    if request.method == 'POST':
        form = UbicacionForm(request.POST, instance=ubicacion)
        if form.is_valid():
            form.save()
            return redirect('lista_ubicaciones')
    else:
        form = UbicacionForm(instance=ubicacion)
    return render(request, 'gestion_activos/ubicacion_form.html', {'form': form, 'titulo': 'Editar Ubicación'})


@login_required
@grupo_requerido("Administrador")
def eliminar_ubicacion(request, pk):
    ubicacion = get_object_or_404(Ubicacion, pk=pk)
    if request.method == 'POST':
        ubicacion.delete()
        return redirect('lista_ubicaciones')
    return render(request, 'gestion_activos/ubicacion_confirm_delete.html', {'obj': ubicacion})


# --- Reportes PDF ---
@login_required
@grupo_requerido("Auditor", "Administrador")
def reporte_pdf(request):
    activos = Activo.objects.select_related('categoria', 'ubicacion').all()

    estado = request.GET.get('estado')
    categoria_id = request.GET.get('categoria')
    ubicacion_id = request.GET.get('ubicacion')

    if estado:
        activos = activos.filter(estado=estado)
    if categoria_id:
        try:
            activos = activos.filter(categoria_id=int(categoria_id))
        except ValueError:
            pass
    if ubicacion_id:
        try:
            activos = activos.filter(ubicacion_id=int(ubicacion_id))
        except ValueError:
            pass

    context = {'activos': activos}
    html_string = render_to_string('gestion_activos/reporte_pdf.html', context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_activos_filtrados.pdf"'

    pisa_status = pisa.CreatePDF(html_string, dest=response)
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)
    return response

# --- Exportar a Excel ---
@login_required
@grupo_requerido("Auditor", "Administrador")
def exportar_excel(request):
    estado = request.GET.get('estado')
    categoria_id = request.GET.get('categoria')
    ubicacion_id = request.GET.get('ubicacion')

    activos = Activo.objects.select_related('categoria', 'ubicacion').all()

    if estado:
        activos = activos.filter(estado=estado)
    if categoria_id:
        try:
            activos = activos.filter(categoria_id=int(categoria_id))
        except ValueError:
            pass
    if ubicacion_id:
        try:
            activos = activos.filter(ubicacion_id=int(ubicacion_id))
        except ValueError:
            pass

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Activos"
    ws.append(['Código', 'Nombre', 'Descripción', 'Categoría', 'Ubicación', 'Estado', 'Fecha de Registro'])

    for activo in activos:
        ws.append([
            activo.codigo,
            activo.nombre,
            activo.descripcion,
            activo.categoria.nombre if activo.categoria else '',
            activo.ubicacion.nombre if activo.ubicacion else '',
            activo.get_estado_display(),
            str(activo.fecha_registro)
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="activos_filtrados.xlsx"'
    wb.save(response)
    return response


def contacto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        mensaje = request.POST.get('mensaje')

        send_mail(
            subject=f'Nuevo mensaje de {nombre}',
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,  # tomado desde settings
            recipient_list=['destinatario@dominio.com'],
            fail_silently=False
        )

        return HttpResponse("Correo enviado correctamente")
    return render(request, 'formulario_contacto.html')