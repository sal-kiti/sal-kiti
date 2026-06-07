"""
Calculate divari results

usage: ./manage.py divaricalculation
"""

import datetime

from django.core.management.base import BaseCommand

from divari.models import Season
from divari.utils import calculate_season_results


class Command(BaseCommand):
    """Calculate divari results"""

    args = "None"
    help = "Calculate Divari season results."

    def add_arguments(self, parser):
        parser.add_argument(
            "--date",
            type=lambda s: datetime.datetime.strptime(s, "%Y-%m-%d"),
            help="Seasons during date. i.e. 2019-12-31.",
            required=False,
            default=None,
        )

    def handle(self, *args, **options):
        date = options["date"]
        seasons = Season.objects.all()
        if date:
            seasons = seasons.filter(date_start__lte=date, date_end__gte=date)
        for season in seasons:
            calculate_season_results(season)
