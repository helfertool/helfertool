from django.db import models
from django.utils.translation import gettext_lazy as _

from copy import deepcopy


class BadgeDefaults(models.Model):
    role = models.ForeignKey(
        "BadgeRole",
        related_name="+",  # no reverse accessor
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Default role"),
    )

    design = models.ForeignKey(
        "BadgeDesign",
        related_name="+",  # no reverse accessor
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Default design"),
    )

    no_default_role = models.BooleanField(
        default=False,
        verbose_name=_("Do not print default roles on badges"),
    )

    def __str__(self):
        if hasattr(self, "badgesettings"):
            return str(self.badgesettings.event)
        return "Badge defaults without settings"

    def duplicate(self):
        new_defaults = deepcopy(self)
        new_defaults.pk = None
        new_defaults.save()

        # design and role are updates in BadgeSettings.duplicate later

        return new_defaults

    def update_after_dup(self, role_map, design_map):
        if self.role:
            self.role = role_map[self.role]
        if self.design:
            self.design = design_map[self.design]
        self.save()
