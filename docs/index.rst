SAL Kiti
====================================
Sport results and statistics service created for the
Finnish Shooting Sport Federation.

Main features
-------------
* Events and competitions management
* Competition result lists
* Statistics
* Records keeping

Authentication and user types
-----------------------------
SAL Kiti API supports both token authentication and Django's cookie based session authentication.
Settings variable controls if authentication tokens are created automatically or not.

Anonymous users have read access for most data.

Organization users are authenticated users who are included in the same group(s) as the organization(s).
Organization users may create new events and competitions for this organization and add or modify results until
staff users either locks the event or competition or confirms results.

Staff users are users who may create or modify events, competitions and results for any organizations.
They also have access to Django admin interface and may be permitted access to various models there.

Administrators are users who have access to all Django admin interface commands.

Data relations
--------------
All links between models may be checked from models-page but there are descriptions of the most important.

Sports, categories and competition types
++++++++++++++++++++++++++++++++++++++++
Sports may include multiple categories and competition types.

Categories may include limitations for athlete age and gender. If age_exact is set in category, age checks are
done with exact competition start date and athlete's date of birth. If it's not set, age checks are done by
birth year only.

Competition types may include limits for the result values.

By default all categories in sport are allowed in all competition types. It's possible to limit these by
creating CategoryForCompetitionType links between those. Result values may also be set individually for different
categories.

Organizations and areas
+++++++++++++++++++++++
Organizations may be part of the areas. This may affect some record checks.

Competitions and events
+++++++++++++++++++++++
Events may have multiple competitions. Each competition has specific type and level.

Organization users may create and modify events and competitions for their organizations and change the visibility.
Staff users may set events and competitions locked so that organization users may no longed modify them or add
new competitions or results. They may also set trial status to competition which may be used in statistics search.

Results and partial results
+++++++++++++++++++++++++++
Competitions include results which may include partial results.

Allowed partial results depend on the competition type and are defined in CompetitionResultTypes.

Added and modified results are subject to various validations. Most important are:
* Age and gender checks for the category, if athlete has date_of_birth and gender attributes and category has
limitations for those.
* Team results may only be added if category allows it and team size is checked if defined for the category.
* Result value limits from competition type or partial result types.

Records
+++++++
Possible records are calculated automatically for added or modified results if the competition type
has records status set.

Records are checked against all record levels allowed for that competition type and competition level.
If record level includes area, records are only checked if athlete's organization is part of that area.

By default, record is only checked against the category of the result. It's possible to group categories so
that record is checked against all grouped categories if athlete's age and gender would allow competing in that
category. This is done by setting same record_group number in CategoryForCompetitionType for all categories.

Competition layouts
+++++++++++++++++++
Dynamic layout information may be set to competition types and competitions (defaults to competition type
layout).

This information is meant for the front end to define how the result information of various competition
types should be displayed.

* type: layout number
* label: label displayed to user, in table view only first row label is displayed
* name: competition result type abbreviation + order number. i.e. "elim-1", "elim-2" if result type is "elim"
* block: results block, i.e. finals or preliminary results
* row: result may be splitted to multiple rows (1-4)
* col: table column number for the result
* order: additional ordering if a result is displayed in single column
* hide: hide on smaller screens
* show: show on larger screens

Structure
----------

.. toctree::
   :maxdepth: 2

   modules/models
   modules/serializers
   modules/views
   modules/helpers

Index and search
==================

* :ref:`genindex`
* :ref:`search`
