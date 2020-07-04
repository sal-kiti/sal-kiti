"""
Approve or lock objects from the database
"""
import logging

from dateutil.relativedelta import relativedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from results.models.competitions import Competition
from results.models.events import Event
from results.models.records import Record
from results.models.results import Result

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    list_only = False
    verbosity = 0

    def add_arguments(self, parser):
        parser.add_argument('-d', type=int, action='store', dest='days',
                            help='Date limit for approval or locking, default 30.')
        parser.add_argument('--result', action='store_true', dest='approve_results',
                            help='Approve results which have not been modified during date limit')
        parser.add_argument('--record', action='store_true', dest='approve_records',
                            help='Approve records which have not been modified during date limit')
        parser.add_argument('--event', action='store_true', dest='lock_events',
                            help='Lock past events which have not been modified during date limit')
        parser.add_argument('--competition', action='store_true', dest='lock_competitions',
                            help='Lock past competitions which have not been modified during date limit')
        parser.add_argument('-l', action='store_true', dest='list_only',
                            help='List only, do not approve')

    def output(self, text):
        if self.list_only:
            self.stdout.write("(List only) " + text)
        else:
            if self.verbosity:
                self.stdout.write(text)
            logger.info(text)

    def approve_results(self, date_limit):
        """ Approve results which have not been modified during date limits"""
        for result in Result.objects.filter(updated_at__lt=date_limit, approved=False):
            result.approved = True
            self.output("Result approved: %s" % result)
            if not self.list_only:
                result.save()

    def approve_records(self, date_limit):
        """ Approve records which have not been modified during date limits"""
        for record in Record.objects.filter(updated_at__lt=date_limit, approved=False):
            record.approved = True
            self.output("Record approved: %s" % record)
            if not self.list_only:
                record.save()

    def lock_competitions(self, date_limit):
        """Lock past competitions which have not been modified during date limit"""
        for competition in Competition.objects.filter(date_start__lte=date_limit,
                                                      updated_at__lt=date_limit,
                                                      locked=False):
            competition.locked = True
            self.output("Competition locked: %s" % competition)
            if not self.list_only:
                competition.save()

    def lock_events(self, date_limit):
        """Lock past events which have not been modified during date limit"""
        for event in Event.objects.filter(date_start__lte=date_limit,
                                          updated_at__lt=date_limit,
                                          locked=False):
            event.locked = True
            self.output("Event locked: %s" % event)
            if not self.list_only:
                event.save()

    def handle(self, *args, **options):
        days = options['days']
        approve_results = options['approve_results']
        approve_records = options['approve_records']
        lock_competitions = options['lock_competitions']
        lock_events = options['lock_events']
        self.verbosity = options['verbosity']
        self.list_only = options['list_only']
        # Set date range to one year if not given
        if days is None:
            days = 30
        if days >= 0:
            date_limit = timezone.now() - relativedelta(days=days)
            if approve_results:
                self.approve_results(date_limit)
            if approve_records:
                self.approve_records(date_limit)
            if lock_competitions:
                self.lock_competitions(date_limit)
            if lock_events:
                self.lock_events(date_limit)
        else:
            self.stderr.write("Error: -d must be positive")