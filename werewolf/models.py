from django.db import models
from django.contrib.auth.models import User


class Game(models.Model):
    name = models.CharField(max_length=30, unique=True)
    started_date = models.DateTimeField('date started', auto_now_add=True)

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

    def __unicode__(self):
        return '%s as %s in %s' % (self.user, self.character, self.game)



class Switch(models.Model):
    '''A switch action in a game'''
    victim = models.ForeignKey(User, related_name='victim', default=1)
    initiator = models.ForeignKey(User, related_name='initiator', default=1)

    def __unicode__(self):
        return '%s switched %s' % (self.initiator, self.victim)

