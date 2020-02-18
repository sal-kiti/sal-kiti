# SAL Kiti
SAL Kiti (Kiti) is a sport results and statistics service created for the Finnish Shooting Sport Federation.

This is the backend/API side of Kiti.

Backend is written in Python, using [Django](https://www.djangoproject.com/) and
[Django REST framework](https://www.django-rest-framework.org/).

## Versioning
Kiti uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

API should be quite static but some breaking changes are possible in near future. Plan is to release
1.0.0 before June 2020.

Check [CHANGELOG](CHANGELOG.md) for current status

## Requirements
Tested with Python 3.6 - 3.7.

Install requirements for production from requirements.txt and for development from
requirements_dev.txt

Copy sal_kiti/settings/local_settings_example.py to sal_kiti/settings/local_settings.py and edit as necessary.

## Documentation
Documentation in the Read the Docs: https://sal-kiti.readthedocs.io/