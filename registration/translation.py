from modeltranslation.translator import translator, TranslationOptions

from .models import Event, Job


class EventTranslationOptions(TranslationOptions):
    fields = ('text', 'imprint', 'registered', )

translator.register(Event, EventTranslationOptions)


class JobTranslationOptions(TranslationOptions):
    fields = ('name', 'description', )
    required_languages = {'default': ('name',)}

translator.register(Job, JobTranslationOptions)
