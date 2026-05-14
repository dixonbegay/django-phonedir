from django.contrib import admin

from django_phonedir.models import Contact, Department, FaxNumber


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """
    The main class for the Contact model on the admin site.
    """
    list_filter = ["department"]


class ContactInline(admin.StackedInline):
    """
    The inline class for the Contact model on the admin site.
    """
    model = Contact
    # fields = [("first_name", "last_name", "title", "extension"), ("location", "phone")]
    fieldsets = [
        (None, {"fields": ["first_name", "last_name", "extension", "phone", "title", "location"]}),
    ]
    extra = 0

    def has_add_permission(self, request, obj=None):
        # obj is the parent Department; allow if the user supervises it
        if request.user.is_superuser:
            return True
        if obj is None:
            return request.user.is_staff
        return obj.supervisor == request.user

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return request.user.is_staff
        return obj.supervisor == request.user

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return request.user.is_staff
        return obj.supervisor == request.user

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return request.user.is_staff
        return obj.supervisor == request.user


@admin.register(FaxNumber)
class FaxNumberAdmin(admin.ModelAdmin):
    """
    The main class for the FaxNumber model on the admin site.
    """
    list_filter = ["department"]


class FaxNumberInline(admin.TabularInline):
    """
    The inline class for the FaxNumber model on the admin site.
    """
    model = FaxNumber
    extra = 0

    def has_add_permission(self, request, obj=None):
        # obj is the parent Department; allow if the user supervises it
        if request.user.is_superuser:
            return True
        if obj is None:
            return request.user.is_staff
        return obj.supervisor == request.user

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return request.user.is_staff
        return obj.supervisor == request.user

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return request.user.is_staff
        return obj.supervisor == request.user

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return request.user.is_staff
        return obj.supervisor == request.user


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """
    The main class for the Department model on the admin site.
    """
    list_display = ("name", "supervisor")
    inlines = [ContactInline, FaxNumberInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(supervisor=request.user)

    def has_module_permission(self, request):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return request.user.is_staff
        return request.user.is_staff and obj.supervisor == request.user

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
