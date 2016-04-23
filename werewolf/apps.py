from django.apps import AppConfig


class WerewolfConfig(AppConfig):
    name = 'werewolf'

    def ready(self):
        import signals
