FROM python:3.9
# FROM python:3.10

WORKDIR /app

# RUN pip install gunicorn==20.1.0

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir
# RUN pip install -r /app/requirements.txt --no-cache-dir

COPY . .

# CMD ["python", "manage.py", "runserver", "0:8000"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram_backend.wsgi"]