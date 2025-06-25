from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.conf import settings
from .models import Activo, Categoria, Ubicacion, LogAccion, Perfil
from .forms import (
    LoginForm, ActivoForm, CategoriaForm, UbicacionForm,
    UsuarioForm, UsuarioActivoForm, PerfilForm
)
from .utils.decoradores import grupo_requerido
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse


# ==============================================================================
# VISTAS DE ÍNDICE Y AUTENTICACIÓN
# ==============================================================================
@login_required
def index_view(request):
    user = request.user
    roles_staff = ['Administrador', 'Supervisor', 'Técnico', 'Auditor']
    if user.is_superuser or user.is_staff or user.groups.filter(name__in=roles_staff).exists():
        return redirect('lista_activos')
    elif user.groups.filter(name='Usuario').exists():
        return redirect('mis_activos')
    else:
        return redirect('login')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(request, **form.cleaned_data)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenido de nuevo, {user.username}!')
                return redirect('index')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
    return render(request, 'gestion_activos/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')

@login_required
def sin_permisos(request):
    return render(request, 'gestion_activos/sin_permisos.html')
# ==============================================================================
# VISTAS PARA EL ROL "USUARIO" Y SU PERFIL
# ==============================================================================

@login_required
@grupo_requerido('Usuario')
def mis_activos(request):
    activos = Activo.objects.filter(responsable=request.user).select_related('categoria', 'ubicacion')
    return render(request, 'gestion_activos/mis_activos.html', {'activos': activos})

@login_required
def completar_perfil(request):
    if request.user.perfil.info_personal_confirmada:
        return redirect('mis_activos')
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=request.user.perfil)
        if form.is_valid():
            perfil = form.save(commit=False)
            perfil.info_personal_confirmada = True
            perfil.save()
            messages.success(request, '¡Gracias por completar tu perfil!')
            return redirect('mis_activos')
    else:
        form = PerfilForm(instance=request.user.perfil)
    return render(request, 'gestion_activos/completar_perfil.html', {'form': form})

@login_required
def ver_perfil(request):
    if request.method == 'POST':
        password_form = PasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, '¡Tu contraseña ha sido actualizada!')
            return redirect('ver_perfil')
    else:
        password_form = PasswordChangeForm(request.user)
    return render(request, 'gestion_activos/perfil.html', {'password_form': password_form})

@login_required
@grupo_requerido('Administrador', 'Supervisor', 'Técnico', 'Auditor')
def editar_perfil_staff(request):
    """
    Vista para que el personal administrativo (staff) complete o edite
    su propia información de perfil, manteniéndose dentro del layout
    de administración.
    """
    # Se obtiene el perfil del usuario logueado.
    # Se añade un try/except para el caso extremo de que no exista.
    try:
        perfil = request.user.perfil
    except Perfil.DoesNotExist:
        # Si por alguna razón el perfil no se creó con la señal, se crea aquí.
        perfil = Perfil.objects.create(user=request.user)

    if request.method == 'POST':
        # Si se envía el formulario, se procesa con los datos enviados.
        form = PerfilForm(request.POST, instance=perfil)
        if form.is_valid():
            instancia_perfil = form.save(commit=False)

            # Se marca la bandera para que el middleware no lo vuelva a pedir.
            instancia_perfil.info_personal_confirmada = True
            instancia_perfil.save()

            messages.success(request, '¡Tu información de perfil ha sido guardada correctamente!')

            # Se redirige al dashboard principal de administración.
            return redirect('lista_activos')
    else:
        # Si es una petición GET, se muestra el formulario con los datos actuales del perfil.
        form = PerfilForm(instance=perfil)

    context = {
        'form': form,
        'titulo': 'Completar / Editar Mi Perfil'
    }
    # Renderiza la plantilla diseñada para el layout de administración.
    return render(request, 'gestion_activos/perfil_staff_form.html', context)
# --- Vistas Principales (Dashboards) ---

@login_required
@grupo_requerido('Administrador', 'Supervisor', 'Técnico', 'Auditor')
def lista_activos(request):
    """Muestra la lista general de todos los activos con filtros."""
    # Lógica de filtrado...
    activos = Activo.objects.all()
    return render(request, 'gestion_activos/lista_activos.html', {'activos': activos})
# --- CRUD de Activos ---
@login_required
@grupo_requerido("Técnico", "Administrador")
def registrar_activo(request):
    """Muestra el formulario para registrar un nuevo activo."""
    if request.method == 'POST':
        form = ActivoForm(request.POST)
        if form.is_valid():
            nuevo_activo = form.save()
            LogAccion.objects.create(
                usuario=request.user,
                accion=LogAccion.ACCION_CREACION,
                content_type=ContentType.objects.get_for_model(nuevo_activo),
                object_id=nuevo_activo.id,
                detalles=f'Se registró el activo: {nuevo_activo.nombre}'
            )
            messages.success(request, 'Activo registrado correctamente.')
            return redirect('lista_activos')
    else:
        form = ActivoForm()
    return render(request, 'gestion_activos/activo_form.html', {
        'form': form,
        'titulo': 'Registrar Activo'
    })


@login_required
@grupo_requerido("Técnico", "Administrador", "Usuario")
def editar_activo(request, pk):
    """Permite editar un activo, con lógica de permisos por rol."""
    activo = get_object_or_404(Activo, pk=pk)
    es_usuario_regular = request.user.groups.filter(name='Usuario').exists()

    # Verificación de seguridad: un usuario regular solo puede editar sus propios activos.
    if es_usuario_regular and activo.responsable != request.user:
        messages.error(request, 'No tiene permiso para editar este activo.')
        return redirect('sin_permisos')

    # Se elige el formulario adecuado según el rol del usuario.
    FormularioAUsar = UsuarioActivoForm if es_usuario_regular else ActivoForm

    if request.method == 'POST':
        form = FormularioAUsar(request.POST, instance=activo)
        if form.is_valid():
            activo_actualizado = form.save()
            LogAccion.objects.create(
                usuario=request.user,
                accion=LogAccion.ACCION_ACTUALIZACION,
                content_type=ContentType.objects.get_for_model(activo_actualizado),
                object_id=activo_actualizado.id,
                detalles=f'Se actualizó el activo: {activo_actualizado.nombre}'
            )
            messages.success(request, 'Activo actualizado correctamente.')
            return redirect('mis_activos' if es_usuario_regular else 'lista_activos')
    else:
        form = FormularioAUsar(instance=activo)

    return render(request, 'gestion_activos/activo_form.html', {
        'form': form,
        'titulo': f'Editar Activo: {activo.nombre}'
    })


@login_required
@grupo_requerido("Administrador")
def eliminar_activo(request, pk):
    """Elimina un activo del sistema."""
    activo = get_object_or_404(Activo, pk=pk)
    if request.method == 'POST':
        LogAccion.objects.create(
            usuario=request.user,
            accion=LogAccion.ACCION_ELIMINACION,
            content_type=ContentType.objects.get_for_model(activo),
            object_id=activo.id,
            detalles=f'Se eliminó el activo: {activo.nombre}'
        )
        activo.delete()
        messages.success(request, 'Activo eliminado correctamente.')
        return redirect('lista_activos')
    return render(request, 'gestion_activos/activo_confirm_delete.html', {'object': activo})


# --- CRUD de Categorías ---

@login_required
@grupo_requerido('Administrador')
def lista_categorias(request):
    """Muestra una lista de todas las categorías."""
    query = request.GET.get('busqueda', '')
    categorias = Categoria.objects.all()
    if query:
        categorias = categorias.filter(nombre__icontains=query)
    return render(request, 'gestion_activos/lista_categorias.html', {'categorias': categorias})


@login_required
@grupo_requerido('Administrador')
def crear_categoria(request):
    """Crea una nueva categoría."""
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            nueva_categoria = form.save()
            LogAccion.objects.create(
                usuario=request.user,
                accion=LogAccion.ACCION_CREACION,
                content_type=ContentType.objects.get_for_model(nueva_categoria),
                object_id=nueva_categoria.id,
                detalles=f'Se creó la categoría: {nueva_categoria.nombre}'
            )
            messages.success(request, 'Categoría creada correctamente.')
            return redirect('lista_categorias')
    else:
        form = CategoriaForm()
    return render(request, 'gestion_activos/categoria_form.html', {'form': form})


@login_required
@grupo_requerido("Administrador")
def editar_categoria(request, pk):
    """Edita una categoría existente."""
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            categoria_actualizada = form.save()
            LogAccion.objects.create(
                usuario=request.user,
                accion=LogAccion.ACCION_ACTUALIZACION,
                content_type=ContentType.objects.get_for_model(categoria_actualizada),
                object_id=categoria_actualizada.id,
                detalles=f'Se actualizó la categoría: {categoria_actualizada.nombre}'
            )
            messages.success(request, 'Categoría actualizada correctamente.')
            return redirect('lista_categorias')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'gestion_activos/categoria_form.html', {'form': form})


@login_required
@grupo_requerido('Administrador')
def eliminar_categoria(request, pk):
    """Elimina una categoría."""
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        LogAccion.objects.create(
            usuario=request.user,
            accion=LogAccion.ACCION_ELIMINACION,
            content_type=ContentType.objects.get_for_model(categoria),
            object_id=categoria.id,
            detalles=f'Se eliminó la categoría: {categoria.nombre}'
        )
        categoria.delete()
        messages.success(request, 'Categoría eliminada correctamente.')
        return redirect('lista_categorias')
    return render(request, 'gestion_activos/categoria_confirm_delete.html', {'object': categoria})


# --- CRUD de Ubicaciones ---

@login_required
@grupo_requerido('Administrador')
def lista_ubicaciones(request):
    """Muestra una lista de todas las ubicaciones."""
    query = request.GET.get('busqueda', '')
    ubicaciones = Ubicacion.objects.all()
    if query:
        ubicaciones = ubicaciones.filter(nombre__icontains=query)
    return render(request, 'gestion_activos/lista_ubicaciones.html', {'ubicaciones': ubicaciones})


@login_required
@grupo_requerido('Administrador')
def crear_ubicacion(request):
    """Crea una nueva ubicación."""
    if request.method == 'POST':
        form = UbicacionForm(request.POST)
        if form.is_valid():
            nueva_ubicacion = form.save()
            LogAccion.objects.create(
                usuario=request.user,
                accion=LogAccion.ACCION_CREACION,
                content_type=ContentType.objects.get_for_model(nueva_ubicacion),
                object_id=nueva_ubicacion.id,
                detalles=f'Se creó la ubicación: {nueva_ubicacion.nombre}'
            )
            messages.success(request, 'Ubicación creada correctamente.')
            return redirect('lista_ubicaciones')
    else:
        form = UbicacionForm()
    return render(request, 'gestion_activos/ubicacion_form.html', {'form': form})


@login_required
@grupo_requerido("Administrador")
def editar_ubicacion(request, pk):
    """Edita una ubicación existente."""
    ubicacion = get_object_or_404(Ubicacion, pk=pk)
    if request.method == 'POST':
        form = UbicacionForm(request.POST, instance=ubicacion)
        if form.is_valid():
            ubicacion_actualizada = form.save()
            LogAccion.objects.create(
                usuario=request.user,
                accion=LogAccion.ACCION_ACTUALIZACION,
                content_type=ContentType.objects.get_for_model(ubicacion_actualizada),
                object_id=ubicacion_actualizada.id,
                detalles=f'Se actualizó la ubicación: {ubicacion_actualizada.nombre}'
            )
            messages.success(request, 'Ubicación actualizada correctamente.')
            return redirect('lista_ubicaciones')
    else:
        form = UbicacionForm(instance=ubicacion)
    return render(request, 'gestion_activos/ubicacion_form.html', {'form': form})


@login_required
@grupo_requerido("Administrador")
def eliminar_ubicacion(request, pk):
    """Elimina una ubicación."""
    ubicacion = get_object_or_404(Ubicacion, pk=pk)
    if request.method == 'POST':
        LogAccion.objects.create(
            usuario=request.user,
            accion=LogAccion.ACCION_ELIMINACION,
            content_type=ContentType.objects.get_for_model(ubicacion),
            object_id=ubicacion.id,
            detalles=f'Se eliminó la ubicación: {ubicacion.nombre}'
        )
        ubicacion.delete()
        messages.success(request, 'Ubicación eliminada correctamente.')
        return redirect('lista_ubicaciones')
    return render(request, 'gestion_activos/ubicacion_confirm_delete.html', {'object': ubicacion})


# --- CRUD de Usuarios ---

@login_required
@grupo_requerido('Administrador')
def lista_usuarios(request):
    """Muestra una lista de todos los usuarios del sistema."""
    busqueda = request.GET.get('busqueda', '').strip()
    usuarios = User.objects.all()
    if busqueda:
        usuarios = usuarios.filter(Q(username__icontains=busqueda) | Q(email__icontains=busqueda))
    return render(request, 'gestion_activos/lista_usuarios.html', {'usuarios': usuarios})


@login_required
@grupo_requerido('Administrador')
def crear_usuario(request):
    """Crea un nuevo usuario y le asigna un grupo/rol."""
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            nuevo_usuario = form.save()
            LogAccion.objects.create(
                usuario=request.user,
                accion=LogAccion.ACCION_CREACION,
                content_type=ContentType.objects.get_for_model(nuevo_usuario),
                object_id=nuevo_usuario.id,
                detalles=f'Se creó el usuario: {nuevo_usuario.username}'
            )
            messages.success(request, 'Usuario creado correctamente.')
            return redirect('lista_usuarios')
    else:
        form = UsuarioForm()
    return render(request, 'gestion_activos/usuario_form.html', {'form': form})


@login_required
@grupo_requerido('Administrador')
def editar_usuario(request, pk):
    """Edita los datos y el rol de un usuario existente."""
    usuario_a_editar = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario_a_editar)
        if form.is_valid():
            usuario_actualizado = form.save()
            LogAccion.objects.create(
                usuario=request.user,
                accion=LogAccion.ACCION_ACTUALIZACION,
                content_type=ContentType.objects.get_for_model(usuario_actualizado),
                object_id=usuario_actualizado.id,
                detalles=f'Se actualizó el usuario: {usuario_actualizado.username}'
            )
            messages.success(request, 'Usuario actualizado correctamente.')
            return redirect('lista_usuarios')
    else:
        form = UsuarioForm(instance=usuario_a_editar)
    return render(request, 'gestion_activos/usuario_form.html', {'form': form})


@login_required
@grupo_requerido('Administrador')
def eliminar_usuario(request, pk):
    """Elimina un usuario del sistema."""
    usuario_a_eliminar = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        LogAccion.objects.create(
            usuario=request.user,
            accion=LogAccion.ACCION_ELIMINACION,
            content_type=ContentType.objects.get_for_model(usuario_a_eliminar),
            object_id=usuario_a_eliminar.id,
            detalles=f'Se eliminó al usuario: {usuario_a_eliminar.username}'
        )
        usuario_a_eliminar.delete()
        messages.success(request, 'Usuario eliminado correctamente.')
        return redirect('lista_usuarios')
    return render(request, 'gestion_activos/usuario_confirm_delete.html', {'object': usuario_a_eliminar})


# --- Vistas de Reportes ---

@login_required
@grupo_requerido("Auditor", "Administrador")
def reporte_pdf(request):
    """Genera y descarga un reporte en PDF de los activos (con filtros)."""
    # Esta lógica de filtrado es la misma que en lista_activos y exportar_excel.
    # Se podría refactorizar a una función auxiliar si crece en complejidad.
    activos = Activo.objects.select_related('categoria', 'ubicacion').all()
    estado = request.GET.get('estado')
    categoria_id = request.GET.get('categoria')
    ubicacion_id = request.GET.get('ubicacion')

    if estado:
        activos = activos.filter(estado=estado)
    if categoria_id:
        activos = activos.filter(categoria_id=categoria_id)
    if ubicacion_id:
        activos = activos.filter(ubicacion_id=ubicacion_id)

    context = {'activos': activos}
    html_string = render_to_string('gestion_activos/reporte_pdf.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_activos.pdf"'

    pisa_status = pisa.CreatePDF(html_string, dest=response)
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF.', status=500)
    return response


@login_required
@grupo_requerido("Auditor", "Administrador", "Supervisor")
def exportar_excel(request):
    """Genera y descarga un reporte en Excel de los activos (con filtros)."""
    activos = Activo.objects.select_related('categoria', 'ubicacion').all()
    estado = request.GET.get('estado')
    categoria_id = request.GET.get('categoria')
    ubicacion_id = request.GET.get('ubicacion')

    if estado:
        activos = activos.filter(estado=estado)
    if categoria_id:
        activos = activos.filter(categoria_id=categoria_id)
    if ubicacion_id:
        activos = activos.filter(ubicacion_id=ubicacion_id)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Activos"
    ws.append(
        ['Código', 'Nombre', 'Descripción', 'Categoría', 'Ubicación', 'Estado', 'Responsable', 'Fecha de Registro'])

    for activo in activos:
        ws.append([
            activo.codigo,
            activo.nombre,
            activo.descripcion,
            activo.categoria.nombre if activo.categoria else '',
            activo.ubicacion.nombre if activo.ubicacion else '',
            activo.get_estado_display(),
            activo.responsable.username if activo.responsable else '',
            activo.fecha_registro.strftime("%d/%m/%Y %H:%M") if activo.fecha_registro else ''
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="reporte_activos.xlsx"'
    wb.save(response)
    return response


# --- Otras Vistas ---

@login_required
@grupo_requerido("Auditor", "Administrador")
def vista_bitacora(request):
    """Muestra la bitácora de acciones del sistema."""
    logs = LogAccion.objects.select_related('usuario', 'content_type').all().order_by('-timestamp')
    return render(request, 'gestion_activos/vista_bitacora.html', {'logs': logs})


def contacto(request):
    """Muestra y procesa el formulario de contacto."""
    if request.method == 'POST':
        nombre = request.POST.get('nombre', 'Anónimo')
        mensaje = request.POST.get('mensaje', '')
        email_remitente = request.POST.get('email', '')

        mensaje_completo = f"Mensaje de: {nombre} ({email_remitente})\n\n{mensaje}"

        send_mail(
            subject=f'Nuevo mensaje de contacto desde el sistema',
            message=mensaje_completo,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_CONTACTO],  # Se recomienda definir esta variable en settings.py
            fail_silently=False
        )
        messages.success(request, 'Tu mensaje ha sido enviado correctamente. Gracias por contactarnos.')
        return redirect('lista_activos')  # O a una página de 'gracias'

    return render(request, 'gestion_activos/contacto.html')

@login_required
@grupo_requerido('Usuario')
def solicitar_mantenimiento(request, pk):
    """Permite a un usuario cambiar el estado de su activo a 'En mantenimiento'."""
    activo = get_object_or_404(Activo, pk=pk, responsable=request.user)
    if request.method == 'POST':
        activo.estado = 'en_mantenimiento'
        activo.save()
        messages.success(request, f'Se ha reportado la solicitud de mantenimiento para el activo "{activo.nombre}".')
    return redirect('mis_activos')

@login_required
@grupo_requerido('Usuario')
def historial_activo(request, pk):
    """Muestra el historial de un activo específico del usuario."""
    activo = get_object_or_404(Activo, pk=pk, responsable=request.user)
    # Lógica para obtener el historial del activo...
    return render(request, 'gestion_activos/historial_activo.html', {'activo': activo})

@login_required
@grupo_requerido('Usuario')
def editar_mi_activo(request, pk):
    """Permite a un usuario editar la información de uno de sus propios activos."""
    activo = get_object_or_404(Activo, pk=pk, responsable=request.user)
    if request.method == 'POST':
        form = UsuarioActivoForm(request.POST, instance=activo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Activo actualizado correctamente.')
            return redirect('mis_activos')
    else:
        form = UsuarioActivoForm(instance=activo)
    return render(request, 'gestion_activos/editar_mi_activo.html', {'form': form, 'activo': activo})

@login_required
def ver_perfil(request):
    """
    Muestra el perfil del usuario y maneja la actualización de su
    información personal y el cambio de su contraseña.
    """
    # Inicializamos ambos formularios
    perfil_form = PerfilForm(instance=request.user.perfil)
    password_form = PasswordChangeForm(request.user)

    if request.method == 'POST':
        # Verificamos qué botón de formulario se presionó
        if 'update_profile' in request.POST:
            perfil_form = PerfilForm(request.POST, instance=request.user.perfil)
            if perfil_form.is_valid():
                perfil_form.save()
                messages.success(request, '¡Tu información de perfil ha sido actualizada!')
                return redirect('ver_perfil')

        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, '¡Tu contraseña ha sido actualizada correctamente!')
                return redirect('ver_perfil')
            else:
                messages.error(request, 'Error al cambiar la contraseña. Por favor, corrige los errores.')

    context = {
        'perfil_form': perfil_form,
        'password_form': password_form,
    }
    return render(request, 'gestion_activos/perfil.html', context)

def check_username_availability(request):
    """Verifica si un nombre de usuario ya está en uso."""
    username = request.GET.get('value', None)
    # la búsqueda 'iexact' no distingue mayúsculas de minúsculas
    is_taken = User.objects.filter(username__iexact=username).exists()
    return JsonResponse({'is_taken': is_taken})

def check_email_availability(request):
    """Verifica si un email ya está en uso."""
    email = request.GET.get('value', None)
    if not email:
        return JsonResponse({'is_taken': False})
    is_taken = User.objects.filter(email__iexact=email).exists()
    return JsonResponse({'is_taken': is_taken})

def check_ci_availability(request):
    """Verifica si una cédula ya está en uso."""
    ci = request.GET.get('value', None)
    if not ci:
        return JsonResponse({'is_taken': False})
    is_taken = Perfil.objects.filter(ci=ci).exists()
    return JsonResponse({'is_taken': is_taken})