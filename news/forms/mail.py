from django import forms
from django.conf import settings
from django.core.mail import send_mass_mail
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from ..models import Person


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
        first_language = self.cleaned_data.get('language')
        append_english = self.cleaned_data.get('english')

        if first_language == 'en':
            # english may be set anyway
            append_english = False

        # build mails
        prev_language = translation.get_language()
        base_url = self.request.build_absolute_uri(reverse('index'))

        mails = []
        for person in Person.objects.all():
            text = ""

            if append_english:
                text += render_to_string("news/mail/english.txt")

            text += self._mail_text_language(
                first_language, self.cleaned_data.get("text"), person,
                base_url)

            if append_english:
                text += self._mail_text_language(
                    "en", self.cleaned_data.get("text_en"), person, base_url)

            translation.activate(prev_language)

            text = text.rstrip().lstrip()

            mails.append((subject, text, settings.FROM_MAIL, [person.email]))

        # send mails
        print(mails)
        send_mass_mail(mails)

    def _mail_text_language(self, language, text, person, base_url):
        unsubscribe_url = self.request.build_absolute_uri(
            reverse('news:unsubscribe', args=[person.email]))

        translation.activate(language)

        tmp = ""
        tmp += render_to_string("news/mail/preface.txt", {'url': base_url})
        tmp += text
        tmp += render_to_string("news/mail/end.txt",
                                {'unsubscribe_url': unsubscribe_url})

        return tmp

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
