from django.contrib import admin

from phonedir.models import Contact, Department, FaxNumber


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_filter = ["department"]


class ContactInline(admin.StackedInline):
    model = Contact
    # fields = [("first_name", "last_name", "title", "extension"), ("location", "phone")]
    fieldsets = [
        (None, {"fields": ["first_name", "last_name", "extension", "phone"]}),
        (
            "More options",
            {"classes": ["wide", "collapse"], "fields": ["title", "location"]},
        ),
    ]
    extra = 0  # Provides one empty slot for a new contact


@admin.register(FaxNumber)
class FaxNumberAdmin(admin.ModelAdmin):
    list_filter = ["department"]


class FaxNumberInline(admin.TabularInline):
    model = FaxNumber
    extra = 0  # Provides one empty slot for a new contact


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "supervisor")
    inlines = [ContactInline, FaxNumberInline]

    def has_module_permission(self, request):
        # Only allows users with is_staff = True to see this in the admin
        return request.user.is_staff

    def has_permission(self, request, obj=None):
        return request.user.is_staff
