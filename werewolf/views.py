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
    context = {}
    return render(request, 'werewolf/profile.html', context)


def ready(request, game_name, user_id):
    '''User has signalled they are ready for the game to start'''
    user = get_object_or_404(User, id=user_id)
    game = get_object_or_404(Game, name=game_name)
    print game.users.all()
    if user in game.users.all():
        game.present = sorted(list(set(game.present + [user.username])))
        game.save()
        allowed = True
    else:
        allowed = False
    return JsonResponse({'allowed': allowed})
