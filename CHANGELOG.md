# Changelog
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
Django upgrade includes database changes, run migrations

## 1.0.1 - 2021-02-10
### Changes
- Fixed field name in event filter

## 1.0.0 - 2020-11-16
### Changes
- Requirements version updates
- Added missing text field to partial result nested serializer

## 0.5.0 - 2020-09-13
### Changes
- Added statistics links

## 0.4.0 - 2020-08-14
### Changes
- Added group by one support to statistics list
- Fixed missing user id in logging
- Changed parameter to limit organizations to users own 

### Updating notes
Includes database changes, run migrations
- Added StatisticsLink model

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