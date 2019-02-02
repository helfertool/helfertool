from modeltranslation.translator import translator, TranslationOptions

from .models import Agreement


class AgreementTranslationOptions(TranslationOptions):
    fields = ('name', 'text', )


translator.register(Agreement, AgreementTranslationOptions)
