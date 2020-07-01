"""
Update athletes and licences from Suomisport

usage: ./manage.py suomisportimport
"""

from django.core.management.base import BaseCommand
from results.connectors.suomisport import Suomisport

from sys import stderr


class Command(BaseCommand):
    """Approve records"""
    args = 'None'
    help = 'Import athletes and licences from Suomisport'

    def add_arguments(self, parser):
        parser.add_argument('-a',
                            action='store_true',
                            default=False,
                            dest='update_all',
                            help='Update all athletes and licences. Updates only new by default.')
        parser.add_argument('-y',
                            action='store_true',
                            default=False,
                            dest='only_year',
                            help='Set day and month of birth date as YYYY-01-01.')

    def handle(self, *args, **options):
        update_only_latest = not options['update_all']
        only_year = options['only_year']
        try:
            suomisport = Suomisport()
            suomisport.update_licences(update_only_latest=update_only_latest, print_to_stdout=True, only_year=only_year)
        except Exception as e:
            stderr.write('Cloud not update licences. Most likely API credentials are incorrect.\n')
            stderr.write('Error: %s\n' % e)
