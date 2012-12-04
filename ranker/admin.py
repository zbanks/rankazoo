from django.contrib.admin import *
from models import *

class GroupAdmin(ModelAdmin):
    pass

class ItemAdmin(ModelAdmin):
    pass

class AxisAdmin(ModelAdmin):
    pass

class RankingAdmin(ModelAdmin):
    pass

class GameAdmin(ModelAdmin):
    pass

class QueueItemAdmin(ModelAdmin):
    pass

class QueueItemVoteAdmin(ModelAdmin):
    pass

class GuessAdmin(ModelAdmin):
    pass

class GameAxisAdmin(ModelAdmin):
    pass

class GuessAxisAdmin(ModelAdmin):
    pass

site.register(Group, GroupAdmin)
site.register(Item, ItemAdmin)
site.register(Axis, AxisAdmin)
site.register(Ranking, RankingAdmin)
site.register(Game, GameAdmin)
site.register(QueueItem, QueueItemAdmin)
site.register(QueueItemVote, QueueItemVoteAdmin)
site.register(Guess, GuessAdmin)
site.register(GameAxis, GameAxisAdmin)
site.register(GuessAxis, GuessAxisAdmin)
