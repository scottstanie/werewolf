import json
import random
from itertools import izip_longest
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from django.views.decorators.http import require_http_methods

from .models import Game, Character, Switch, Matchup
from django.contrib.auth.models import User


def index(request):
    return render(request, 'werewolf/index.html')


def about(request):
    return render(request, 'werewolf/about.html')


def game(request, name=None):
    try:
        g = Game.objects.get(name=name)
    except Game.DoesNotExist:
        return render(request, 'werewolf/game.html', {
            'error_message': "This game doesn't exist.",
        })

    context = {
        'game': g,
        'characters': Character.objects.all(),
    }
    return render(request, 'werewolf/game.html', context)


class GameCreate(CreateView):
    model = Game
    fields = ['users']

    def form_valid(self, form):
        # TODO: check that request.user is one of the players
        form.instance.created_by = self.request.user
        return super(GameCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse('game', kwargs={'name': self.object.name})


@login_required
def profile(request):
    u = request.user

    context = {
        'started_games': u.game_set.filter(started=True),
        'unstarted_games': u.game_set.filter(started=False)
    }
    return render(request, 'werewolf/profile.html', context)


def ready(request, game_name, user_id):
    '''User has signalled they are ready for the game to start'''
    user = get_object_or_404(User, id=user_id)
    game = get_object_or_404(Game, name=game_name)
    if user in game.users.all():
        game.present = sorted(list(set(game.present + [user.username])))
        game.save()
        allowed = True
    else:
        allowed = False
    return JsonResponse({'allowed': allowed})


@require_http_methods(['POST'])
def start(request, game_name):
    '''User has signalled to start the game'''
    characters_chosen = json.loads(request.POST['chars'])
    characters = list(Character.objects.filter(name__in=characters_chosen))
    random.shuffle(characters)

    game = get_object_or_404(Game, name=game_name)
    users = list(game.users.all())
    random.shuffle(users)

    # Make a list of the same game to zip together
    # game_list = [game for _ in range(len(characters))]
    # Weird feature of map:
    # list(izip_longest(chars, users)) == map(None, chars, users)
    matchup_tuples = izip_longest(users, characters)
    matchup_dicts = [{'user': t[0], 'character': t[1], 'game': game}
                     for t in matchup_tuples]

    matchups = [Matchup(**m) for m in matchup_dicts]
    for m in matchups:
        m.save()
    print matchups

    game.started = True
    game.save(update_fields=['started'])
    return JsonResponse({})
