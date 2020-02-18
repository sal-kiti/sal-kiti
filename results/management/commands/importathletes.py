"""
Import athletes from CSV

usage: ./manage.py importathletes -i <file>

<file> is a CSV file with following format:
sport_id,first_name,last_name,date_of_birth[YYYY-MM-DD],gender[M/W/O/U],organization_id

File may contain athlete multiple times, in different organizations
"""
import csv

from datetime import datetime

from django.core.management.base import BaseCommand

from results.models.athletes import Athlete
from results.models.organizations import Organization


class Command(BaseCommand):
    """Approve records"""
    args = 'None'
    help = 'Approve records'

    def add_arguments(self, parser):
        parser.add_argument('-i', type=str, action='store',
                            dest='input', help='Import file')

    def _create_athlete(self, row, date_of_birth, organization):
        athlete = Athlete.objects.create(sport_id=row[0],
                                         first_name=row[2],
                                         last_name=row[1],
                                         date_of_birth=date_of_birth,
                                         gender=row[4],
                                         organization=organization)
        if self.verbosity > 0:
            print("Created athlete: %s, %s %s" % (athlete.sport_id, athlete.first_name, athlete.last_name))
        self.athletes.add(row[0])

    def _update_athlete(self, row, athlete, date_of_birth, organization):
        if athlete.first_name != row[2]:
            athlete.first_name = row[2]
            if self.verbosity > 1:
                print("Update first name for athlete: %s, %s %s" % (
                    athlete.sport_id, athlete.first_name, athlete.last_name))
        if athlete.last_name != row[1]:
            athlete.last_name = row[1]
            if self.verbosity > 1:
                print("Update last name for athlete: %s, %s %s" % (
                    athlete.sport_id, athlete.first_name, athlete.last_name))
        if athlete.date_of_birth != date_of_birth:
            athlete.date_of_birth = date_of_birth
            if self.verbosity > 1:
                print("Update date of birth for athlete: %s, %s %s" % (
                    athlete.sport_id, athlete.first_name, athlete.last_name))
        if athlete.gender != row[4]:
            athlete.gender = row[4]
            if self.verbosity > 1:
                print("Update gender for athlete: %s, %s %s" % (
                    athlete.sport_id, athlete.first_name, athlete.last_name))
        athlete.date_of_birth = date_of_birth
        athlete.gender = row[4]
        if row[0] not in self.athletes:
            self.athletes.add(row[0])
            if athlete.organization != organization:
                athlete.organization = organization
                if self.verbosity > 1:
                    print("Update organization for athlete: %s, %s %s" % (
                        athlete.sport_id, athlete.first_name, athlete.last_name))
        else:
            if (organization != athlete.organization and
                    organization not in athlete.additional_organizations.all()):
                athlete.additional_organizations.add(organization)
                if self.verbosity > 1:
                    print("Added additional organization for athlete: %s, %s %s" % (
                        athlete.sport_id, athlete.first_name, athlete.last_name))
        athlete.save()

    def _parse_row(self, row):
        try:
            athlete = Athlete.objects.get(sport_id=row[0])
        except Athlete.DoesNotExist:
            athlete = None
        try:
            organization = Organization.objects.get(id=row[5])
        except (Organization.DoesNotExist, ValueError):
            organization = None
        date_of_birth = datetime.strptime(row[3], '%Y-%m-%d').date()
        if not athlete and organization:
            self._create_athlete(row, date_of_birth, organization)
        elif organization:
            self._update_athlete(row, athlete, date_of_birth, organization)
        else:
            if self.verbosity > 0:
                print("Could not parse organization %s" % row[5])

    def handle(self, *args, **options):
        input_file = options['input']
        self.verbosity = options['verbosity']
        self.athletes = set()
        with open(input_file) as csv_file:
            csv_reader = csv.reader(filter(lambda row: row[0] != '#', csv_file))
            for row in csv_reader:
                self._parse_row(row)
