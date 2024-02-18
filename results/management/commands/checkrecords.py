"""
Check all results for records from oldest to newest

usage: ./manage.py checkrecords
"""

from django.core.management.base import BaseCommand

from results.models.results import Result, ResultPartial
from results.utils.records import check_records, check_records_partial


class Command(BaseCommand):
    """Approve records"""

    args = "None"
    help = "Approve records"

    def handle(self, *args, **options):
        verbosity = options.get("verbosity")
        results = Result.objects.filter(organization__external=False).order_by("competition__date_start", "-result")
        for result in results:
            if verbosity:
                print(result)
            check_records(result)
        partials = ResultPartial.objects.filter(result__organization__external=False).order_by(
            "result__competition__date_start", "-value"
        )
        for partial in partials:
            if verbosity:
                print(partial)
            check_records_partial(partial)
