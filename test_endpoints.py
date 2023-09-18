import requests

url = "https://api.farmeurimmo.fr/mc/user/{uuid}"
uuid = "f09cd989-3fd7-43b2-95b0-6f9dfab11793"
data = {"content": {"hi": "hello"}}

response = requests.post(url.format(uuid=uuid), json=data)
