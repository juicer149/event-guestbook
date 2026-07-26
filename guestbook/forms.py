from django import forms

from .models import Entry


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = [
            "author_name",
            "message",
        ]
        widgets = {
            "author_name": forms.TextInput(
                attrs={
                    "autocomplete": "name",
                    "placeholder": "Ditt namn",
                },
            ),
            "message": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Skriv något till Simon…",
                },
            ),
        }
