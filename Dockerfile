# Use an official Python runtime as a parent image
FROM python:3.10.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN apt-get update \
    && apt-get install -y postgresql-client \
    && pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/

# Run Django migrations
# RUN python manage.py migrate

# Expose port 8000
EXPOSE 8000

# Define the command to run on container start
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]