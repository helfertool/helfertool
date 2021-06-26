from django.utils.translation import ugettext_lazy as _

# Django uses the first translation it detects in an installed app.
# The "helfertool" app is listed first, so we have can override default translations here.
#
# Just put the english text here and translate it, this vesion will be used.
# There is no other purpose of this file, it is not included anywhere.

override_translations = [
    _("User"),
]
