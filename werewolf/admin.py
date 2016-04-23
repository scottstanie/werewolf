from django.contrib import admin

from .models import Game, Character, Switch, Matchup


class GameAdmin(admin.ModelAdmin):
    readonly_fields = ('created_date',)


class MatchupInline(admin.TabularInline):
    model = Matchup
    extra = 1


class UserAdmin(admin.ModelAdmin):
    inlines = (MatchupInline,)


class CharacterAdmin(admin.ModelAdmin):
    inlines = (MatchupInline,)


admin.site.register(Game, GameAdmin)
admin.site.register(Character, CharacterAdmin)
admin.site.register(Switch)
admin.site.register(Matchup)
