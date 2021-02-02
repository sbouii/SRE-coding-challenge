import logging
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import os

def main():
   logging.basicConfig(level=logging.DEBUG)
   s = requests.Session()
   retries = Retry(total=int(os.environ['CLIENT_TOTAL_FAILURE_RETRIES']), backoff_factor=int(os.environ['CLIENT_BACKOFF_FACTOR']), status_forcelist=[429])
   s.mount('http://', HTTPAdapter(max_retries=retries))
   for i in range(1, int(os.environ['CLIENT_TOTAL_REQUESTS'])):
    try:
      r = s.get("http://server:80/")
      print(r.text)
    except requests.exceptions.RetryError:
      print ("Failure retries limit is reached")
      break
if __name__ == "__main__":
  main()
