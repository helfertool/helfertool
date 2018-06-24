def get_setting(setting_class, key, default=None):
    try:
        setting = setting_class.objects.get(key=key)
        return setting.value
    except setting_class.DoesNotExist:
        return default
