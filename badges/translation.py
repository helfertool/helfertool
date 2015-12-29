from modeltranslation.translator import translator, TranslationOptions

from .models import BadgePermission, BadgeRole, BadgeDesign


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
