from django.contrib.admin import *
from models import *

class AxisAdmin(ModelAdmin):
    pass

class ItemAdmin(ModelAdmin):
    pass

class RankingAdmin(ModelAdmin):
    pass

site.register(Axis, AxisAdmin)
site.register(Item, ItemAdmin)
site.register(Ranking, RankingAdmin)
