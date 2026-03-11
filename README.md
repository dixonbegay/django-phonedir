# django_phonedir

A reusable Django app for a phone directory system.

Tested and known to work with Django 5.2 and newer. Tested with Python 3.12 and
newer.

## Installation

Install via pip.

```
pip install django-phonedir
```

Add to Django settings `INSTALLED_APPS` like so...

```
INSTALLED_APPS = [
    ...
    "django-phonedir",
    ...
]
```

## Development

This project is under active development by myself. This Django app is
functioning, but would like to setup more testing to ensure the package remains
stable.

This project will eventually be published to PyPi in the near future so that it
can easily be integrated into a Django website.

I will develop better documentation at a later date.

### Setup

Use pipenv for managing the package requirements for development.

```
pipenv install --dev
```

### Testing

Tests can be run using the command: `pipenv run`
