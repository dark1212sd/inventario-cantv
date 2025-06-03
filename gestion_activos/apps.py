from django.apps import AppConfig

class GestionActivosConfig(AppConfig):
    name = 'gestion_activos'

    def ready(self):
        import gestion_activos.signals  # asegúrate de importar el módulo aquí