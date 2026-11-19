from django import forms

from .models import Production


class ProductionForm(forms.ModelForm):
    class Meta:
        model = Production
        fields = ["title", "script"]
        widgets = {"script": forms.Textarea(attrs={"rows": 16})}
