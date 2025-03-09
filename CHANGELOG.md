# Changelog

## 1.6.0 - 2025-03-09
- Added sport managers
- Changed API schema to OpenAPI 3
- Changed CI testing from Travis to GitHub Actions
- Removed support for Python 3.8
- Fixed missing organization in permission check
- Updated Pohjolan malja calculation
- Updated requirements

### Updating notes
Includes database changes, run migrations
- Added manager group for sports
- Renamed manager group for areas

## 1.5.0 - 2024-12-16
- Added notifications for new events and competitions
- Added option to include competitions in event status change
- Added new event contact type
- Added athlete to EventContact filters
- Added limited event info to EventContact serializer
- Updated requirements

### Updating notes
Includes database changes, run migrations
- Added new event contact type

## 1.4.0 - 2024-06-21
- Updated to Django 4.2
- Updated requirements
- Added support to SuomiSport merits
- Fixed signal name for area group creation
- Updated type choices for event contacts
- Added missing basenames to routers
- Filter athlete information to currently valid

## 1.3.0 - 2023-12-17
### Changes
- Add support for area managers
- Remove support for Python 3.7
- Update requirements
- Add validation that competition dates are within event dates
- Lock competitions and events based on the end date, not start date
- Add organization id and abbreviation to Athletes filter
- Add ordering filter to events and competitions
- Fix permission group check in events serializer

### Updating notes
Includes database changes, run migrations
- Add groups to Area model
- Add area_competition option to competition levels

## 1.2.0 - 2022-07-09
### Changes
- Add description field to statistic links
- Add support for result greater or less than filtering
- Add info to AthleteLimitedSerializer and limit info values
- Change dry-rest-permissions to supported fork
- Fix licence check when licence type is not specified

### Updating notes
Includes database changes, run migrations
- Updated StatisticsLink model

## 1.1.0 - 2022-05-27
### Changes
- Remove support for Python 3.6
- Django upgraded to 3.2 series
- Requirements version updates
- Add extra searchable fields
- Ignore historical records in record approval
- Limit Pohjolan Malja statistics to positive positions
- Add support to saving statistics links

### Updating notes
Includes database changes, run migrations
- Added StatisticsLink model
- Django upgrade

## 1.0.1 - 2021-02-10
### Changes
- Fixed field name in event filter

## 1.0.0 - 2020-11-16
### Changes
- Requirements version updates
- Added missing text field to partial result nested serializer

## 0.4.0 - 2020-08-14
### Changes
- Added group by one support to statistics list
- Fixed missing user id in logging
- Changed parameter to limit organizations to users own 

## 0.3.0 - 2020-08-11
### Changes
- Added support nested partial results in results import
- Fixed various record check limitations and bugs
- Added partial record check limiting by result type and category
- Added option to specify if same result value should create a record
- Added result code to partial results
- Fixed partial result maximum value in team results
- Added competition calendar support
  - Added event information fields and event contacts
  - Added competitions to event serializer
  - Changed limit event information in competition serializer
  - Added event and Competition approval
- Added management task to get list of organizations from Suomisport
- Added setting to save only birth year from Suomisport
- Added timestamps to Competition, Event, Record and Result models
- Added management task for approvals based on last update date
- Added limit and search options for events and competitions
- Added until filter to competitions
- Added visibility restrictions setting for events and competitions
- Fixed multipart name case in Suomisport connector
- Added dry run option to result create and update
- Added text base partial result value
- Changed DateTime partial result value to Time
- Changed result values and limits to 3 decimals
- Added missing result info parameter to serializers

### Updating notes
Includes database changes, run migrations
- Added event related name to Competition model
- Added check_record_partial and limit_partial options to
  CategoryForCompetitionType model
- Added Event and Competition approval
- Added EventContact model
- Added various Event information fields
- Added result code to ResultPartial model
- Added created and changed timestamps to Competition, Event, Record and
  Result models
- Changed DateTime partial result value to Time
- Changed result values to 3 decimals
- Changed result limits to decimal values

## 0.2.0 - 2020-03-05
### Changes
- Added Suomisport connector
- Fixed results grouping
- Fixed templates path in settings
- Test and documentation updates

### Updating notes
Includes database changes, run migrations
- Changed public (boolean) to visibility (char) in AthleteInformation model
- Added modification_time to AthleteInformation model
- Added no_auto_update option to Athlete model
- Added sport_id and historical status to Organizations model

## 0.1.0 - 2020-02-17
Initial public version