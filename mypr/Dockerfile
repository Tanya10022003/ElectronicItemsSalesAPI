# Dockerfile

FROM python:3.9

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the project files into the container
COPY . .

EXPOSE 8000

# Run Django migrations and start the server
CMD ["gunicorn", "mypr.wsgi:application", "--bind", "0.0.0.0:8000"]
