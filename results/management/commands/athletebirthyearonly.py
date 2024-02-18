"""
Changes all birth dates to year only
usage: ./manage.py athletebirthyearonly
"""

from django.core.management.base import BaseCommand

from results.models.athletes import Athlete


class Command(BaseCommand):
    """Approve records"""

    args = "None"
    help = "Approve records"

    def handle(self, *args, **options):
        athletes = Athlete.objects.filter(date_of_birth__isnull=False)
        for athlete in athletes:
            date_of_birth = athlete.date_of_birth.replace(month=1, day=1)
            athlete.date_of_birth = date_of_birth
            athlete.save()
