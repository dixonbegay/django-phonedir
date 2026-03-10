from django.urls import path

from django_phonedir.views import (  # Assuming views.py is in the same app folder
    DepartmentDetailView,
    DepartmentListView,
    SearchResultsView,
)

urlpatterns = [
    # When a user visits the site root (empty path), it calls SearchResultsView
    path("departments", DepartmentListView.as_view(), name="department_list"),
    path(
        "department/<slug:short_name>/",
        DepartmentDetailView.as_view(),
        name="department_detail",
    ),
    path("search", SearchResultsView.as_view(), name="search_results"),
]
