import random
import json
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.views.generic.edit import CreateView
from django.views.decorators.http import require_http_methods
from channels import Group

from .models import Game, Character, Switch, Matchup, Vote
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
        'finished_games': u.game_set.filter(finished=True),
        'unfinished_games': u.game_set.filter(finished=False)
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
    # random.shuffle(characters)
    characters.sort(key=lambda c: c.id, reverse=True)

    game = get_object_or_404(Game, name=game_name)
    game.num_cards_selected = len(characters_chosen)

    # {user_id: '<html of character for this user>'}
    matchups = game.generate_matchups(characters)
    character_info = game.get_character_info(matchups)
    print character_info
    game.current_stage = 1

    # game.save(update_fields=['finished'])
    game.save()

    countdown_time = json.loads(request.POST['countdownTime'])
    Group(game.form_groupname()).send({
        # Channel messages need 'text' as a key
        'text': json.dumps({
            'starting': True,
            'countdown_time': countdown_time,
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
    if user not in game.users.all():
        return JsonResponse({'allowed': False})

    current_matchups = game.current_matchups()
    print 'current_matchups'
    print current_matchups
    character_info = game.get_character_info(current_matchups)

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


@require_http_methods(['GET', 'POST'])
def vote(request, game_name):
    game = get_object_or_404(Game, name=game_name)
    if request.method == 'GET':
        users = game.users.order_by('username')
        template_string = render_to_string(
            'werewolf/vote.html',
            {'players': users}
        )
        return JsonResponse({'template': template_string})
    elif request.method == 'POST':
        player_id = request.POST['playerId']
        # Check if this player somehow already voted
        if game.vote_set.filter(voter__user__id=request.user.id).count() > 0:
            return JsonResponse({'allowed': False})

        voted_for = Matchup.objects.filter(game=game, user_id=player_id).order_by('-id').first()
        voter = Matchup.objects.filter(game=game, user_id=request.user.id).order_by('-id').first()
        v = Vote(voted_for=voted_for, voter=voter, game=game)
        v.save()
        return JsonResponse({'vote_id': v.id})
