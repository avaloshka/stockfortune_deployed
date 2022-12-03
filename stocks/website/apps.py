from django.apps import AppConfig


class WebsiteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'website'

    def ready(self):
        from jobs.jobs import Millioner
        millioner = Millioner()
        millioner.run_in_order()