import json
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels import Group

from .models import Vote


@receiver(post_save, sender=Vote)
def end_game(sender, **kwargs):
    print 'End Game'
    game = kwargs['instance'].game
    if game.is_finished_voting():
        game.finished = True

        vote_counts, winners = game.tally_votes()
        game.winning_teams.extend(winners)
        game.save()
        Group(game.form_groupname()).send({
            'text': json.dumps({
                'finished': True,
                'votes': vote_counts,
                'winners': winners
            })
        })
        print 'all voted'
