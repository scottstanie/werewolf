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


@require_http_methods(['POST'])
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
def switch(request, initiator_id, before_id, after_id):
    '''User has iniatiated a switch of the cards'''
    initiator = get_object_or_404(Matchup, id=initiator_id)
    before = get_object_or_404(Matchup, id=before_id)
    after = get_object_or_404(Matchup, id=after_id)
    game = initiator.game

    # First record the switch happening
    s = Switch(initiator=initiator, before=before, after=after, game=game)
    print s
    s.save()

    # Then make new matchups for the game
    m = Matchup(user=before.user, character=after.character, game=game)
    m.save()

    return JsonResponse({'ok': 'ok'})


@require_http_methods(['POST'])
def start(request, game_name):
    '''User has signalled to start the game'''
    characters_chosen = json.loads(request.POST['chars'])
    characters = list(Character.objects.filter(id__in=characters_chosen))
    random.shuffle(characters)

    game = get_object_or_404(Game, name=game_name)
    game.num_cards_selected = len(characters_chosen)

    # {user_id: '<html of character for this user>'}
    matchups = game.generate_matchups(characters)
    character_info = game.get_character_info(matchups)
    print character_info
    game.started = True
    game.current_stage = 1

    # game.save(update_fields=['started'])
    game.save()

    Group(game.form_groupname()).send({
        # Channel messages need 'text' as a key
        'text': json.dumps({
            'starting': True,
            'characters': character_info,
            'current_stage': game.current_stage,
            'stage_info': game.stage_info()
        })
    })
    return JsonResponse(character_info)


@require_http_methods(['POST'])
def advance(request, game_name, user_id):
    user = get_object_or_404(User, id=user_id)
    game = get_object_or_404(Game, name=game_name)

    # Make sure no hackin
    print 'ADVANCE!'
    print user_id, game.ready_to_advance
    if user in game.users.all():
        game.ready_to_advance = list(set(game.ready_to_advance + [user.username]))
        game.save()

    # If there are still others, don't advance yet
    if len(game.ready_to_advance) < game.num_users():
        return JsonResponse({'num_ready': len(game.ready_to_advance)})

    matchups = game.current_matchups()
    character_info = game.get_character_info(matchups)
    print character_info

    game.current_stage += 1
    game.ready_to_advance = []
    game.save()

    Group(game.form_groupname()).send({
        # Channel messages need 'text' as a key
        'text': json.dumps({
            'advancing': True,
            'characters': character_info,
            'current_stage': game.current_stage,
        })
    })
    return JsonResponse(character_info)
