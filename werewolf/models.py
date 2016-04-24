import random
from itertools import izip_longest
from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.template.loader import render_to_string
import haikunator
from os.path import join


def _new_haiku():
    name = None
    while not name:
        name = haikunator.haikunate(tokenlength=3, delimiter='')
        if Game.objects.filter(name=name).exists():
            name = None
            continue
    return name


def find_characters(matchups, character_name):
    return [m for m in matchups if m.character.name == character_name]


def find_middle_cards(matchups):
    return [m for m in matchups if m.user is None]


def find_player_cards(matchups):
    return [m for m in matchups if m.user]


class Game(models.Model):
    name = models.CharField(max_length=30, default=_new_haiku, unique=True)
    created_date = models.DateTimeField('date created', auto_now_add=True)
    started = models.BooleanField(default=False)
    users = models.ManyToManyField(User)
    present = ArrayField(models.CharField(max_length=10), null=True, default=[])

    def num_users(self):
        return self.users.count()

    def form_groupname(self):
        '''Used for the group channel of a game'''
        return 'game-%s' % self.name

    def _character_view(self, character):
        '''Input: name of character
        output: string the html file for the character'''
        return 'werewolf/characters/%s.html' % character.name.lower()

    def generate_matchups(self, characters):
        '''Create the Matchups for this game'''
        users = list(self.users.all())
        random.shuffle(users)
        # Weird feature of map:
        # list(izip_longest(chars, users)) == map(None, chars, users)
        matchup_tuples = izip_longest(users, characters)
        matchup_dicts = [{'user': t[0], 'character': t[1], 'game': self}
                         for t in matchup_tuples]

        matchups = [Matchup(**m) for m in matchup_dicts]

        character_info = {}
        for m in matchups:
            m.save()

        game_info = {
            'werewolves': find_characters(matchups, 'Werewolf'),
            'masons': find_characters(matchups, 'Mason'),
            'middle_cards': find_middle_cards(matchups),
            'player_cards': find_player_cards(matchups),
        }
        print 'game_info'
        print game_info
        for m in matchups:
            if m.user:
                context = self.create_context(m, game_info)
                print m
                print context
                character_info[m.user.id] = render_to_string(
                    self._character_view(m.character),
                    context=context
                )

        return character_info

    def create_context(self, matchup, game_info):
        context = {'character': matchup.character}
        char_name = matchup.character.name
        if char_name in ('Werewolf', 'Minion'):
            wolf_users = [m.user.username for m in game_info['werewolves'] if m.user]
            context['werewolves'] = wolf_users

        if char_name == 'Werewolf':
            other_wolf = list(set(wolf_users) - set([matchup.user.username]))
            context['other_wolf'] = other_wolf[0] if other_wolf else []
            context['middle_card'] = random.choice(game_info['middle_cards'])
        elif char_name == 'Mason':
            masons = [m.user.username for m in game_info['masons'] if m.user]
            other_mason = list(set(masons) - set([matchup.user.username]))
            context['other_mason'] = other_mason[0] if other_mason else []
        elif char_name == 'Seer':
            context['middle_cards'] = random.sample(game_info['middle_cards'], 2)
            # Remove the current player's card from the player_cards list
            context['player_cards'] = list(set(game_info['player_cards']) -
                                           set([matchup]))
        elif char_name == 'Robber':
            context['player_cards'] = list(set(game_info['player_cards']) -
                                           set([matchup]))
            context['initiator'] = matchup
        elif char_name == 'Troublemaker':
            context['player_cards'] = game_info['player_cards']
        elif char_name == 'Drunk':
            context['middle_cards'] = game_info['middle_cards']
            context['before_matchup'] = matchup
        elif char_name == 'Insomniac':
            context['your_card'] = matchup

        return context

    def __unicode__(self):
        return self.name


class Character(models.Model):
    name = models.CharField(max_length=200)
    image = models.FilePathField(path=join('/static', 'werewolf', 'images'),
                                 recursive=True, blank=True, null=True)
    users = models.ManyToManyField(User, through='Matchup')

    def __unicode__(self):
        return self.name


class Matchup(models.Model):
    user = models.ForeignKey(User, null=True)
    character = models.ForeignKey(Character)
    game = models.ForeignKey(Game)
    is_final = models.BooleanField(default=False)

    def __unicode__(self):
        return '%s as %s in %s' % (self.user, self.character, self.game)


class Switch(models.Model):
    '''A switch action in a game'''
    initiator = models.ForeignKey(Matchup, related_name='initiator', default=1)
    before = models.ForeignKey(Matchup, related_name='before', default=1)
    after = models.ForeignKey(Matchup, related_name='after', default=1)
    game = models.ForeignKey(Game)

    def __unicode__(self):
        return '%s made %s into %s' % (self.initiator, self.before, self.after)
