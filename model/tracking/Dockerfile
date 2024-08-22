FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

# Clear pip cache to reduce image size
# RUN pip cache purge

COPY . .

# Make sure to copy static files
COPY static /app/static

EXPOSE 8002

CMD ["uvicorn", "user_api:app", "--host", "0.0.0.0", "--port", "8002"]
