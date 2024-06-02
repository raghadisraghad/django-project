# Use the official Python image from the Docker Hub
FROM python:3.9

# Set environment variables for Python to run in unbuffered mode and to prevent Python from writing pyc files to disk
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file from your host to the container
COPY requirements.txt /app/

# Install the dependencies specified in requirements.txt
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code to the container
COPY . /app/

# Expose port 8000 to the outside world
EXPOSE 8000

# Run the Django development server using Gunicorn as the WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "E_learning.wsgi:application"]
