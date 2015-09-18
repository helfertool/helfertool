from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class UsernameForm(forms.Form):
    username = forms.CharField(
        label=_('Username'),
        max_length=100,
        required=False,
    )

    instance = None

    def clean(self):
        cleaned_data = super(UsernameForm, self).clean()
        username = cleaned_data.get("username")

        # search for user
        if username:
            try:
                self.instance = User.objects.get(username=username)
            except User.DoesNotExist as e:
                raise forms.ValidationError(_("The user does not exist."))

    def get_user(self):
        return self.instance


class UserCreationForm(UserCreationForm):
    email = forms.EmailField(label=_("Email address"), required=True)
    first_name = forms.CharField(label=_('First name'), max_length=30,
                                 required=True)
    last_name = forms.CharField(label=_('Last name'), max_length=30,
                                required=True)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1",
                  "password2")

    def clean(self):
        # add '@' to the beginning
        if not self.cleaned_data['username'].startswith('@'):
            self.cleaned_data['username'] = '@' + self.cleaned_data['username']

        return super(UserCreationForm, self).clean()

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)

        # change mail and name
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        if commit:
            user.save()

        return user
