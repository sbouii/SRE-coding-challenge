### Implementation:
- Server:
  The sever is implemented using Flask framework, it's running on port 80 and it servers a simple JSON object {"message": "hello world!"}.

  For configuring the rate limit, it uses the python library flask_limiter https://flask-limiter.readthedocs.io/en/stable/. The rate limit is configured using the environment variable RATE_LIMIT, the details are in the How it works section.

  It uses Redis as a key-value store for session management, Redis and the server are running separately.

  For generating prometheus metrics, it uses Flask prometheus exporter which provides metrics about Flask HTTP requests, you can create your own metrics or use the default ones https://pypi.org/project/prometheus-flask-exporter/.

- Client:
  The client is a simple python script that uses the requests library to create a session for sending HTTP requests to the server.

  You can configure how many requests it's allowed to send to the server during a session, how many retires it can perform when it a has request failure and how long should the client wait between the failure retry requests, more details are in the How it works section.

### How it works:
- You have the possibility to deploy the application in containers using the Dockerfiles.
  You can run the containers with Docker compose or in a kubernetes cluster.

#### Deploy with Docker-compose:
  Docker compose file will spin up 3 containers, one for each of the client, the server and Redis.

  Apply the following steps for deploying the application with Docker-compose:

- Modify the client and the server settings in the .env file, please add the values without '' or "":
  ```
  RATE_LIMIT: number of requests the server can handler in a specific time period:
  20/2hour: 20 requests per 2 hours
  10/day: 10 requests per day
  300/30minute: 300 requests per 30 minutes.

  CLIENT_TOTAL_REQUESTS: number of requests the client is allowed to send to the server.

  CLIENT_TOTAL_FAILURE_RETRIES: number of retries the client is allowed to send to the server in case of request failure.

  CLIENT_BACKOFF_FACTOR: used to calculate how long should the client wait between the failure retry requests based on this rule: {backoff factor} * (2 ** ({number of total retries} - 1)), it can be integer or float.
  ```

- Build and start the containers with Docker-compose:
  ```
  docker-compose up -d
  ```
  If you want to run multiple clients at the same time in order to multiply the requests sent to the server, you can scale up the number of clients:
  ```
  docker-compose up --scale client=4 -d
  ```  
- You can check the server response for your client requests from the client's container logs:
  ```
  docker logs <client-container-id>
  ```
  With the following settings:
  RATE_LIMIT=5/10minute

  CLIENT_TOTAL_REQUESTS=7

  CLIENT_TOTAL_FAILURE_RETRIES=4

  CLIENT_BACKOFF_FACTOR=1

  The output is:

  ```
DEBUG:urllib3.connectionpool:Starting new HTTP connection (1): server:80
DEBUG:urllib3.connectionpool:http://server:80 "GET / HTTP/1.1" 200 27
{"message":"hello world!"}

DEBUG:urllib3.connectionpool:Resetting dropped connection: server
DEBUG:urllib3.connectionpool:http://server:80 "GET / HTTP/1.1" 200 27
{"message":"hello world!"}

DEBUG:urllib3.connectionpool:Resetting dropped connection: server
DEBUG:urllib3.connectionpool:http://server:80 "GET / HTTP/1.1" 200 27
{"message":"hello world!"}

DEBUG:urllib3.connectionpool:Resetting dropped connection: server
DEBUG:urllib3.connectionpool:http://server:80 "GET / HTTP/1.1" 200 27
{"message":"hello world!"}

DEBUG:urllib3.connectionpool:Resetting dropped connection: server
DEBUG:urllib3.connectionpool:http://server:80 "GET / HTTP/1.1" 200 27
{"message":"hello world!"}

DEBUG:urllib3.connectionpool:Resetting dropped connection: server
DEBUG:urllib3.connectionpool:http://server:80 "GET / HTTP/1.1" 429 143
DEBUG:urllib3.util.retry:Incremented Retry for (url='/'): Retry(total=3, connect=None, read=None, redirect=None, status=None)
DEBUG:urllib3.connectionpool:Retry: /
DEBUG:urllib3.connectionpool:Resetting dropped connection: server
DEBUG:urllib3.connectionpool:http://server:80 "GET / HTTP/1.1" 429 143
DEBUG:urllib3.util.retry:Incremented Retry for (url='/'): Retry(total=2, connect=None, read=None, redirect=None, status=None)
DEBUG:urllib3.connectionpool:Retry: /
DEBUG:urllib3.connectionpool:Resetting dropped connection: server
DEBUG:urllib3.connectionpool:http://server:80 "GET / HTTP/1.1" 429 143
DEBUG:urllib3.util.retry:Incremented Retry for (url='/'): Retry(total=1, connect=None, read=None, redirect=None, status=None)
DEBUG:urllib3.connectionpool:Retry: /
DEBUG:urllib3.connectionpool:Resetting dropped connection: server
DEBUG:urllib3.connectionpool:http://server:80 "GET / HTTP/1.1" 429 143
DEBUG:urllib3.util.retry:Incremented Retry for (url='/'): Retry(total=0, connect=None, read=None, redirect=None, status=None)
DEBUG:urllib3.connectionpool:Retry: /
DEBUG:urllib3.connectionpool:Resetting dropped connection: server
DEBUG:urllib3.connectionpool:http://server:80 "GET / HTTP/1.1" 429 143
Failure retries limit is reached
  ```

- To query prometheus metrics about the requests success and failure, you can get it from the client  or the server container:

  ```
  From the client container:

  docker exec -it <client-container-id> ash
  curl http://server:80/metrics  

  From the server container:

  docker exec -it <server-container-id> ash
  curl http://localhost:80/metrics
  ```

  The most relevant metrics that you can use for estimating the rate limit are:

  - flask_http_request_total{method="GET",status="200"} : number of requests successfully served.

  - flask_http_request_total{method="GET",status="429"} : number of failed requests due to rate limit  hit.

  - client_requests_total{address="client-address",status="200"}: number of requests successfully served for a specific client.

  - client_requests_total{address="client-address",status="429"}: number of failed requests due to rate limit hit for a specific client.

#### Deploy with Kubernetes:

- You can use the provided deployment manifests to run the application in a kubernetes cluster.
  It's a simple deployment solution that can be improved:

   - The server, the client and Redis are deployed as separate pods.

   - Each of the server and the client has a configmap where you can change their settings using environment variables.

   - The client and the server docker images are already built and pushed to docker hub, you can built them locally and push to your private docker registry for security reasons, just update the deployment manifests with the correct docker image name.

   - You have the ability to scale up the number of client pods.

   - The server response and the prometheus metrics can be fetched from the client container.

### Questions:

1- How did you validate that your service would correctly respond with the rate limit message after it was reached?

The client receives a 'HTTP 429 Too Many Requests response status code' from the server whenever it reaches the rate limit. This code indicates that the client has hit the rate limit of the server.

2- What assumptions did you make about how configuration would work in a kubernetes environment, and why?

There are different ways to setup this application in a kubernetes cluster, the simplest one is the one that I provided, but thanks to kuberenetes capabilities in maintaining distributed systems in term of scalability, high availability and data persistence, we can those features when deploying this application in a kubernetes environment, for example:

  - In order to increase the load testing on the server, we can run multiple client pods simultaneously, each one has its own specific settings stored in a configmap. This can provide us with clearer visibility in terms of adjusting the rate limit.

  - Instead of running Redis as a single pod, we can deploy it as a master-slave cluster using statefulset, each pod in the statefullset has its own volume. This will guarantee for us the data persistence and the high availability of the key-value store that the server is using.

  - If we configure the server/client to receive/send many requests, we can expect failures due to resources (cpu/memory) limit hit. In this case, we can think of enabling horizontal autoscaling: spin up a new server/client whenever we hit a specifc amount of resources usage or the vertical autoscaling: add more resources (cpu/memory) to the server/client, but this requires the pod restart.

3- Did you have to make any shortcuts, and how would you resolve them?
TO DO

4- How would you want to extend this implementation of either the service or
the client in the future?

Besides the discussed above possibility to scale both of the client and the sever, we can enable threading in the client implementation in order to make it capable of sending the requests concurrently, this can scale the client requests sending capacity in a vertical way.

From the server side, we can add other Flask routes that use the same web server but serve on different paths and we have the ability to configure the rate limit for each route. This can help in testing the rate limit and adjusting its value.

5- Were there any stretch goals you wanted to get to, but lacked the time?  

Except the stretch goals that I have already implemented in my solution, I wanted to work on adding some prometheus alerts whenever a client hits the rate limit for a specific number of times.

TO DO: client_requests_total{address="client-address",status="429"}

Also I wanted to define the SLI and SLO of the service:
As SLO, I suggest 99.5% of client requests who hit the rate limit receive the correct response from the server. For the associated SLIs, we can think of error rate in the server logs or number of HTTP responses with status code different from 429 or 200.
