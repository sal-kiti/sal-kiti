"""
Check all results for records from oldest to newest

usage: ./manage.py checkrecords
"""

from django.core.management.base import BaseCommand

from results.models.results import Result
from results.utils.records import check_records, check_records_partial


class Command(BaseCommand):
    """Approve records"""
    args = 'None'
    help = 'Approve records'

    def handle(self, *args, **options):
        results = Result.objects.filter(organization__external=False).order_by('competition__date_start', '-result')
        for result in results:
            check_records(result)
            for partial in result.partial.all():
                check_records_partial(partial)
