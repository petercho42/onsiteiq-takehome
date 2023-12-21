
# OnsiteIQ Takehome (ATS)

## Table of Contents

- [Screenshots](#screenshots)
- [Installation](#installation)

  
## Screenshots (Postman)
![Create](https://github.com/petercho42/onsiteiq-takehome/blob/main/screenshots/create.png)
![List](https://github.com/petercho42/onsiteiq-takehome/blob/main/screenshots/list.png)
![Approve](https://github.com/petercho42/onsiteiq-takehome/blob/main/screenshots/approve.png)
![Note](https://github.com/petercho42/onsiteiq-takehome/blob/main/screenshots/note.png)


## Installation
0. Build and run docker `docker-compose build; docker-compose up`
1. Once both the db and the web are running connect to the web
(e.g. `docker exec -it takehome-web-1 /bin/bash`)
2. Try running pytest: `pytest`. All test should be passing.
3. Open up django interactive shell (`python manage.py shell`)
4. Create the following objects to get started:
```
from ats.models import Job, User, Applicant
from django.contrib.auth.models import Permission
from rest_framework.authtoken.models import Token

# create user
user = User.objects.create_user(
    username="petercho42",
    password="password",
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

token, _ = Token.objects.get_or_create(user=user)

# make that user as an applicant
Applicant.objects.create(
    user=user,
    phone_number="9172820312",
    linkedin_url="https://www.linkedin.com/in/petercho42/",
)

job = Job.objects.create(
    title="Software Engineer",
    description="Hiring Softwar Engineer with extensive Django experience.",
    location="NYC",
    work_model=Job.WorkModel.HYBRID,
)

print(f"\n\nUse this auth token for postman: {token.key}")
print(f"\nJob ID [{job.id}] created")
``` 