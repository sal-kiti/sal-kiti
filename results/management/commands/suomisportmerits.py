"""
Get merits from Suomisport

usage: ./manage.py suomisportmerits
"""

from sys import stderr

from django.core.management.base import BaseCommand

from results.connectors.suomisport import Suomisport


class Command(BaseCommand):
    """Get merits"""

    args = "None"
    help = "Update judge merits from Suomisport to Kiti"

    def handle(self, *args, **options):
        try:
            suomisport = Suomisport()
            suomisport.update_judge_merits(print_to_stdout=True)
        except Exception as e:
            stderr.write("Cloud not get merit groups. Most likely API credentials are incorrect.\n")
            stderr.write("Error: %s\n" % e)
