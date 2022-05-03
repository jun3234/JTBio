#! usr/bin/env python

import urllib3
import json

print(dir(urllib3))
ip = "10.99.110.110"
http = urllib3.PoolManager()
r = http.request("GET", ip)

print(r.status)
print(dir(r))
print(r.data.decode())

data = {
    'username':'15992485905',
    'password': '92485905'
}

encode_data = json.dumps(data).encode()
r = http.request('POST', ip, body=encode_data, headers={'Content-Type':'application/json'})
print(r.status)
print(r.data.decode())