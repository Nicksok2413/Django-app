FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install "poetry==2.2.0"
RUN poetry config virtualenvs.create false --local
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

COPY mysite .

CMD ["python", "manage.py", "collectstatic", "--noinput"]
CMD ["gunicorn", "mysite.wsgi:application", "--bind", "0.0.0.0:8000"]