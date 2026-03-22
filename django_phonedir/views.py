from django.db.models import Q, query
from django.views.generic import DetailView, ListView

from django_phonedir.models import Contact, Department


class DepartmentListView(ListView):
    """
    Django class based view that shows a list of all department models.
    """
    model = Department
    template_name = "django_phonedir/departments_listing.html"
    context_object_name = "departments"
    ordering = "name"

    # def get_queryset(self, *args, **kwargs):
    # We prefetch 'contacts' to avoid the N+1 query problem
    # return Department.objects.prefetch_related("contacts").all()


class DepartmentDetailView(DetailView):
    """
    Django class based view that shows a detailed view of a specific department.
    The view can be utilized in a URL using "short_name" as a slug in the URL like so:
    "/department/short_name=information%20technology/"
    """
    model = Department
    template_name = "django_phonedir/department_detail.html"
    slug_field = "short_name"
    slug_url_kwarg = "short_name"


class SearchResultsView(ListView):
    """
    Django class based view that shows a list of contact models that match the query.
    """
    model = Contact
    template_name = "django_phonedir/search_contact_results.html"
    context_object_name = "contacts"

    def get_queryset(self) -> query.QuerySet[Contact]:
        query_request = self.request.GET.get("q")
        contact_list = Contact.objects.filter(
            Q(last_name__icontains=query_request)
            | Q(first_name__icontains=query_request)
        ).order_by("last_name")
        return contact_list
