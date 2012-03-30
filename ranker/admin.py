from django.contrib.admin import *
from models import *

class AxisAdmin(ModelAdmin):
    pass

class ItemAdmin(ModelAdmin):
    pass

class RankAdmin(ModelAdmin):
    pass

site.register(Axis, AxisAdmin)
site.register(Item, ItemAdmin)
site.register(Rank, RankAdmin)
