from django.conf import settings
from django.db import models
from django.urls import reverse
from phonenumber_field.modelfields import PhoneNumberField

User = settings.AUTH_USER_MODEL


class Department(models.Model):
    """
    Django model representing a department of a company.
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


class Campus(models.Model):
    """
    Django model representing a campus (top-level physical location).
    """
    name = models.CharField(max_length=64, unique=True, blank=False, help_text="Campus name.")

    def __str__(self):
        return self.name


class Building(models.Model):
    """
    Django model representing a building on a campus.
    """
    name = models.CharField(max_length=64, blank=False, help_text="Building name or number.")
    campus = models.ForeignKey(
        Campus, on_delete=models.CASCADE, related_name="buildings"
    )

    def __str__(self):
        return self.name

    def building_campus_str(self):
        """
        Returns the string representation of the model as "{name} — {campus}".
        """
        return f"{self.name} — {self.campus}"


class Location(models.Model):
    """
    Django model representing a specific room within a building.
    """
    room = models.CharField(max_length=64, blank=False, help_text="Room number or area.")
    building = models.ForeignKey(
        Building, on_delete=models.CASCADE, related_name="locations"
    )

    def __str__(self):
        """
        Returns the string representation of the model as "{room} — {building} — {building.campus}".
        """
        return f"{self.room} — {self.building} — {self.building.campus}"

    def room_building_str(self):
        """
        Returns the string representation of the model as "{room} — {building}".
        """
        return f"{self.room} — {self.building}"




class FaxNumber(models.Model):
    """
    Django model representing a fax number for a department.
    """
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="faxnumbers"
    )
    description = models.CharField(max_length=64, blank=True)
    phone = PhoneNumberField(blank=False)
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="fax_numbers"
    )

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
    first_name = models.CharField(max_length=64, blank=False)
    last_name = models.CharField(max_length=64, blank=False)
    title = models.CharField(max_length=64, blank=False)
    extension = models.IntegerField(blank=True)
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="contacts"
    )
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
