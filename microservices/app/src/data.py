import requests, json
from flask import request, render_template
from src import app

# // For local development,
# // First: connect to Hasura Data APIs directly on port 9000
# // $ hasura ms port-forward data -n hasura --local-port=9000
# // Second: Uncomment the line below
# dataUrl = 'http://localhost:9000/v1/query'

# When deployed to your cluster, use this:
dataUrl = 'http://data.hasura/v1/query'

@app.route('/issues')
def fetch_issues():
    if ('hasura-app.io' in request.url_root) or \
       ('127.0.0.1:5000' in request.url_root) or \
       ('data.hasura' not in dataUrl):
            url = "https://data.enamor68.hasura-app.io/v1/query"

            # This is the json payload for the query
            requestPayload = {
                "type": "select",
                "args": {
                    "table": "issues",
                    "columns": [
                        "*"
                    ]
                }
            }

            # Setting headers
            headers = {
                "Content-Type": "application/json"
            }

            # Make the query and store response in resp
            resp = requests.request("POST", url, data=json.dumps(requestPayload), headers=headers)

            # resp.content contains the json response.
            return resp.content
    else:
        return "None"
