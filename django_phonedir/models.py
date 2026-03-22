from django.conf import settings
from django.db import models
from django.urls import reverse
from phonenumber_field.modelfields import PhoneNumberField

User = settings.AUTH_USER_MODEL


class Department(models.Model):
    """
    Django model representing a deparmtent of a company.
    """

    name = models.CharField(
        max_length=64, unique=True, help_text="Name of the department."
    )
    short_name = models.CharField(
        max_length=8, unique=True, help_text="Short name that is used in the URL."
    )

    # Points to a User (the supervisor)
    supervisor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="supervised_departments",
        help_text="Points to a user, typically the supervisor, or any user that will manage the contacts associate with this department.",
    )

    def __str__(self):
        """
        String for representing the model object name.
        Specifically, this returns whatever value was set to name for the model.
        """
        return self.name

    def get_absolute_url(self):
        """
        Returns the URL to access a particular instance of the model.
        """
        return reverse("department_detail", kwargs={"short_name": self.short_name})


class FaxNumber(models.Model):
    """
    Django model representing a fax number for a department.
    """
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="faxnumbers"
    )
    description = models.CharField(max_length=64)
    phone = PhoneNumberField()
    location = models.CharField(max_length=64)

    def __str__(self):
        """
        Returns the string representation of the model as "{phone} {department}".
        """
        return "{phone} {department}".format(
            phone=self.phone, department=self.department
        )


class Contact(models.Model):
    """
    Django model representing a contact for a department.
    """
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="contacts"
    )
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    title = models.CharField(max_length=64)
    extension = models.IntegerField()
    location = models.CharField(max_length=64)
    phone = PhoneNumberField(blank=True)

    def __str__(self):
        """
        Returns the string representation of the model as "{first_name} {last_name} (Ext: {extension})".
        """
        return "{first_name} {last_name} (Ext: {extension})".format(
            first_name=self.first_name,
            last_name=self.last_name,
            extension=self.extension,
        )
