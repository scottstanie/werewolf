from channels import Group
from channels.sessions import channel_session
from .models import Game
import json
import logging

log = logging.getLogger(__name__)


def form_groupname(name):
    return 'game-%s' % name


@channel_session
def ws_connect(message):
    path = message['path']
    try:
        _, _, name = path.strip('/').split('/')
        game = Game.objects.get(name=name)
        game.num_present += 1
        game.save()
    except ValueError:
        log.debug('Invalid path: %s' % path)
        return
    except Game.DoesNotExist:
        log.debug('game does not exist game=%s', game)
        return

    log.info('chat connect room=%s client=%s:%s',
             game.name, message['client'][0], message['client'][1])

    groupname = form_groupname(game.name)
    Group(groupname).add(message.reply_channel)
    message.channel_session['gamename'] = game.name


@channel_session
def ws_receive(message):
    name = message.channel_session['gamename']
    game = Game.objects.get(name=name)
    data = json.loads(message['text'])
    # m = game.messages.create(handle=data['handle'], message=data['message'])
    # Group('chat-' + name).send({'text': json.dumps(m.as_dict())})
    Group(form_groupname(name)).send({'text': json.dumps(data)})


@channel_session
def ws_disconnect(message):
    name = message.channel_session.get('gamename')
    try:
        game = Game.objects.get(name=name)
        game.num_present -= 1
        game.save()
        groupname = form_groupname(game)
    except Game.DoesNotExist:
        log.info('%s doesnt exist' % name)

    if groupname:
        Group(groupname).discard(message.reply_channel)
