from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from ats.models import Application, ApplicationNote, Job
from ats.permissions import (
    IsApplicationViewer,
    IsApplicationCreator,
    IsApplicationDecisionMaker,
    IsApplicationNoteWriter,
)
from ats.serializers import (
    ApplicationSerializer,
    ApplicationNoteSerializer,
    ApplicationStatsSerializer,
)


class JobApplicationStatsAPIView(APIView):
    def get(self, request):
        jobs_with_stats = Job.objects.annotate(
            total_applications=Count("application"),
            approved_applications=Count(
                "application", filter=Q(application__status="approved")
            ),
            rejected_applications=Count(
                "application", filter=Q(application__status="rejected")
            ),
        )
        print(jobs_with_stats[0].title)

        job_serializer = ApplicationStatsSerializer(jobs_with_stats, many=True)
        stats = job_serializer.data

        return Response(stats)


class ApplicationCreateListView(generics.CreateAPIView, generics.ListAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer

    def get_permissions(self):
        if self.request.method == "POST":  # Create
            permission_classes = [IsApplicationCreator]
        else:  # List
            permission_classes = [IsApplicationViewer]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        job_id = serializer.validated_data["job"]
        applicant = self.request.user.applicant
        job = Job.objects.get(id=job_id)
        if job.status == Job.Status.CLOSED:
            raise serializers.ValidationError(
                {"job": ["The job is closed. Cannot create an application."]}
            )

        serializer.save(job=job, applicant=applicant)


class ApplicationApprovalView(generics.UpdateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsApplicationDecisionMaker]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        status = request.data.get("status", None)

        if status in [Application.Status.APPROVED, Application.Status.REJECTED]:
            instance.update_status(status)
            return Response({"Success": "Application status updated successfully."})
        else:
            return Response({"Error": "Invalid status provided."}, status=400)


class ApplicationNoteCreateView(generics.CreateAPIView):
    queryset = ApplicationNote.objects.all()
    serializer_class = ApplicationNoteSerializer
    permission_classes = [IsApplicationNoteWriter]

    def perform_create(self, serializer):
        application_id = self.kwargs.get("pk")
        note = self.request.data.get("note", None)
        application = get_object_or_404(Application, pk=application_id)
        serializer.save(
            created_by=self.request.user, application=application, note=note
        )
