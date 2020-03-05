# Changelog

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