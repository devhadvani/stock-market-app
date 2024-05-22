from django.apps import AppConfig


class AppStocksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_stocks'
    
    def ready(self):
        import app_stocks.signals