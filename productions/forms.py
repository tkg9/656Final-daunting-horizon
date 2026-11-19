from django import forms

from .models import Production


class ProductionForm(forms.ModelForm):
    class Meta:
        model = Production
        fields = ["title"]


class ScriptForm(forms.Form):
    script = forms.CharField(widget=forms.Textarea(attrs={"rows": 16}), max_length=500_000)
