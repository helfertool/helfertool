from modeltranslation.translator import translator, TranslationOptions

from .models import Agreement


class AgreementTranslationOptions(TranslationOptions):
    fields = ('name', 'text', )
    required_languages = {'default': ('name', 'text', )}


translator.register(Agreement, AgreementTranslationOptions)
