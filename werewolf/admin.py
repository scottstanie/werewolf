from django.contrib import admin

from .models import Game, Character, Switch, UserCharacterRelationship


class GameAdmin(admin.ModelAdmin):
    readonly_fields = ('started_date', 'name')

admin.site.register(Game, GameAdmin)
admin.site.register(Character)
admin.site.register(Switch)
admin.site.register(UserCharacterRelationship)
