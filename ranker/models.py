from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from asf import AutoSlugField

# User from django.contrib
# Comments from django.contrib

class Group(models.Model):
    slug = AutoSlugField(unique=True, populate_from="name", max_length=30)
    name = models.CharField(max_length=80)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["name"]

class Item(models.Model):
    slug = AutoSlugField(unique=True, populate_from="title", max_length=30)
    title = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("item", kwargs={"item_slug": self.slug})

    class Meta:
        pass

class Axis(models.Model):
    AXIS_SCALES = {"LINEAR" : ("Linear", -100, 100),
                   "POSLINEAR" : ("Positive Linear", 0, 100),
                   "LOG" : ("Logarithmic", 0, 100),
                   "BINARY" : ("Binary", 0, 1)
                  }

    AXIS_SCALES_NAMES = zip(AXIS_SCALES.keys(), zip(*AXIS_SCALES.values())[0])

    slug = AutoSlugField(unique=True, populate_from="title", max_length=30)
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    scale = models.CharField(max_length=16, choices=AXIS_SCALES_NAMES, default="LINEAR")

    def __unicode__(self):
        return self.title

#def get_absolute_url(self):
#return reverse("axis", kwargs={"axis_slug": self.slug})

    def get_min_value(self):
        return self.AXIS_SCALES[self.scale][1]

    def get_max_value(self):
        return self.AXIS_SCALES[self.scale][2]

    def renorm_ranks(self):
        minv = self.get_min_value()
        maxv = self.get_max_value()
        for rank in self.rank_set.all():
            rank.value = max(min(rank.value, maxv), minv)
            rank.save()

    class Meta:
        verbose_name_plural = "Axes"
        ordering = ["title"]

class Ranking(models.Model):
    item = models.ForeignKey(Item)
    axis = models.ForeignKey(Axis)
    game = models.ForeignKey("Game")
    value = models.DecimalField(max_digits=6, decimal_places=4, default=0.0)
    user = models.ForeignKey(User, blank=True, null=True)
    description = models.TextField(blank=True)
    time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "%s ranks %0.2f on %s" % (self.item, self.value, self.axis)

    class Meta:
        ordering = ["-time"]

class Game(models.Model):
    slug = AutoSlugField(unique=True, populate_from="title", max_length=30)
    title = models.CharField(max_length=80, blank=True)
#creator = models.ForeignKey(User, blank=True, null=True) # FUTURE TODO
    plotter = models.ForeignKey(User, blank=True, null=True)
    followers = models.ManyToManyField(User, related_name="following_games", blank=True, editable=False)
    active = models.BooleanField(default=True)
    start_time = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now_add=True, editable=False)

    def __unicode__(self):
        return u"Game by %s %s" % (self.plotter, u"(inactive)" if not self.active else u"")

    def touch(self):
        self.last_modified = datetime.datetime.now()
        self.save()

    def get_absolute_url(self):
        return reverse("game", kwargs={"game_slug": self.slug})

    @property
    def claimed(self):
        return self.plotter is not None

    @property
    def x_axis(self):
        try: 
            return self.gameaxis_set.get(direction="x").axis
        except:
            return None

    @property
    def y_axis(self):
        try: 
            return self.gameaxis_set.get(direction="y").axis
        except:
            return None

    @property
    def plotted_items(self):
        # plotted_items ::= [(item, rankx, ranky)]
        plotted_items_pk = {}
        for ranking in self.ranking_set.all():
            if ranking.item.pk in plotted_items_pk:
                rx, ry = plotted_items_pk[ranking.item.pk]
            else:
                rx, ry = None, None
            if ranking.axis.pk == self.x_axis.pk:
                rx = ranking
            elif ranking.axis.pk == self.y_axis.pk:
                ry = ranking
            else:
                pass # Neither x nor y?
            plotted_items_pk[ranking.item.pk] = (rx, ry)
        plotted_items = []
        for item_pk, (rankx, ranky) in plotted_items_pk.items():
            if rankx is not None and ranky is not None:
                try:
                    plotted_items.append((Item.objects.get(pk=item_pk), rankx, ranky))
                except: pass
        return plotted_items

    @property
    def queue(self):
        return sorted(self.queueitem_set.all(), key=lambda qi: -qi.value)

    class Meta:
        ordering = ["-last_modified"]

class QueueItem(models.Model):
    game = models.ForeignKey(Game)
    item = models.ForeignKey(Item)
    time = models.DateTimeField(auto_now_add=True)

    @property
    def value(self):
        v = self.queueitemvote_set.aggregate(models.Sum('value'))["value__sum"]
        if v:
            return v
        else:
            return 0

    def __unicode__(self):
        return u"(%+d) %s" % (self.value, self.item)

    class Meta:
        ordering = ["-time"]

class QueueItemVote(models.Model):
    queue_item = models.ForeignKey(QueueItem)
    user = models.ForeignKey(User)
    value = models.IntegerField(default=0)


class Guess(models.Model):
    user = models.ForeignKey(User)
    game = models.ForeignKey(Game)
    time = models.DateTimeField(auto_now_add=True)
    correct = models.BooleanField(default=False)

    def __unicode__(self):
        return u"Guess by %s on [%s]" % (self.user, self.game)

    class Meta:
        ordering = ["-time"]
        verbose_name_plural = "Guesses"


class AxisInstance(models.Model):
    AXIS_TYPES = {"x": "x",
                  "y": "y" }
    axis = models.ForeignKey(Axis)
    direction = models.CharField(max_length=3, choices=AXIS_TYPES.items(), blank=True, default="")

    def __unicode__(self):
        return unicode(self.axis)

    class Meta:
        abstract = True
        ordering = ["axis"]

class GameAxis(AxisInstance):
    game = models.ForeignKey(Game)

    class Meta:
        ordering = ["axis"]
        verbose_name_plural = "Game axes"

class GuessAxis(AxisInstance):
    guess = models.ForeignKey(Guess)

    class Meta:
        ordering = ["axis"]
        verbose_name_plural = "Guess axes"
