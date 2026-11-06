FROM python:latest
WORKDIR /srv/app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "order_app.api.handlers:app", "--host", "0.0.0.0", "--port", "8000"]
