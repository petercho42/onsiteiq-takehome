from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Job(TimestampMixin, models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100)

    class WorkModel(models.TextChoices):
        ONSITE = (
            "onsite",
            _("Onsite"),
        )
        REMOTE = (
            "remote",
            _("Remote"),
        )
        HYBRID = (
            "hybrid",
            _("HYBRID"),
        )

    work_model = models.CharField(
        max_length=20,
        choices=WorkModel.choices,
        default=WorkModel.ONSITE,
    )

    class Status(models.TextChoices):
        OPEN = (
            "open",
            _("Open"),
        )
        CLOSED = (
            "closed",
            _("Closed"),
        )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )


class User(AbstractUser, TimestampMixin):
    pass


class Applicant(TimestampMixin, models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="applicant"
    )
    phone_number = PhoneNumberField()
    linkedin_url = models.URLField(max_length=200)


class Application(TimestampMixin, models.Model):
    applicant = models.ForeignKey(
        "ats.Applicant", on_delete=models.CASCADE, related_name="applications_submitted"
    )
    job = models.ForeignKey("ats.Job", on_delete=models.CASCADE)

    class Status(models.TextChoices):
        SUBMITTED = (
            "submitted",
            _("Submitted"),
        )
        APPROVED = (
            "approved",
            _("Approved"),
        )
        REJECTED = (
            "rejected",
            _("Rejected"),
        )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SUBMITTED,
    )

    def update_status(self, status):
        self.status = status
        self.save(update_fields=["status"])

    class Meta:
        unique_together = ["applicant", "job"]


class ApplicationNote(TimestampMixin, models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name="application_notes"
    )
    note = models.TextField()
