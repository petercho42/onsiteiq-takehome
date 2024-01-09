import pytest
from django.contrib.auth.models import Permission
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from ats.models import Job, User, Applicant, Application


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    user = User.objects.create_user(
        username="testuser",
        password="testpassword",
        first_name="Peter",
        last_name="Cho",
        email="petercho42@gmail.com",
    )
    view_permission = Permission.objects.get(codename="view_application")
    create_permission = Permission.objects.get(codename="add_application")
    status_permission = Permission.objects.get(codename="change_application")
    note_permission = Permission.objects.get(codename="add_applicationnote")
    user.user_permissions.add(view_permission)
    user.user_permissions.add(create_permission)
    user.user_permissions.add(status_permission)
    user.user_permissions.add(note_permission)
    return user


@pytest.fixture
def no_permission_user(db):
    user = User.objects.create_user(
        username="nopermissionuser",
        password="testpassword",
        first_name="Peter",
        last_name="Cho",
        email="petercho39@gmail.com",
    )
    return user


@pytest.fixture
def applicant(db, user):
    return Applicant.objects.create(
        user=user,
        phone_number="9172820312",
        linkedin_url="https://www.linkedin.com/in/petercho42/",
    )


@pytest.fixture
def job(db):
    return Job.objects.create(
        title="Test Job",
        description="Test Job Description",
        location="NYC",
        work_model=Job.WorkModel.HYBRID,
    )


@pytest.fixture
def application(db, user, applicant, job):
    return Application.objects.create(applicant=applicant, job=job)


def test_application_list_view(api_client, user, no_permission_user, application):
    api_client.force_authenticate(user=user)
    url = reverse("application-create-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["id"] == 1
    assert response.data[0]["applicant"]["phone_number"] == "9172820312"
    assert response.data[0]["job"]["status"] == "open"
    assert response.data[0]["status"] == "submitted"

    # Test with user without permission
    api_client.force_authenticate(user=no_permission_user)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert len(response.data) == 1


def test_application_create_view(api_client, user, no_permission_user, applicant, job):
    api_client.force_authenticate(user=user)
    url = reverse("application-create-list")

    data = {"job": job.id}
    response = api_client.post(url, data=data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in response.data
    assert response.data["applicant"]["phone_number"] == "9172820312"
    assert response.data["job"]["status"] == "open"
    assert response.data["status"] == "submitted"

    # Test with user without permission
    api_client.force_authenticate(user=no_permission_user)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert len(response.data) == 1


def test_application_approval_view(api_client, user, no_permission_user, application):
    api_client.force_authenticate(user=user)
    url = reverse("application-approval", kwargs={"pk": application.id})

    # Test approval
    response = api_client.patch(
        url, {"status": Application.Status.APPROVED}, format="json"
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"Success": "Application status updated successfully."}

    # Test rejection
    response = api_client.patch(
        url, {"status": Application.Status.REJECTED}, format="json"
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"Success": "Application status updated successfully."}

    # Test invalid status
    response = api_client.patch(url, {"status": "invalid_status"}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"Error": "Invalid status provided."}

    # Test with user without permission
    api_client.force_authenticate(user=no_permission_user)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert len(response.data) == 1


def test_application_note_create_view(
    api_client, user, no_permission_user, application
):
    api_client.force_authenticate(user=user)
    url = reverse("applicationnote-create", kwargs={"pk": application.id})

    # Test successful creation
    data = {
        "note": "Superb Applicant!",
    }
    response = api_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_201_CREATED

    # Test invalid data (missing note)
    invalid_data = data.copy()
    invalid_data.pop("note")
    response = api_client.post(url, data=invalid_data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "This field is required" in response.data["note"][0]

    # Test null data
    invalid_data = data.copy()
    invalid_data["note"] = "  "
    response = api_client.post(url, data=invalid_data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "This field may not be blank" in response.data["note"][0]

    # Test with user without permission
    api_client.force_authenticate(user=no_permission_user)
    response = api_client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert len(response.data) == 1


def test_application_stats(api_client, user, application):
    api_client.force_authenticate(user=user)

    stats_url = reverse("application-stats")
    response = api_client.get(stats_url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["title"] == "Test Job"
    assert response.data[0]["total_applications"] == 1
    assert response.data[0]["approved_applications"] == 0
    assert response.data[0]["rejected_applications"] == 0

    approval_url = reverse("application-approval", kwargs={"pk": application.id})

    # Test approval
    response = api_client.patch(
        approval_url, {"status": Application.Status.APPROVED}, format="json"
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"Success": "Application status updated successfully."}

    # Test Stat
    response = api_client.get(stats_url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["title"] == "Test Job"
    assert response.data[0]["total_applications"] == 1
    assert response.data[0]["approved_applications"] == 1
    assert response.data[0]["rejected_applications"] == 0

    # Test rejection
    response = api_client.patch(
        approval_url, {"status": Application.Status.REJECTED}, format="json"
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"Success": "Application status updated successfully."}

    # Test Stat
    response = api_client.get(stats_url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["title"] == "Test Job"
    assert response.data[0]["total_applications"] == 1
    assert response.data[0]["approved_applications"] == 0
    assert response.data[0]["rejected_applications"] == 1
