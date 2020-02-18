"""
Approve all records from oldest to newest

usage: ./manage.py approverecords
"""

from django.core.management.base import BaseCommand

from results.models.records import Record


class Command(BaseCommand):
    """Approve records"""
    args = 'None'
    help = 'Approve records'

    def handle(self, *args, **options):
        records = Record.objects.filter(date_end=None, approved=False).order_by('date_start', '-result__result')
        for record in records:
            print(str(record) + ": " + str(record.date_start) + ": " + str(record.result.result))
            updated = Record.objects.filter(pk=record.pk, approved=False, date_end=None).first()
            if updated:
                print("Approved record")
                updated.approved = True
                updated.save()
