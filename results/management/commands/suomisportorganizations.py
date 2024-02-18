"""
Get organizations from Suomisport

usage: ./manage.py suomisportorganizations
"""

from sys import stderr

from django.core.management.base import BaseCommand

from results.connectors.suomisport import Suomisport


class Command(BaseCommand):
    """Approve records"""

    args = "None"
    help = "Get organizations from Suomisport"

    def handle(self, *args, **options):
        try:
            suomisport = Suomisport()
            suomisport.get_organizations(print_to_stdout=True)
        except Exception as e:
            stderr.write("Cloud not get organizations. Most likely API credentials are incorrect.\n")
            stderr.write("Error: %s\n" % e)
