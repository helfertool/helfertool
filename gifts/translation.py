from modeltranslation.translator import translator, TranslationOptions

from .models import Gift, GiftSet


class GiftTranslationOptions(TranslationOptions):
    fields = ('name', )
    required_languages = {'default': ('name',)}

translator.register(Gift, GiftTranslationOptions)


class GiftSetTranslationOptions(TranslationOptions):
    fields = ('name', )
    required_languages = {'default': ('name',)}

translator.register(GiftSet, GiftSetTranslationOptions)
