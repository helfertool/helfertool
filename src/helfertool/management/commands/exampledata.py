from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from django.utils.timezone import make_aware

from datetime import date, datetime, time

from registration.models import Event, Job, Shift
from gifts.models import Gift, GiftSet, IncludedGift
from badges.models import BadgePermission, BadgeRole, BadgeDesign
from prerequisites.models import Prerequisite


class Command(BaseCommand):
    help = "Add an example event (no inventory settings are changed as these are global)"

    def handle(self, *args, **options):
        event_date = date.today()

        try:
            # create event
            event = Event.objects.create(
                name="Test Event",
                url_name="test",
                date=event_date,
                max_overlapping=15,
                badges=True,
                gifts=True,
                prerequisites=True,
                inventory=True,
            )

            # gifts
            event.giftsettings.default_deposit = 10
            event.giftsettings.save()

            gifts = []
            for i in range(2):
                gift = Gift.objects.create(
                    event=event,
                    name_en="Gift {}".format(i+1),
                    name_de="Geschenk {}".format(i+1),
                )
                gifts.append(gift)

            giftsets = []
            for i in range(2):
                giftset = GiftSet.objects.create(
                    event=event,
                    name_en="Gift set {}".format(i+1),
                    name_de="Geschenkset {}".format(i+1),
                )
                giftsets.append(giftset)

            IncludedGift.objects.create(
                gift_set=giftsets[0],
                gift=gifts[0],
                count=1,
            )
            IncludedGift.objects.create(
                gift_set=giftsets[0],
                gift=gifts[1],
                count=2,
            )
            IncludedGift.objects.create(
                gift_set=giftsets[1],
                gift=gifts[0],
                count=1,
            )

            # badges
            badge_perm_food = BadgePermission.objects.create(
                badge_settings=event.badgesettings,
                name_en="Food",
                name_de="Verpflegung",
                latex_name="food",
            )

            badge_perm_finance = BadgePermission.objects.create(
                badge_settings=event.badgesettings,
                name_en="Finance",
                name_de="Finanzen",
                latex_name="finance",
            )

            badge_role_default = BadgeRole.objects.create(
                badge_settings=event.badgesettings,
                name_en="Default",
                name_de="Default",
                latex_name="default",
            )
            badge_role_default.permissions.add(badge_perm_food)

            badge_role_coordinators = BadgeRole.objects.create(
                badge_settings=event.badgesettings,
                name_en="Coordinators",
                name_de="Koordinatoren",
                latex_name="coordinators",
            )
            badge_role_coordinators.permissions.add(badge_perm_food)
            badge_role_coordinators.permissions.add(badge_perm_finance)

            badge_design = BadgeDesign.objects.create(
                badge_settings=event.badgesettings,
                name_en="Default",
                name_de="Default",
            )

            f = open(settings.BADGE_DEFAULT_TEMPLATE)
            event.badgesettings.latex_template.save("template.tex", File(f))

            event.badgesettings.coordinator_title = "Coordinator"
            event.badgesettings.helper_title = "Helper"
            event.badgesettings.barcodes = True
            event.badgesettings.save()

            event.badgesettings.defaults.role = badge_role_default
            event.badgesettings.defaults.design = badge_design
            event.badgesettings.defaults.save()

            # prerequisites
            prerequisite = Prerequisite.objects.create(
                event=event,
                name_en="Training",
                name_de="Schulung",
            )

            # create some jobs and shifts
            for j in ["A", "B", "C"]:
                job = Job.objects.create(
                    event=event,
                    name_en="Job {}".format(j),
                    name_de="Aufgabe {}".format(j),
                    public=True,
                )

                # create shifts
                for s in range(3):
                    shift = Shift.objects.create(
                        job=job,
                        begin=make_aware(datetime.combine(event_date, time(9+s*2, 45))),
                        end=make_aware(datetime.combine(event_date, time(12+s*2, 0))),
                        number=100,
                    )

                    shift.gifts.add(giftsets[0])
                    if s == 0:
                        shift.gifts.add(giftsets[1])

                # add prerequisite
                if j == "A":
                    job.prerequisites.add(prerequisite)
        except IntegrityError:
            raise CommandError("Test event exists already")

        self.stdout.write(self.style.SUCCESS("Created event: test"))
