FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Clear pip cache to reduce image size
# RUN pip cache purge

COPY . .

EXPOSE 8000

RUN chmod +x initialize.sh

CMD ["./initialize.sh"]
