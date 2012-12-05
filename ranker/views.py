from django import forms
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.views.defaults import page_not_found, server_error
from django.http import HttpResponse
from django.db.models import Count
from django.template import RequestContext
from django.utils import simplejson
from models import *

class AxisForm(forms.ModelForm):
    class Meta:
        model = Axis

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item

class RankingForm(forms.Form):
    pass    

class NewGameForm(forms.Form):
    title = forms.CharField(max_length=80)
    axes = forms.ModelMultipleChoiceField(queryset=Axis.objects.all())

class ClaimGameForm(forms.Form):
    x_axis = forms.ModelChoiceField(queryset=[], empty_label=None)
    y_axis = forms.ModelChoiceField(queryset=[], empty_label=None)
    def __init__(self, game, *args, **kwargs):
        super(ClaimGameForm, self).__init__(*args, **kwargs)
        self.x_axis.queryset = game.gameaxis_set.all()
        self.y_axis.queryset = game.gameaxis_set.all()

def index(request):
    user = request.user
    games = Game.objects.filter(plotter__isnull=False)[:5]
    inactive_games = Game.objects.filter(plotter__isnull=True)
    return render_to_response("ranker/index.html", 
                             {"games": games,
                              "inactive_games": inactive_games,
                              "user": user
                             },context_instance=RequestContext(request))

def game(request, game_slug=""):
    user = request.user
    game = get_object_or_404(Game, slug=game_slug)
    x_axis, y_axis = game.x_axis, game.y_axis

    return render_to_response("ranker/game.html",
                             {"game": game,
                              "user": user,
                              "x_axis": x_axis,
                              "y_axis": y_axis
                             }, context_instance=RequestContext(request))

def to_json_to_response(jsondata):
    return HttpResponse(simplejson.dumps(jsondata), mimetype="application/json")

def json_data(request):
    """Dump a json object with axes and items""" 
    axes = [(ax.title, ax.slug) for ax in Axis.objects.all()]
    items = [(it.title, it.slug) for it in Item.objects.all()]
    return to_json_to_response({"axes": axes, "items": items})
