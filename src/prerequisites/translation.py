from modeltranslation.translator import translator, TranslationOptions

from .models import Prerequisite


class PrerequisiteTranslationOptions(TranslationOptions):
    fields = ('long_name', 'description', )


translator.register(Prerequisite, PrerequisiteTranslationOptions)
