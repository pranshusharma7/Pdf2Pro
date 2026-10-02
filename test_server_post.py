import http.client
import json

conn = http.client.HTTPConnection("localhost", 3000)
conn.request("POST", "/api/payment/initiate", json.dumps({"plan": "Pro", "amount": 199}), {"Content-Type": "application/json"})
res = conn.getresponse()
print(res.status, res.read().decode())
