from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
import haikunator


def _new_haiku():
    name = None
    while not name:
        name = haikunator.haikunate(tokenlength=3, delimiter='')
        if Game.objects.filter(name=name).exists():
            name = None
            continue
    return name


class Game(models.Model):
    name = models.CharField(max_length=30, default=_new_haiku, unique=True)
    started_date = models.DateTimeField('date started', auto_now_add=True)
    users = models.ManyToManyField(User)
    present = ArrayField(models.CharField(max_length=10), null=True, default=[])
    num_present = models.IntegerField(default=0)

    def num_users(self):
        return self.users.count()

    def is_ready(self):
        return self.num_users <= self.num_present

    def __unicode__(self):
        return self.name


class Character(models.Model):

    name = models.CharField(max_length=200)
    users = models.ManyToManyField(User, through='Matchup')

    def __unicode__(self):
        return self.name


class Matchup(models.Model):
    user = models.ForeignKey(User)
    character = models.ForeignKey(Character)
    game = models.ForeignKey(Game)
    is_final = models.BooleanField(default=False)

    def __unicode__(self):
        return '%s as %s in %s' % (self.user, self.character, self.game)



class Switch(models.Model):
    '''A switch action in a game'''
    victim = models.ForeignKey(User, related_name='victim', default=1)
    initiator = models.ForeignKey(User, related_name='initiator', default=1)

    def __unicode__(self):
        return '%s switched %s' % (self.initiator, self.victim)

