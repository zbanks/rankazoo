from django import forms
from models import *

class NewGameForm(forms.Form):
    title = forms.CharField(max_length=80)
    axes = forms.ModelMultipleChoiceField(queryset=Axis.objects.all())
    def clean_axes(self):
        data = self.cleaned_data["axes"]
        if len(data) != 5: # Change to 5 +/- 1?
            raise forms.ValidationError("Each game needs exactly 5 axes")
        return data


class ClaimGameForm(forms.Form):
    x_axis = forms.ModelChoiceField(queryset=GameAxis.objects.none(), empty_label=None)
    y_axis = forms.ModelChoiceField(queryset=GameAxis.objects.none(), empty_label=None)

    def __init__(self, game, *args, **kwargs):
        super(ClaimGameForm, self).__init__(*args, **kwargs)
        self.fields["x_axis"].queryset = game.gameaxis_set.all()
        self.fields["y_axis"].queryset = game.gameaxis_set.all()

    def clean(self):
        cleaned_data = super(ClaimGameForm, self).clean()
        if cleaned_data["x_axis"] == cleaned_data["y_axis"]:
            raise forms.ValidationError("X and Y axis must be different")
        return cleaned_data

class ModelFormCleanSlug(forms.ModelForm):
    def clean_slug(self):
        data = self.cleaned_data["slug"]
        if self.model.objects.filter(slug=data).exists():
            raise forms.ValidationError("Title insufficiently different from another axis")

class AxisForm(ModelFormCleanSlug):
    class Meta:
        model = Axis
        fields = ('title',)

class ItemForm(ModelFormCleanSlug):
    class Meta:
        model = Item
        fields = ('title',)

class GuessAxesForm(forms.Form):
    x_axis_guess = forms.ModelChoiceField(queryset=GameAxis.objects.none(), empty_label=None)
    y_axis_guess = forms.ModelChoiceField(queryset=GameAxis.objects.none(), empty_label=None)
    def __init__(self, game, *args, **kwargs):
        super(GuessAxesForm, self).__init__(*args, **kwargs)
        self.fields["x_axis_guess"].queryset = game.gameaxis_set.all()
        self.fields["y_axis_guess"].queryset = game.gameaxis_set.all()


