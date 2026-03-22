from django.contrib import admin as django_admin
from django.contrib.auth import get_user_model
from django.forms import Form
from django.test import RequestFactory, TestCase, override_settings
from django.urls import resolve, reverse
from phonenumber_field.modelfields import PhoneNumberField

from django_phonedir.admin import ContactAdmin, DepartmentAdmin, FaxNumberAdmin
from django_phonedir.apps import PhonedirConfig
from django_phonedir.models import Contact, Department, FaxNumber
from django_phonedir.views import (
    DepartmentDetailView,
    DepartmentListView,
    SearchResultsView,
)


# Define test form.
class PhoneFormTest(Form):
    number = PhoneNumberField()


@override_settings(ROOT_URLCONF="django_phonedir.urls")
class PhoneDirTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.supervisor = User.objects.create_user(
            username="supervisor",
            password="password",
            first_name="Super",
            last_name="Visor",
            is_staff=True,
        )

        cls.dept_it = Department.objects.create(
            name="Information Technology",
            short_name="IT",
            supervisor=cls.supervisor,
        )
        cls.dept_hr = Department.objects.create(
            name="Human Resources",
            short_name="HR",
            supervisor=cls.supervisor,
        )

        # Two known-good phone numbers for PhoneNumberField.
        cls.valid_phone = "+1 555 555 5555"
        cls.valid_phone_alt = "+1 555 555 1234"

        cls.fax_it = FaxNumber.objects.create(
            department=cls.dept_it,
            description="Test Fax",
            phone=cls.valid_phone,
            location="Test Location",
        )

        cls.contact_smith = Contact.objects.create(
            department=cls.dept_it,
            first_name="Alice",
            last_name="Smith",
            title="CEO",
            extension=21111,
            location="CEO Office",
            phone=cls.valid_phone_alt,
        )
        cls.contact_smythe = Contact.objects.create(
            department=cls.dept_it,
            first_name="Alicia",
            last_name="Smythe",
            title="CTO",
            extension=22222,
            location="CTO Office",
            phone=cls.valid_phone_alt,
        )
        cls.contact_johnson = Contact.objects.create(
            department=cls.dept_hr,
            first_name="Bob",
            last_name="Johnson",
            title="Manager",
            extension=33333,
            location="HR Office",
            phone=cls.valid_phone_alt,
        )

    def test_phone_form_is_valid(self):
        form = PhoneFormTest({"number": self.valid_phone})
        self.assertTrue(form.is_valid())

    def test_models_str_and_get_absolute_url(self):
        self.assertEqual(str(self.dept_it), self.dept_it.name)
        self.assertEqual(
            self.dept_it.get_absolute_url(),
            reverse(
                "department_detail",
                kwargs={"short_name": self.dept_it.short_name},
            ),
        )

        self.assertEqual(
            str(self.fax_it), f"{self.fax_it.phone} {self.fax_it.department}"
        )

        expected_contact = (
            f"{self.contact_smith.first_name} {self.contact_smith.last_name} "
            f"(Ext: {self.contact_smith.extension})"
        )
        self.assertEqual(str(self.contact_smith), expected_contact)

    def test_urls_resolve_to_correct_views(self):
        # Note: resolve() expects a leading slash.
        dep_list_path = reverse("department_list")
        if not dep_list_path.startswith("/"):
            dep_list_path = "/" + dep_list_path
        match = resolve(dep_list_path)
        self.assertEqual(match.func.view_class, DepartmentListView)

        dep_detail_path = reverse(
            "department_detail",
            kwargs={"short_name": self.dept_it.short_name},
        )
        if not dep_detail_path.startswith("/"):
            dep_detail_path = "/" + dep_detail_path
        match = resolve(dep_detail_path)
        self.assertEqual(match.func.view_class, DepartmentDetailView)

        search_path = reverse("search_results")
        if not search_path.startswith("/"):
            search_path = "/" + search_path
        match = resolve(search_path)
        self.assertEqual(match.func.view_class, SearchResultsView)

    def test_department_list_view_template_and_order(self):
        response = self.client.get(reverse("department_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "django_phonedir/departments_listing.html"
        )

        # ListView orders by "name" (see DepartmentListView.ordering).
        departments = list(response.context["departments"])
        self.assertEqual(
            [d.short_name for d in departments],
            ["HR", "IT"],
        )

        self.assertContains(response, self.dept_it.name)
        self.assertContains(response, self.dept_hr.name)

    def test_department_detail_view_template_contains_related_objects(self):
        response = self.client.get(
            reverse(
                "department_detail",
                kwargs={"short_name": self.dept_it.short_name},
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "django_phonedir/department_detail.html"
        )

        self.assertContains(response, self.dept_it.name)
        self.assertContains(response, self.fax_it.description)
        self.assertContains(response, self.contact_smith.first_name)
        self.assertContains(response, self.contact_smith.last_name)

    def test_search_results_view_get_queryset_filters_and_orders(self):
        factory = RequestFactory()
        request = factory.get(reverse("search_results"), data={"q": "Sm"})

        view = SearchResultsView()
        view.setup(request)

        qs = view.get_queryset()
        self.assertEqual(
            list(qs.values_list("last_name", flat=True)),
            ["Smith", "Smythe"],
        )

    def test_search_results_view_template_and_content(self):
        response = self.client.get(
            reverse("search_results"), data={"q": "Sm"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "django_phonedir/search_contact_results.html"
        )

        self.assertContains(response, self.contact_smith.first_name)
        self.assertContains(response, self.contact_smith.last_name)
        self.assertContains(response, self.contact_smythe.last_name)
        self.assertNotContains(response, self.contact_johnson.last_name)

    def test_admin_permission_methods(self):
        factory = RequestFactory()
        request = factory.get("/")
        User = get_user_model()

        department_admin = DepartmentAdmin(Department, django_admin.site)

        # Test with a staff user
        request.user = User(is_staff=True)
        self.assertTrue(department_admin.has_module_permission(request))
        self.assertTrue(department_admin.has_permission(request))

        # Test with a regular user
        request.user = User(is_staff=False)
        self.assertFalse(department_admin.has_module_permission(request))
        self.assertFalse(department_admin.has_permission(request))

    def test_admin_classes_smoke_instantiation(self):
        # Ensures the admin module defines all expected ModelAdmin classes.
        ContactAdmin(Contact, django_admin.site)
        FaxNumberAdmin(FaxNumber, django_admin.site)
        DepartmentAdmin(Department, django_admin.site)

    def test_app_config_name(self):
        self.assertEqual(PhonedirConfig.name, "django_phonedir")
