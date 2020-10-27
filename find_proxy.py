import requests

proxies = {
'https': '212.119.40.107:8085',
'http': '212.119.40.107:8085'
}

url = 'http://httpbin.org/ip'
resp = requests.get(url,proxies=proxies)
print(resp.json())
