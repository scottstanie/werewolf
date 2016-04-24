import random
import json
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from django.views.decorators.http import require_http_methods
from channels import Group

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
        'characters': Character.objects.order_by('id').all(),
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
    characters = list(Character.objects.filter(id__in=characters_chosen))
    random.shuffle(characters)

    game = get_object_or_404(Game, name=game_name)

    # {user_id: '<html of character for this user>'}
    character_info = game.generate_matchups(characters)
    print character_info
    game.started = True
    game.save(update_fields=['started'])

    Group(game.form_groupname()).send({
        'text': json.dumps({
            'starting': True,
            'characters': character_info
        })
    })
    return JsonResponse(character_info)
