from modeltranslation.translator import translator, TranslationOptions

from .models import Event, Job, BadgePermission, BadgeRole, BadgeDesign


class EventTranslationOptions(TranslationOptions):
    fields = ('text', 'imprint', 'registered', )

translator.register(Event, EventTranslationOptions)


class JobTranslationOptions(TranslationOptions):
    fields = ('name', 'description', )
    required_languages = {'default': ('name',)}

translator.register(Job, JobTranslationOptions)


class BadgePermissionTranslationOptions(TranslationOptions):
    fields = ('name', )
    required_languages = {'default': ('name',)}

translator.register(BadgePermission, BadgePermissionTranslationOptions)


class BadgeRoleTranslationOptions(TranslationOptions):
    fields = ('name', )
    required_languages = {'default': ('name',)}

translator.register(BadgeRole, BadgeRoleTranslationOptions)

class BadgeDesignTranslationOptions(TranslationOptions):
    fields = ('name', )
    required_languages = {'default': ('name',)}

translator.register(BadgeDesign, BadgeDesignTranslationOptions)
