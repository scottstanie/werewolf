from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Game


@receiver(post_save, sender=Game)
def initiate_game(sender, **kwargs):
    print sender
    print kwargs
