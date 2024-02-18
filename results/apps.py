from django.apps import AppConfig


class ResultsConfig(AppConfig):
    name = "results"

    def ready(self):
        import results.signals
