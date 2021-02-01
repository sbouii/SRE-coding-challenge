### Implementation:
- Server:
- Client:
### How it works:
- You have the possibility to deploy the application in containers using the Dockerfiles.
  You can run the containers with Docker compose or in a kubernetes cluster.

#### Deploy with Docker-compose:
  Docker compose file will spin up 3 containers, one for each of the client, the server and redis.
  The client and the server settings are configured using the environment variables mentioned in the .env file.
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
  docker-compose up --scale client=5 -d
  ```  
- You can check the server response for your client requests from the client's container logs:
  ```
  docker logs <client-container-id>
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
  - flask_http_request_total{method="GET",status="429"} : number of failed requests due to rate limit  hit  
  - client_requests_total{address="client-address",status="200"}: number of requests successfully served for a specific client.
  - client_requests_total{address="client-address",status="429"}: number of failed requests due to rate limit hit for a specific client.

#### Deploy with Kubernetes:
- You can use the provided deployment manifests to run the application in a kubernetes cluster.
  It's a simple deployment solution that can be improved:

   - The server, the client and redis are deployed as separate pods.

   - Each of the server and the client has a configmap where you can change their settings using environment variables.

   - The client and the server docker images are already built and pushed to docker hub, you can built them locally and push to your private docker registry for security reasons, just update the deployment manifests with the correct docker image name.

   - You have the ability to scale up the number of client pods.
   - The server response and the prometheus metrics can be fetched from the client container.

### Questions:
