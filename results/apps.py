from django.apps import AppConfig


class ResultsConfig(AppConfig):
    name = "results"

    def ready(self):
        import results.extensions  # noqa: F401
        import results.signals  # noqa: F401
