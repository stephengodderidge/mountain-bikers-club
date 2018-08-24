from django.apps import AppConfig


class TrailConfig(AppConfig):
    name = 'trail'

    def ready(self):
        import trail.signals
