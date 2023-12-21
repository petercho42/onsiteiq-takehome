from rest_framework import serializers

from ats.models import Job, User, Applicant, Application, ApplicationNote


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ["title", "status", "location", "work_model"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email"]


class ApplicantSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Applicant
        fields = ["id", "user", "phone_number", "linkedin_url"]


class ApplicationNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationNote
        fields = ["note"]


class ApplicationSerializer(serializers.ModelSerializer):
    applicant = ApplicantSerializer()
    job = JobSerializer()
    application_notes = ApplicationNoteSerializer(many=True, read_only=True)

    class Meta:
        model = Application
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("context", {}).get("request")
        super().__init__(*args, **kwargs)

    def to_representation(self, instance):
        """
        Serialize for list view
        """
        representation = super().to_representation(instance)

        representation["applicant"] = {
            "user": {
                "id": instance.applicant.user.id,
                "first_name": instance.applicant.user.first_name,
                "last_name": instance.applicant.user.last_name,
                "email": instance.applicant.user.email,
            },
            "applicant_id": instance.applicant.id,
            "linkedin_url": instance.applicant.linkedin_url,
            "phone_number": str(instance.applicant.phone_number),
        }
        representation["job"] = {
            "id": instance.job.id,
            "title": instance.job.title,
            "status": instance.job.status,
            "location": instance.job.location,
            "work_model": instance.job.work_model,
        }

        representation["application_notes"] = ApplicationNoteSerializer(
            instance.application_notes.all(), many=True
        ).data

        return representation

    def to_internal_value(self, data):
        """
        Deserialize for create view
        """
        request_user = self.request.user if self.request else None
        return {"job": data.get("job"), "applicant": request_user.applicant}
