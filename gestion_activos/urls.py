from django.urls import path
from . import views

urlpatterns = [
    # --- RUTA PRINCIPAL Y AUTENTICACIÓN ---
    # La ruta raíz (página de inicio) ahora apunta a nuestra vista "despachadora".
    path('', views.index_view, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('sin_permisos/', views.sin_permisos, name='sin_permisos'),

    # --- VISTAS DEL ROL "USUARIO" ---
    path('mis-activos/', views.mis_activos, name='mis_activos'),
    path('mis-activos/editar/<int:pk>/', views.editar_mi_activo, name='editar_mi_activo'),
    path('mis-activos/historial/<int:pk>/', views.historial_activo, name='historial_activo'),
    path('mis-activos/solicitar-mantenimiento/<int:pk>/', views.solicitar_mantenimiento, name='solicitar_mantenimiento'),
    path('mi-perfil/', views.ver_perfil, name='ver_perfil'),
    path('completar-perfil/', views.completar_perfil, name='completar_perfil'),

    # --- VISTAS DE ADMINISTRACIÓN: ACTIVOS ---
    # La lista de activos ahora tiene su propia URL dedicada.
    path('activos/', views.lista_activos, name='lista_activos'),
    path('activos/registrar/', views.registrar_activo, name='registrar_activo'),
    path('activos/editar/<int:pk>/', views.editar_activo, name='editar_activo'),
    path('activos/eliminar/<int:pk>/', views.eliminar_activo, name='eliminar_activo'),

    # --- VISTAS DE ADMINISTRACIÓN: CATEGORÍAS ---
    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('categorias/crear/', views.crear_categoria, name='crear_categoria'),
    path('categorias/editar/<int:pk>/', views.editar_categoria, name='editar_categoria'),
    path('categorias/eliminar/<int:pk>/', views.eliminar_categoria, name='eliminar_categoria'),

    # --- VISTAS DE ADMINISTRACIÓN: UBICACIONES ---
    path('ubicaciones/', views.lista_ubicaciones, name='lista_ubicaciones'),
    path('ubicaciones/crear/', views.crear_ubicacion, name='crear_categoria'), # Corregido: debería ser crear_ubicacion
    path('ubicaciones/editar/<int:pk>/', views.editar_ubicacion, name='editar_ubicacion'),
    path('ubicaciones/eliminar/<int:pk>/', views.eliminar_ubicacion, name='eliminar_ubicacion'),

    # --- VISTAS DE ADMINISTRACIÓN: USUARIOS ---
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/editar/<int:pk>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/eliminar/<int:pk>/', views.eliminar_usuario, name='eliminar_usuario'),

    # --- REPORTES Y OTROS ---
    path('reporte/pdf/', views.reporte_pdf, name='reporte_pdf'),
    path('reporte/excel/', views.exportar_excel, name='exportar_excel'),
    path('bitacora/', views.vista_bitacora, name='vista_bitacora'),
]