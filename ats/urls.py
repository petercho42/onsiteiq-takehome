from django.urls import path

from ats.views import (
    ApplicationCreateListView,
    ApplicationApprovalView,
    ApplicationNoteCreateView,
    JobApplicationStatsAPIView,
)


urlpatterns = [
    path(
        "applications/",
        ApplicationCreateListView.as_view(),
        name="application-create-list",
    ),
    path(
        "applications/<int:pk>/approval/",
        ApplicationApprovalView.as_view(),
        name="application-approval",
    ),
    path(
        "applications/<int:pk>/notes/",
        ApplicationNoteCreateView.as_view(),
        name="applicationnote-create",
    ),
    path(
        "applications/stats/",
        JobApplicationStatsAPIView.as_view(),
        name="application-stats",
    ),
]
