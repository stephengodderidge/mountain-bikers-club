from django import forms
from django.forms import TextInput

from .models import Trail


class GpxUploadForm(forms.ModelForm):
    class Meta:
        model = Trail
        fields = ('file',)

    def save(self, commit=True):
        trail = super().save(commit=False)
        if commit:
            trail.save()
        return trail


class GpxEditForm(forms.ModelForm):
    class Meta:
        model = Trail
        fields = ('name', 'description')
        widgets = {
            'name': TextInput(attrs={'autofocus': True})
        }

    def save(self, commit=True):
        trail = super().save(commit=False)
        if commit:
            trail.save()
        return trail
