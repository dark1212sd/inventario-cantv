from django.contrib import admin
from django.urls import path, include
from . import views
from gestion_activos.views import lista_usuarios, crear_usuario

urlpatterns = [
    # --- Autenticación ---
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('sin_permisos/', views.sin_permisos, name='sin_permisos'),

    # --- Usuarios y Roles ---
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/editar/<int:pk>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/eliminar/<int:pk>/', views.eliminar_usuario, name='eliminar_usuario'),

    # --- CRUD Activos ---
    path('', views.lista_activos, name='lista_activos'),
    path('activos/crear/', views.registrar_activo, name='registrar_activo'),
    path('activos/editar/<int:pk>/', views.editar_activo, name='editar_activo'),
    path('activos/eliminar/<int:pk>/', views.eliminar_activo, name='eliminar_activo'),

    # --- CRUD Categorías ---
    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('categorias/crear/', views.crear_categoria, name='crear_categoria'),
    path('categorias/editar/<int:pk>/', views.editar_categoria, name='editar_categoria'),
    path('categorias/eliminar/<int:pk>/', views.eliminar_categoria, name='eliminar_categoria'),

    # --- CRUD Ubicaciones ---
    path('ubicaciones/', views.lista_ubicaciones, name='lista_ubicaciones'),
    path('ubicaciones/crear/', views.crear_ubicacion, name='crear_ubicacion'),
    path('ubicaciones/editar/<int:pk>/', views.editar_ubicacion, name='editar_ubicacion'),
    path('ubicaciones/eliminar/<int:pk>/', views.eliminar_ubicacion, name='eliminar_ubicacion'),

    # --- Reportes ---
    path('reporte/pdf/', views.reporte_pdf, name='reporte_pdf'),
    path('reporte/excel/', views.exportar_excel, name='exportar_excel'),

    # --- Bitacora ---
    path('bitacora/', views.vista_bitacora, name='vista_bitacora'),
    # --- Usuario ---
    path('mis-activos/', views.mis_activos, name='mis_activos'),
    path('mis-activos/historial/<int:pk>/', views.historial_activo, name='historial_activo'),
    path('activos/solicitar-mantenimiento/<int:pk>/', views.solicitar_mantenimiento, name='solicitar_mantenimiento'),
    path('mis-activos/editar/<int:pk>/', views.editar_mi_activo, name='editar_mi_activo'),
    path('mi-perfil/', views.ver_perfil, name='ver_perfil'),
]