from channels import Group
from channels.sessions import channel_session
from .models import Game
import json


@channel_session
def ws_connect(message):
    prefix, name = message['path'].strip('/').split('/')
    game = Game.objects.get(name=name)
    Group('chat-' + name).add(message.reply_channel)
    message.channel_session['game'] = game.name


@channel_session
def ws_receive(message):
    name = message.channel_session['game']
    game = Game.objects.get(name=name)
    data = json.loads(message['text'])
    m = game.messages.create(handle=data['handle'], message=data['message'])
    Group('chat-' + name).send({'text': json.dumps(m.as_dict())})


@channel_session
def ws_disconnect(message):
    name = message.channel_session['game']
    Group('chat-' + name).discard(message.reply_channel)
