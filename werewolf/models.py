from django.db import models
from django.contrib.auth.models import User


class Game(models.Model):
    name = models.CharField(max_length=30, unique=True)
    started_date = models.DateTimeField('date started', auto_now_add=True)
    user_characters = models.ManyToManyField('UserCharacterRelationship')


class Character(models.Model):

    name = models.CharField(max_length=200)
    users = models.ManyToManyField(User, through='UserCharacterRelationship')

    def __unicode__(self):
        return self.name


class UserCharacterRelationship(models.Model):
    user = models.ForeignKey(User)
    character = models.ForeignKey(Character)


class Switch(models.Model):
    '''A switch action in a game'''
    victim = models.ForeignKey(User, related_name='victim', default=1)
    initiator = models.ForeignKey(User, related_name='initiator', default=1)
