FROM python:3-alpine
ADD . /app
WORKDIR /app
RUN apk --no-cache add curl
RUN pip install -r requirements.txt
CMD ["ash","-c","python -u app.py && tail -f /dev/null"]
