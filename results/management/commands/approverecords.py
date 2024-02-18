"""
Approve all records from oldest to newest

usage: ./manage.py approverecords
"""

import datetime

from django.core.management.base import BaseCommand

from results.models.records import Record


class Command(BaseCommand):
    """Approve records"""

    args = "None"
    help = "Approve records"

    def add_arguments(self, parser):
        parser.add_argument(
            "date",
            type=lambda s: datetime.datetime.strptime(s, "%Y-%m-%d"),
            help="Approve up to date, i.e. 2019-12-31.",
        )

    def handle(self, *args, **options):
        date = options["date"]

        def approve_records(records):
            for record in records:
                print(str(record) + ": " + str(record.date_start) + ": " + str(record.result.result))
                updated = Record.objects.filter(pk=record.pk, approved=False, date_end=None).first()
                if updated:
                    print("Approved record")
                    updated.approved = True
                    updated.save()

        if date:
            record_list = Record.objects.filter(
                date_end=None, approved=False, partial_result=None, date_start__lte=date
            ).order_by("date_start", "-result__result")
        else:
            record_list = Record.objects.filter(date_end=None, partial_result=None, approved=False).order_by(
                "date_start", "-result__result"
            )
        approve_records(record_list)
        if date:
            record_list = Record.objects.filter(date_end=None, approved=False, date_start__lte=date).order_by(
                "date_start", "-partial_result__value"
            )
        else:
            record_list = Record.objects.filter(date_end=None, approved=False).order_by(
                "date_start", "-partial_result__value"
            )
        approve_records(record_list)
