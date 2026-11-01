FROM python:3.14-slim

# Prevent Python from generating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Ensure Python logs appear immediately
ENV PYTHONUNBUFFERED=1

# Set working directory inside the container
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Django development server port
EXPOSE 8000

# Start Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]