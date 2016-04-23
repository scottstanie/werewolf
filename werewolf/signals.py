import json
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels import Group

from .models import Game


@receiver(post_save, sender=Game)
def initiate_game(sender, **kwargs):
    if kwargs['update_fields'] == set(['started']):
        current_game = kwargs['instance']