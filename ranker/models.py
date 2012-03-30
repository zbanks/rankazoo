from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from asf import AutoSlugField

AXIS_SCALES = {"LINEAR" : ("Linear", -100, 100),
               "POSLINEAR" : ("Positive Linear", 0, 100),
               "LOG" : ("Logarithmic", 0, 100),
               "BINARY" : ("Binary", 0, 1)
              }

AXIS_SCALES_NAMES = zip(AXIS_SCALES.keys(), zip(*AXIS_SCALES.values())[0])


class Item(models.Model):
    slug = AutoSlugField(unique=True, populate_from="title", max_length=30)
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    
    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("item", kwargs={"item_slug": self.slug})

    class Meta:
        pass

class Axis(models.Model):
    slug = AutoSlugField(unique=True, populate_from="title", max_length=30)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    scale = models.CharField(max_length=16, choices=AXIS_SCALES_NAMES, default="POSLINEAR")

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("axis", kwargs={"axis_slug": self.slug})

    def get_min_value(self):
        return AXIS_SCALES[self.scale][1]

    def get_max_value(self):
        return AXIS_SCALES[self.scale][2]

    def renorm_ranks(self):
        minv = self.get_min_value()
        maxv = self.get_max_value()
        for rank in self.rank_set.all():
            rank.value = max(min(rank.value, maxv), minv)
            rank.save()

    class Meta:
        verbose_name_plural = "Axes"

class Rank(models.Model):
    item = models.ForeignKey(Item)
    axis = models.ForeignKey(Axis)
    value = models.DecimalField(max_digits=6, decimal_places=4, default=0.0)
    user = models.ForeignKey(User, blank=True, null=True) # Future
    description = models.TextField(blank=True) # Future

    def __unicode__(self):
        return "%s ranks %0.2f on %s" % (self.item, self.value, self.axis)

    class Meta:
        verbose_name = "Ranking"
        verbose_name_plural = "Rankings"
