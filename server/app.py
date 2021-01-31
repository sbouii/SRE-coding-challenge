from flask import Flask, jsonify, request
from redis import Redis
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from prometheus_flask_exporter import PrometheusMetrics
import os
import sys

app = Flask(__name__)

for variable, value in os.environ.items():
    if variable.startswith("RATE_LIMIT"):
        app.config[variable] = value

metrics = PrometheusMetrics(app, group_by='endpoint')

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1/minute"]
)
redis = Redis(host='redis', port=6379)

@app.route('/')
@limiter.limit(app.config["RATE_LIMIT"])
@metrics.counter('client_requests', 'client requests by status code and address', labels={'status': lambda resp: resp.status_code, 'address': lambda: request.environ['REMOTE_ADDR']})
def helloIndex():
    data  =  {"message": "hello world!"}
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
