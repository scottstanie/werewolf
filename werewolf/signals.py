import json
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels import Group

from .models import Vote


@receiver(post_save, sender=Vote)
def end_game(sender, **kwargs):
    game = kwargs['instance'].game
    if game.is_finished_voting():
        game.finished = True

        winners = game.tally_votes()
        game.winning_team.extend(winners)
        game.save()
        Group(game.form_groupname()).send({
            'text': json.dumps({
                'finished': True
            })
        })
        print 'all voted'
