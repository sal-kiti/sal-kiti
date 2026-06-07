"""
Check all results for records from oldest to newest

usage: ./manage.py checkrecords
"""

from datetime import date

from django.core.management.base import BaseCommand

from results.models.results import Result, ResultPartial
from results.utils.records import check_records, check_records_partial


class Command(BaseCommand):
    """Approve records"""

    args = "None"
    help = "Approve records"

    def __init__(self):
        super().__init__()
        self.verbosity = 0
        self.sports = []
        self.competition_types = []
        self.competition_levels = []
        self.date = None

    def add_arguments(self, parser):
        parser.add_argument(
            "-r",
            "--results",
            action="store_true",
            dest="check_results",
            help="Check results",
        )
        parser.add_argument(
            "-p",
            "--partial",
            action="store_true",
            dest="check_partial_results",
            help="Check partial results",
        )
        parser.add_argument(
            "-s",
            "--sports",
            nargs="+",
            default=[],
            help="Checks only these sports (abbreviations)",
        )
        parser.add_argument(
            "-c",
            "--competition_types",
            nargs="+",
            default=[],
            help="Checks only these competition type (abbreviations)",
        )
        parser.add_argument(
            "-l",
            "--competition_levels",
            nargs="+",
            default=[],
            help="Checks only these competition levels (abbreviations)",
        )
        parser.add_argument(
            "-d",
            "--date",
            type=date.fromisoformat,
            default=None,
            help="Checks only results greater and equal to given date (ISO format, e.g. 2024-01-01)",
        )

    def get_queryset(self, queryset, prefix=""):
        q = queryset.filter(**{f"{prefix}organization__external": False})
        if self.sports:
            q = q.filter(**{f"{prefix}competition__type__sport__abbreviation__in": self.sports})
        if self.competition_types:
            q = q.filter(**{f"{prefix}competition__type__abbreviation__in": self.competition_types})
        if self.competition_levels:
            q = q.filter(**{f"{prefix}competition__level__abbreviation__in": self.competition_levels})
        if self.date:
            q = q.filter(**{f"{prefix}competition__date_start__gte": self.date})
        return q

    def check_results(self):
        results = self.get_queryset(Result.objects.all())
        results = results.order_by("competition__date_start", "-result")
        for result in results:
            if self.verbosity > 1:
                self.stdout.write(f"Checking result {result}")
            created = check_records(result)
            if created and self.verbosity:
                self.stdout.write(f"Created {len(created)} record(s) for result {result}")

    def check_partial_results(self):
        partials = self.get_queryset(ResultPartial.objects.all(), prefix="result__")
        partials = partials.order_by("result__competition__date_start", "-value")
        for partial in partials:
            if self.verbosity > 1:
                self.stdout.write(f"Checking partial result {partial}")
            created = check_records_partial(partial)
            if created and self.verbosity:
                self.stdout.write(f"Created {len(created)} record(s) for partial result {partial}")

    def handle(self, *args, **options):
        self.verbosity = options.get("verbosity")
        check_results = options.get("check_results")
        check_partial_results = options.get("check_partial_results")
        self.sports = options.get("sports")
        self.competition_types = options.get("competition_types")
        self.competition_levels = options.get("competition_levels")
        self.date = options.get("date")
        if check_results:
            self.check_results()
        if check_partial_results:
            self.check_partial_results()
