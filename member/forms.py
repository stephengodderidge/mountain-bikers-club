from django import forms
from django.contrib.auth.forms import UserCreationForm as DefaultUserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import User


forbidden_username = [
    'superuser',
    'member'
]


class UserCreateForm(DefaultUserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ('username', 'email', 'password1', 'password2'):
            self.fields[field].widget.attrs['autocapitalize'] = 'off'
            self.fields[field].widget.attrs['autocorrect'] = 'off'
            self.fields[field].widget.attrs['spellcheck'] = 'false'
            if not field.startswith('pass'):
                self.fields[field].widget.attrs['autocomplete'] = field

    class Meta:
        model = User
        fields = DefaultUserCreationForm.Meta.fields + ('email',)

    def clean_username(self):
        username = self.cleaned_data['username']

        if username in forbidden_username or username.startswith('admin'):
            raise forms.ValidationError(_("This username is forbidden."))

        return username


class UserProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ('username', 'first_name', 'last_name', 'email'):
            self.fields[field].widget.attrs['autocapitalize'] = 'off'
            self.fields[field].widget.attrs['autocorrect'] = 'off'
            self.fields[field].widget.attrs['spellcheck'] = 'false'
            self.fields[field].widget.attrs['autocomplete'] = field
        self.fields['first_name'].widget.attrs['autofocus'] = 'true'

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean_username(self):
        username = self.cleaned_data['username']

        if username in forbidden_username or username.lower().startswith('admin'):
            raise forms.ValidationError(_("This username is forbidden."))

        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user
