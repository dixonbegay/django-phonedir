from django.test import TestCase
from django.test import SimpleTestCase
from django.urls import reverse
from django.forms import Form
from phonenumber_field.modelfields import PhoneNumberField
import logging

from django_phonedir.models import Department, FaxNumber, Contact

logger = logging.getLogger(__name__)

try:
    # Django >= 1.7
    from django.test import override_settings
except ImportError as err:
    # Django <= 1.6
    logger.error(err)
    raise RuntimeError(
        "Could not import django.test. No support for Django versions 1.6 or less."
    )

try:
    # Django >= 1.7
    from django.urls import reverse
except ImportError as err:
    # Django <= 1.6
    logger.error(err)
    raise RuntimeError(
        "Could not import django.urls. No support for Django versions 1.6 or less."
    )


# Define test form.
class PhoneFormTest(Form):
    number = PhoneNumberField()


class PhoneDirTests(TestCase):
    def test_models(self):
        # Testing Department model.
        dept = Department(
            name="Information Technology", short_name="IT", supervisor=None
        )
        phoneFormTest = PhoneFormTest({"number": "+1 555 555 5555"})
        self.assertTrue(phoneFormTest.is_valid())

        # Testing FaxNumber model.
        faxNumberTest = FaxNumber(
            department=dept.pk,
            description="Test Fax",
            phone=phoneFormTest.fields.get("number"),
            location="Test Location",
        )
        self.assertEqual(str(faxNumberTest), "+1 555 555 5555 Information Technology")

        # Testing Contact model.
        contactTest = Contact(
            department=dept.pk,
            first_name="Testfirstname",
            last_name="Testlastname",
            title="CEO",
            extension="21111",
            location="CEO Office",
            phone="555-555-1111",
        )
        self.assertEqual(str(contactTest), "Testfirstname Testlastname (Ext: 21111)")

    def test_url_exists_at_correct_location(self):
        response = self.client.get("departments")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("search")
        self.assertEqual(response.status_code, 200)

    def test_url_available_by_name(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_template_name_correct(self):
        response = self.client.get(reverse("home"))
        self.assertTemplateUsed(
            response, "django_phonedir/templates/django_phonedir/home.html"
        )

    def test_template_content(self):
        response = self.client.get(reverse("departments"))
        self.assertContains(response, "<h1>Homepage</h1>")
        self.assertNotContains(response, "Not on the page")
