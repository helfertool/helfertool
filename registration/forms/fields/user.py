from .duallist import DualListField

class UserSelectField(DualListField):
    def label_from_instance(self, obj):
        if obj.first_name and obj.last_name:
            return obj.get_full_name()
        return obj.get_username()
