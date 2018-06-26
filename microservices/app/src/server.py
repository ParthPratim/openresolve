from src import app
from flask import render_template
from flask import request
from .backend import * 
import json, requests

# from flask import jsonify
TEMPLATES_AUTO_RELOAD = True
@app.route("/")
@app.route("/<durl>")
def home(durl=None):
    auth_data =  request.cookies.get("hasura_auth_uikit") 
    temp_params = {};
    temp_params["d_url"] = durl
    ci = request.args.get("ci_status")
    if ci is not None:
        if ci == "success":
            temp_params["ci"] = "true"
        else:
            temp_params["ci"] = "false"
            
    if auth_data:
        auth_data = json.loads(auth_data)
        uinfo = auth_data["user_info"];
        if len(uinfo["auth_token"]) > 0:
            temp_params["u_name"] = uinfo["username"]
            temp_params["u_hid"] = uinfo["hasura_id"]
            
    return render_template('index.html', params = temp_params ,  request = request)

@app.route("/issue/<issueid>")
def resolve_issue(issueid):
    temp_params = {}
    auth_data =  request.cookies.get("hasura_auth_uikit") 
    if auth_data:
        auth_data = json.loads(auth_data)
        uinfo = auth_data["user_info"];
        if len(uinfo["auth_token"]) > 0:
            temp_params["u_name"] = uinfo["username"]
            temp_params["u_hid"]= uinfo["hasura_id"] 
            u_role = auth_data['user_info']['hasura_roles'][0]
            headers = {
                "Content-Type": "application/json", 
                "Authorization": "Bearer "+uinfo["auth_token"],
                "X-Hasura-Role": u_role
            }
            url = "https://data.enamor68.hasura-app.io/v1/query"
            requestPayload = {
            "type": "select",
            "args": {
            "table": "issues",
            "columns": [
                "*"
            ],
            "where": {
                "id": {
                    "$eq": str(issueid)
                }
            }
            }
            }
    
    
            # Make the query and store response in resp
            resp = requests.request("POST", url, data=json.dumps(requestPayload), headers=headers)
            try:
                ret = json.loads(resp.content.decode('utf-8'))
                if len(ret) > 0:
                    rp = {
                        "type" : "select",
                        "args" : {
                                "table" : "contributors",
                                "columns" : [
                                    "*"
                                ],
                                "where" : {
                                    "issueid" : {
                                        "$eq" : issueid
                                    },
                                    "userid" : {
                                        "$eq": temp_params["u_hid"]
                                    }
                                }
                        }
                    }
                    data = json.loads(send_request(url,headers,rp).content.decode('utf-8'))
                    if len(data) == 0:
                        rp = {
                        "type" : "insert",
                        "args" : {
                                "table" : "contributors",
                            "objects" :[{
                                "issueid" : issueid,
                                "userid" : temp_params["u_hid"],
                                "username" : temp_params["u_name"]
                            }]
                        }
                        }
                        send_request(url,headers,rp)
                    try :
                        jrow = ret[0];
                        for key, value in jrow.items():
                            temp_params[key] = value
                        return render_template('codeedit.html', params = temp_params ,  request = request)
                    except KeyError:
                        return "Invalid Issue-ID Submitted"
                else:
                    return "404"
            except json.decoder.JSONDecodeError:
                return "Invalid Error"
    else:
        return "PLease login first"
