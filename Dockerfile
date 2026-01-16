FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app


RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
 && rm -rf /var/lib/apt/lists/*


RUN pip install --no-cache-dir pipenv


COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy


COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
