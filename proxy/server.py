# importing the requests library
import requests
  
# # api-endpoint
# URL = "http://127.0.0.1:5000/web"
  
# # location given here
# location = "https://fit.mta.edu.vn/"
  
# # defining a params dict for the parameters to be sent to the API
# PARAMS = {'url':location}

URL = "http://127.0.0.1:5000/url"
PARAMS = {'url':"https://mta.edu.vn/"}
  
# sending get request and saving the response as response object
r = requests.post(url = URL, params = PARAMS)
  
# extracting data in json format
# data = r.json()

print(r.text)