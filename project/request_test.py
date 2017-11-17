import requests

headers = {"Username": "a@pi.com", "Password": "api123"}
response = requests.post("http://54.187.225.165:8080/api/auth/", headers=headers)

print(response.reason)
print(response.request)
print(response.text)
print(response.raw)
print(response.content)
