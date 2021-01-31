FROM python:3-alpine
ADD . /app
WORKDIR /app
RUN apk --no-cache add curl
RUN pip install -r requirements.txt
EXPOSE 80
CMD ["python", "-u", "app.py"]
