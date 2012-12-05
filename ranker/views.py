from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.views.defaults import page_not_found, server_error
from django.http import HttpResponse, Http404
from django.db.models import Count
from django.template import RequestContext
from django.contrib import messages
from django.utils import simplejson

from models import *
from forms import *

def index(request):
    user = request.user if request.user.is_authenticated() else None
    games = Game.objects.filter(plotter__isnull=False)[:5]
    inactive_games = Game.objects.filter(plotter__isnull=True)

    new_game_form = NewGameForm(prefix="new-game")
    axis_form = AxisForm(prefix="axis")
    item_form = ItemForm(prefix="item")
    if request.method == "POST" and user:
        # Submitted new game/axis/item
        if request.POST["new-game-submit"]:
            new_game_form = NewGameForm(request.POST, prefix="new-game")
        if new_game_form.is_valid():
            new_game = Game(title=new_game_form.cleaned_data["title"])
            new_game.save()
            for ax in new_game_form.cleaned_data["axes"]:
                g_ax = GameAxis(game=new_game, axis=ax)
                g_ax.save()
            return redirect(new_game) #TODO: need to claim?

        if request.POST["axis-submit"]:
            axis_form = AxisForm(request.POST, prefix="axis")
        if axis_form.is_valid():
            axis = axis_form.save()
            messages.info(request, "Created axis '%s'" % axis.title)

        if request.POST["item-submit"]:
            item_form = ItemForm(request.POST, prefix="item")
        if item_form.is_valid():
            item = item_form.save()
            messages.info(request, "Created item '%s'" % item.title)
            
    return render_to_response("ranker/index.html", 
                             {"games": games,
                              "inactive_games": inactive_games,
                              "user": user,
                              "new_game_form": new_game_form,
                              "axis_form": axis_form,
                              "item_form": item_form
                             },context_instance=RequestContext(request))

def game(request, game_slug=""):
    user = request.user if request.user.is_authenticated() else None
    game = get_object_or_404(Game, slug=game_slug)
    x_axis, y_axis = game.x_axis, game.y_axis

    if request.method == "POST" and user:
        if game.plotter:
            guess_form = GuessAxesForm(game, request.POST)
            if guess_form.is_valid():
                data = guess_form.cleaned_data
                guess = Guess(user=user, game=game)
                guess.save()
                x_gax = data["x_axis"]
                y_gax = data["y_axis"]
                x_guess = GuessAxis(guess=guess, axis=x_gax.axis, direction="x")
                y_guess = GuessAxis(guess=guess, axis=y_gax.axis, direction="y")
                x_guess.save()
                y_guess.save()
                if x_gax.axis == game.x_axis and y_gax.axis == game.y_axis:
                    guess.correct = True
                    guess.save()
                    messages.info("Correct guess!")
                else:
                    messages.error("Incorrect guess!")

                
        else:
            claim_game_form = ClaimGameForm(game, request.POST)
            if claim_game_form.is_valid():
                data = claim_game_form.cleaned_data
                x_gax = data["x_axis"]
                y_gax = data["y_axis"]
                x_gax.direction = "x"
                y_gax.direction = "y"
                x_gax.save()
                y_gax.save()
                game.plotter = user
                game.save()
    else:
        claim_game_form = ClaimGameForm(game)
        guess_form = GuessAxesForm(game)

    return render_to_response("ranker/game.html",
                             {"game": game,
                              "user": user,
                              "x_axis": x_axis,
                              "y_axis": y_axis,
                              "claim_game_form": claim_game_form,
                              "guess_form": guess_form
                             }, context_instance=RequestContext(request))


def to_json_to_response(jsondata):
    return HttpResponse(simplejson.dumps(jsondata), mimetype="application/json")

def json_data(request):
    """Dump a json object with axes and items""" 
    axes = [(ax.title, ax.slug) for ax in Axis.objects.all()]
    items = [(it.title, it.slug) for it in Item.objects.all()]
    return to_json_to_response({"axes": axes, "items": items})
