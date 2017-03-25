from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class MailForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(MailForm, self).__init__(*args, **kwargs)

        self.languages = self._get_languages()

        self.fields['language'] = forms.ChoiceField(
            choices = self.languages,
            label=_("Language"),
        )
        self.fields['language'].widget.attrs['onChange'] = 'handle_lang()'

        self.fields['english'] = forms.BooleanField(
            label=_("Add English text"),
            initial=True,
            required=False,
        )
        self.fields['english'].widget.attrs['onChange'] = 'handle_lang()'

        self.fields['subject'] = forms.CharField(
            label=_("Subject"),
            max_length=200,
        )

        self.fields["text"] = forms.CharField(
            widget=forms.Textarea,
            label=_("Text"),
        )

        self.fields["text_en"] = forms.CharField(
            widget=forms.Textarea,
            label=_("English text"),
        )

    def send_mail(self):
        pass

    def _get_languages(self):
        """
        Returns available languages, the first entry is the default language.
        """
        langs = []

        for lang, name in settings.LANGUAGES:
            if lang == settings.LANGUAGE_CODE:
                langs.insert(0, (lang, name))
            else:
                langs.append((lang, name))

        return langs
