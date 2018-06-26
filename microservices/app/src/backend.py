import requests , json

def send_request(url,headers,payload):
    resp = requests.request("POST", url, data=json.dumps(payload), headers=headers)
    return resp