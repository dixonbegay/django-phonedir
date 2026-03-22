import os
import django
from django.core.management import call_command

def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_phonedir.tests.settings")
    django.setup()
    call_command("makemigrations", "django_phonedir")

if __name__ == "__main__":
    main()