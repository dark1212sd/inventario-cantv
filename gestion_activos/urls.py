from django.contrib import admin
from django.urls import path, include
from . import views
from gestion_activos.views import lista_usuarios, crear_usuario


urlpatterns = [
    # --- Login_view ---
    path('admin/', admin.site.urls),

    # ¡Aquí sólo incluyes las rutas de gestion_activos!

    # --- CRUD de permisos ---
    path('sin_permisos/', views.sin_permisos, name='sin_permisos'),

    # --- CRUD de creación de usuarios ---
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/editar/<int:pk>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/eliminar/<int:pk>/', views.eliminar_usuario, name='eliminar_usuario'),
    # --- CRUD de Activos ---
    path('', views.lista_activos, name='lista_activos'),
    path('activos/editar/<int:pk>/', views.editar_activo, name='editar_activo'),
    path('activos/eliminar/<int:pk>/', views.eliminar_activo, name='eliminar_activo'),
    path('activos/crear/', views.registrar_activo, name='registrar_activo'),

    # --- CRUD de Categorías ---
    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('categorias/crear/', views.crear_categoria, name='crear_categoria'),
    path('categorias/editar/<int:pk>/', views.editar_categoria, name='editar_categoria'),
    path('categorias/eliminar/<int:pk>/', views.eliminar_categoria, name='eliminar_categoria'),

    # --- CRUD de Ubicaciones ---
    path('ubicaciones/', views.lista_ubicaciones, name='lista_ubicaciones'),
    path('ubicaciones/crear/', views.crear_ubicacion, name='crear_ubicacion'),
    path('ubicaciones/editar/<int:pk>/', views.editar_ubicacion, name='editar_ubicacion'),
    path('ubicaciones/eliminar/<int:pk>/', views.eliminar_ubicacion, name='eliminar_ubicacion'),

    # --- Autenticación ---
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('reporte/pdf/', views.reporte_pdf, name='reporte_pdf'),
    path('reporte/excel/', views.exportar_excel, name='exportar_excel'),

    path('usuarios/', lista_usuarios, name='lista_usuarios'),
    path('usuarios/crear/', crear_usuario, name='crear_usuario'),
]