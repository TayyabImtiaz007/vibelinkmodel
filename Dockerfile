# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variable for Python packages path
ENV PYTHONPATH=/usr/lib/python3.11/site-packages

# Install git (required for pip installing from GitHub)
RUN apt-get update && apt-get install -y git

# Install poetry
RUN pip install poetry

# Copy only the pyproject.toml and poetry.lock first
WORKDIR /app
COPY pyproject.toml poetry.lock /app/

RUN pip install django-cors-headers
RUN pip install psycopg-binary

# Install specific dependencies not covered by poetry
RUN pip install openapi-codec==1.3.2 pypika==0.48.9 moviepy==1.0.3

RUN pip install openai
# RUN pip install openai-whisper
RUN pip install git+https://github.com/openai/whisper.git

# Install dependencies using poetry
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

# Copy the rest of the application code
COPY . /app

# Set environment variables
ENV OPENAI_API_KEY='sk-proj-oLe6eS8vqBtuBVddeM8oT3BlbkFJcN6eFqtnwGyh8J8EGSUy'
ENV DEBUG=true

# Expose port 8000 for the application
EXPOSE 8000

# Define the command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "8", "--timeout", "100", "JacobRyanMedia.wsgi:application"]
