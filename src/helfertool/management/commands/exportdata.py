#!/usr/bin/env python3

import csv
import hashlib
import os
import string

from django.core.management.base import BaseCommand, CommandError

from registration.models import Event, HelperShift
from gifts.models import HelpersGifts


def hash(data, salt):
    m = hashlib.pbkdf2_hmac("sha256", str(data).encode(), salt, 1000)
    return m.hex()


def printable(data):
    return ''.join(filter(lambda x: x in string.printable, data))


class Command(BaseCommand):
    """
    Export anonymized helper data of an event. The UUIDs of helpers are hashed and most personal data is not exported.
    The following personal data is exported: shirt sizes, vegetarian, infection_instruction.

    The command will export multiple CSV files into a directory (optionally specified with --output).

    The CSV files are meant for data analysis without leaking any personal data.
    Nevertheless, please review the files before giving them to someone!
    """
    def add_arguments(self, parser):
        parser.add_argument('event_url_name', type=str, help="URL name of the event")
        parser.add_argument('--output', type=str, help='The output directory (default: URL name of exported event)')

    def handle(self, *args, **options):
        event_url_name = options["event_url_name"]
        output_dir = options["output"]

        salt = os.urandom(16)

        # get event
        try:
            event = Event.objects.get(url_name=event_url_name)
            print("Using event {event.name} starting at {event.date}".format(**locals()))
        except Event.DoesNotExist:
            raise CommandError('Event "%s" does not exist' % event_url_name)

        # create output directory
        if not output_dir:
            output_dir = event_url_name

        try:
            os.mkdir(output_dir)
        except FileExistsError:
            pass

        # export
        print("Exporting helpers to {output_dir}/helper.csv...".format(**locals()))
        with open("{output_dir}/helper.csv".format(**locals()), 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=";")
            writer.writerow(["pk", "shirt", "vegetarian", "infection_instruction", "timestamp", "validated"])
            for h in event.helper_set.all():
                writer.writerow([hash(h.pk, salt), h.shirt, h.vegetarian, h.infection_instruction, h.timestamp,
                                 h.validated])

        print("Exporting jobs to {output_dir}/jobs.csv...".format(**locals()))
        with open("{output_dir}/jobs.csv".format(**locals()), 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=";")
            writer.writerow(["pk", "name", "infection_instruction"])
            for j in event.job_set.all():
                writer.writerow([j.pk, printable(j.name), j.infection_instruction])

        print("Exporting shifts to {output_dir}/shifts.csv...".format(**locals()))
        with open("{output_dir}/shifts.csv".format(**locals()), 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=";")
            writer.writerow(["pk", "job_pk", "name", "begin", "end", "number"])
            for j in event.job_set.all():
                for s in j.shift_set.all():
                    writer.writerow([s.pk, j.pk, printable(s.name), s.begin, s.end, s.number])

        print("Exporting helper shifts to {output_dir}/helper_shifts.csv...".format(**locals()))
        with open("{output_dir}/helper_shifts.csv".format(**locals()), 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=";")
            writer.writerow(["helper_pk", "shift_pk", "timestamp"])
            for j in event.job_set.all():
                for s in j.shift_set.all():
                    for h in HelperShift.objects.filter(shift=s):
                        writer.writerow([hash(h.helper.pk, salt), s.pk, h.timestamp])

        print("Exporting helper gifts to {output_dir}/helper_gifts.csv...".format(**locals()))
        with open("{output_dir}/helper_gifts.csv".format(**locals()), 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=";")
            gifttypes = [g.name for g in event.gift_set.all()]
            writer.writerow(["helper_pk"] + [printable(g) for g in gifttypes])
            for h in event.helper_set.all():
                gifts = dict.fromkeys(gifttypes, 0)
                try:
                    hg = HelpersGifts.objects.get(helper=h)
                    hg.update()

                    for deserved in hg.deservedgiftset_set.all():
                        for gift in deserved.gift_set.gifts.all():
                            num = deserved.gift_set.get_gift_num(gift)
                            name = gift.name
                            gifts[name] += num

                    data = [gifts[name] for name in gifttypes]
                    writer.writerow([hash(h.pk, salt)] + data)

                except HelpersGifts.DoesNotExist:
                    pass

        print("Done.")
