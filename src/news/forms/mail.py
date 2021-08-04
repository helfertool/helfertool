from django import forms
from django.conf import settings
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from .. import tasks

import re


class MailForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')

        super(MailForm, self).__init__(*args, **kwargs)

        self.languages = self._get_languages()

        self.fields['language'] = forms.ChoiceField(
            choices=self.languages,
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
            required=False,  # will be checked in clean
        )

    def clean(self):
        cleaned_data = super(MailForm, self).clean()

        if cleaned_data.get('language') != 'en' and \
                cleaned_data.get('english') and \
                not cleaned_data.get("text_en"):
            self.add_error('text_en', _("This field is required."))

        return cleaned_data

    def send_mail(self):
        subject = self.cleaned_data.get('subject')
        text = self.cleaned_data.get('text')
        text_en = self.cleaned_data.get('text_en')

        first_language = self.cleaned_data.get('language')
        append_english = self.cleaned_data.get('english')
        if first_language == 'en':
            # english may be set anyway
            append_english = False

        unsubscribe_url = self.request.build_absolute_uri(
            reverse('news:unsubscribe', args=[""]))
        # since args is empty, the URL ends with // (this is a dirty trick to get the base URL for unsubscribe)
        unsubscribe_url = re.sub("//$", "/", unsubscribe_url)

        tasks.send_news_mails.delay(first_language, append_english, subject,
                                    text, text_en, unsubscribe_url)

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
