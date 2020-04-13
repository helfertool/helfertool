from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils.timezone import make_aware

from datetime import datetime


def date(s):
    return datetime.strptime(s, '%Y-%m-%d')


class Command(BaseCommand):
    help = """Disabled accounts which are inactive since the specified time.
    If the account was never logged in, the creation date is checked instead of the login date.

    Accounts from external authentication sources (LDAP, OpenID Connect) are not changed
    as the active flag is synced again from there."""

    def add_arguments(self, parser):
        parser.add_argument('date', type=date,
                            help='Accounts that were not active since this date will be disabled (format: YYYY-MM-DD).')

        parser.add_argument('--dry-run', action='store_true', help='do not really disable the accounts')

    def handle(self, *args, **options):
        date = make_aware(options['date'])
        dry_run = options['dry_run']

        # get users which
        # 1. are still active
        # 2. need to be disabled because
        #    a. last login before deadline
        #    b. never logged in but created before deadline
        for u in User.objects.filter(is_active=True) \
            .filter(Q(last_login__lt=date)
                    | Q(last_login__isnull=True, date_joined__lt=date)):
            # skip users from external authentication providers
            if u.has_usable_password():
                # disable user
                if not dry_run:
                    u.is_active = False
                    u.save()

                # print some nice output
                if u.last_login is None:
                    reason = "never logged in and created at {}".format(u.date_joined)
                else:
                    reason = "last login at {}".format(u.last_login)
                print("{} ({})".format(u.username, reason))
