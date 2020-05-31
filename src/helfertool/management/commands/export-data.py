#!/usr/bin/env python3

import sys
import hashlib
import csv
import string

from django.core.management.base import BaseCommand, CommandError
from registration.models import Event, HelperShift
from gifts.models import HelpersGifts, DeservedGiftSet

def hash(data):
    m = hashlib.sha256()
    m.update(str(data).encode())
    return m.hexdigest()

def printable(data):
    return ''.join(filter(lambda x: x in string.printable, data))

class Command(BaseCommand):
    """
    Export an event, and anonymize the helper mapping by hashing the helper ids
    will export to the current directory / <event name>
    """
    def add_arguments(self, parser):
        parser.add_argument('url_name', type=str, help="event_url_name to export")

    def handle(self, *args, **options):
        event_name = options["url_name"]

        try:
            event = Event.objects.get(url_name=event_name)
            print("Using event {event.name} starting at {event.date}".format(**locals()))
        except Event.DoesNotExist:
            print("No event found with id {event_name}".format(**locals()))
            return -1

        print("Exporting helpers to {event_name}/helper.csv...".format(**locals()))
        with open("{event_name}/helper.csv".format(**locals()), 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=";")
            writer.writerow(["pk", "shirt", "vegetarian", "infection_instruction", "timestamp", "validated"])
            for h in event.helper_set.all():
                writer.writerow([hash(h.pk), h.shirt, h.vegetarian, h.infection_instruction, h.timestamp, h.validated])

        print("Exporting jobs to {event_name}/jobs.csv...".format(**locals()))
        with open("{event_name}/jobs.csv".format(**locals()), 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=";")
            writer.writerow(["pk", "name", "infection_instruction"])
            for j in event.job_set.all():
                writer.writerow([j.pk, printable(j.name), j.infection_instruction])

        print("Exporting shifts to {event_name}/shifts.csv...".format(**locals()))
        with open("{event_name}/shifts.csv".format(**locals()), 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=";")
            writer.writerow(["pk", "job_pk", "name", "begin", "end", "number"])
            for j in event.job_set.all():
                for s in j.shift_set.all():
                    writer.writerow([s.pk, j.pk, printable(s.name), s.begin, s.end, s.number])

        print("Exporting helper shifts to {event_name}/helper_shifts.csv...".format(**locals()))
        with open("{event_name}/helper_shifts.csv".format(**locals()), 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=";")
            writer.writerow(["helper_pk", "shift_pk", "timestamp"])
            for j in event.job_set.all():
                for s in j.shift_set.all():
                    for h in HelperShift.objects.filter(shift=s):
                        writer.writerow([hash(h.helper.pk), s.pk, h.timestamp])

        print("Exporting helper gifts to {event_name}/helper_gifts.csv...".format(**locals()))
        with open("{event_name}/helper_gifts.csv".format(**locals()), 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=";")
            gifttypes = [ g.name for g in event.gift_set.all()]
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

                    data = [ gifts[name] for name in gifttypes ]
                    writer.writerow([hash(h.pk)] + data)

                except HelpersGifts.DoesNotExist:
                    pass
        print("Done.")
