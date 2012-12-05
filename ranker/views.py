from django import forms
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.views.defaults import page_not_found, server_error
from django.http import HttpResponse
from django.db.models import Count
from models import *

class AxisForm(forms.ModelForm):
    class Meta:
        model = Axis

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item

class RankingForm(forms.Form):
    pass    

def index(request):
    user = request.user
    games = Game.objects.filter(plotter__isnull=False)[:5]
    inactive_games = Game.objects.filter(plotter__isnull=True)
    return render_to_response("ranker/index.html", 
                             {"games": games,
                              "inactive_games": inactive_games,
                              "user": user
                             })

def game(request, game_slug=""):
    user = request.user
    game = get_object_or_404(Game, slug=game_slug)
    x_axis, y_axis = game.x_axis, game.y_axis

    return render_to_response("ranker/game.html",
                             {"game": game,
                              "user": user,
                              "x_axis": x_axis,
                              "y_axis": y_axis
                             })
'''
def index(request):
    axes = Axis.objects.all()
    items = Item.objects.all()
    new_axis_form = AxisForm()
    new_item_form = ItemForm()
    return render_to_response("ranker/index.html", 
                             {"axes" : axes,
                              "items" : items,
                              "games" : games,
                              "new_axis_form" : new_axis_form,
                              "new_item_form" : new_item_form
                             })
'''


def axis(request, axis_slug=""):
    try:
        axis = Axis.objects.get(slug=axis_slug)
    except:
        axis = None

    if request.method == "POST":
        axis_form = AxisForm(request.POST, instance=axis)
        if axis_form.is_valid():
            axis_form.save()
            axis = axis_form.instance
            axis.renorm_ranks()
            return redirect(axis_form.instance.get_absolute_url()) 
    else:
        if not axis:
            return page_not_found(request)
        axis_form = AxisForm(instance=axis)

    items = Item.objects.all()
    ranked_items = []
    for item in items:
        try:
            rank = Ranking.objects.get(item=item, axis=axis)
            ranked_items.append((item, rank))
        except:
            ranked_items.append((item, None))
    
    def gr(x):
        if x:
            return x[1].value
        else:
            return 100000 
    ranked_items.sort(lambda a, b: cmp(gr(b), gr(a)))

    new_item_form = ItemForm()
    all_axes = Axis.objects.all()
    return render_to_response("ranker/axis.html",
                             {"axis" : axis,
                              "items" : items,
                              "all_axes" : all_axes,
                              "ranked_items" : ranked_items,
                              "axis_form" : axis_form,
                              "new_item_form" : new_item_form
                             })




def item(request, item_slug=""):
    try:
        item = Item.objects.get(slug=item_slug)
    except:
        item = None

    if request.method == "POST":
        item_form = ItemForm(request.POST, instance=item)
        if item_form.is_valid():
            item_form.save()
            return redirect(item_form.instance.get_absolute_url())
    else:
        if not item:
            return page_not_found(request)
        item_form = ItemForm(instance=item)

    axes = Axis.objects.all()
    ranked_axes = []
    for axis in axes:
        try:
            rank = Ranking.objects.get(axis=axis, item=item)
            ranked_axes.append((axis, rank))
        except:
            ranked_axes.append((axis, None))
    
    def gr(x):
        if x:
            return x[1].value
        else:
            return 100000 
    ranked_axes.sort(lambda a, b: cmp(gr(b), gr(a)))

    new_item_form = ItemForm()
    return render_to_response("ranker/item.html",
                             {"item" : item,
                              "item_form" : item_form,
                              "ranked_axes" : ranked_axes,
                              "new_item_form" : new_item_form
                             })

def rank(request, axis_slug="", item_slug=""):
    try:
        axis = Axis.objects.get(slug=axis_slug)
        item = Item.objects.get(slug=item_slug)
    except:
        return page_not_found(request)

    rank = Ranking.objects.get_or_create(item=item, axis=axis)[0]
    if "value" in request.POST:
        try:
            value = float(request.POST["value"])
        except:
            return server_error(request)
        rank.value = value
        rank.save()
    
    return HttpResponse("%0.4f" % rank.value)


def chart(request, axis_x_slug="", axis_y_slug=""):
    try:
        axis_x = Axis.objects.get(slug=axis_x_slug)
        axis_y = Axis.objects.get(slug=axis_y_slug)
    except:
        return page_not_found(request)

    ranks_x = axis_x.rank_set.all()
    ranks_y = axis_y.rank_set.all()
    

    plot_items = {}
    for rank in ranks_x:
        plot_items[rank.item] = (rank,None)
    for rank in ranks_y:
        if rank.item in plot_items:
            plot_items[rank.item] = (plot_items[rank.item][0], rank)
    plot_items = dict(filter(lambda x: x[1][1] is not None, plot_items.items()))
    plot_items = zip(plot_items.keys(), *zip(*plot_items.values()))

    return render_to_response("ranker/chart.html",
                             {"axis_x" : axis_x,
                              "axis_y" : axis_y,
                              "ranks_x" : ranks_x,
                              "ranks_y" : ranks_y,
                              "plot_items" : plot_items
                              })
                                
