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

### URL Paths

By default, there are certain URL paths that are provided to help get you
started. The built-in URL paths and templates can be utilized by adding
`django_phonedir.urls` to your main list of urlpatterns in a urls.py file like
so...

```
from django.urls import include, path

urlspatterns = [
    ...
    path("", include("django_phonedir.urls")),
    ...
]
```

You don't have to use these URL paths and associated templates. Below is a
listing of the paths with the associated views and template names.

- Path: departments
  - View: DepartmentListView
  - Template Name: department_list
  - Template File: department_listing.html
- Path: department/<slug:short_name>/
  - View: DepartmentDetailView
  - Template Name: department_detail
  - Template File: department_detail.html
- Path: search
  - View: SearchResultsView
  - Template Name: search_results
  - Template File: search_contact_results.html

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
