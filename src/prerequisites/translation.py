from modeltranslation.translator import translator, TranslationOptions

from .models import Prerequisite


class PrerequisiteTranslationOptions(TranslationOptions):
    fields = (
        "name",
        "description",
    )
    required_languages = {"default": ("name",)}


translator.register(Prerequisite, PrerequisiteTranslationOptions)
