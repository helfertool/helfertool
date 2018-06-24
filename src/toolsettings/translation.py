from modeltranslation.translator import translator, TranslationOptions

from .models import HTMLSetting, TextSetting


class HTMLTranslationOptions(TranslationOptions):
    fields = ('value', )


translator.register(HTMLSetting, HTMLTranslationOptions)


class TextTranslationOptions(TranslationOptions):
    fields = ('value', )


translator.register(TextSetting, TextTranslationOptions)
