#INSTANT MESSAGING MODULE

from src import app
from flask import render_template
from flask import request
from .backend import * 
import json, requests, datetime

@app.route("/im", endpoint='im')
def im():
    return "INSTANT MESSAGING MODULE - openresolve"

@app.route("/im/newmsg" , methods=['GET', 'POST'] , endpoint='new_chat')
def new_chat():
    post_data = request.values
    chat_msg = post_data.get("chat_msg") 
    issueid = post_data.get("issueid")
    auth_d = request.cookies.get("hasura_auth_uikit");
    if auth_d:
        auth_d = json.loads(auth_d)
        if auth_d['user_info']:
            hasura_id = auth_d['user_info']['hasura_id']
            username = auth_d['user_info']['username']
            auth_token = auth_d['user_info']['auth_token']
            u_role = auth_d['user_info']['hasura_roles'][0]
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer "+auth_token,
                "X-Hasura-Role": u_role
            }

            if chat_msg and issueid:
                if len(chat_msg) > 0:
                    url = "https://data.enamor68.hasura-app.io/v1/query"
                    rp = {
                        "type": "select",
                        "args": {
                            "table": "contributors",
                            "columns": [
                                "*"
                            ],
                            "where": {
                                "issueid": {
                                    "$eq": issueid
                                },
                                "userid" : {
                                    "$eq": str(hasura_id)
                                }
                            }
                        }
                    }
                    response = send_request(url,headers,rp).content;
                    response = json.loads(response.decode('utf-8'))
                    if len(response) != 0:
                        url = "https://data.enamor68.hasura-app.io/v1/query"
                        rp = {
                            "type": "insert",
                            "args": {
                                "table": "im_chats",
                                "objects": [
                                    {
                                        "userid": str(hasura_id),
                                        "chatmsg": chat_msg,
                                        "issueid": issueid,
                                        "username": username,
                                        "timestamp": datetime.datetime.now().isoformat()
                                    }
                                ]
                            }
                        }
                        return (send_request(url,headers,rp).content)
                    else:
                        return "CHAT NOT CREATED"
                else:
                    return "NO CHAT MESSAGE SUBMITTED"
            else:
                return "SUBMIT ALL PARAMETERS"
    else:
        return "PLEASE LOGIN FIRST"
                
@app.route("/im/fetchmsgs", endpoint='fetch_chats')
def fetch_chats():
    post_data = request.args
    issueid = post_data.get("issueid")
    auth_d = request.cookies.get("hasura_auth_uikit");
    if auth_d:
        auth_d = json.loads(auth_d)
        if auth_d['user_info']:
            hasura_id = auth_d['user_info']['hasura_id']
            auth_token = auth_d['user_info']['auth_token']
            u_role = auth_d['user_info']['hasura_roles'][0]
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer "+auth_token,
                "X-Hasura-Role": u_role
            }

            if issueid:
                url = "https://data.enamor68.hasura-app.io/v1/query"
                rp = {
                        "type": "select",
                        "args": {
                            "table": "contributors",
                            "columns": [
                                "*"
                            ],
                            "where": {
                                "issueid": {
                                    "$eq": issueid
                                },
                                "userid" : {
                                    "$eq": hasura_id
                                }
                            }
                        }
                    }
                response_d = send_request(url,headers,rp).content;
                response = json.loads(response_d.decode('utf-8'))
                if len(response) != 0 :
                    url = "https://data.enamor68.hasura-app.io/v1/query"
                    # This is the json payload for the query
                    rp = {
                            "type": "select",
                            "args": {
                            "table": "im_chats",
                            "columns": [
                            "*"
                            ],
                            "where": {
                                "issueid": {
                                "$eq": issueid
                                }
                            },
                            "order_by": [
                                {
                                "column": "timestamp",
                                "order": "asc"
                                }
                            ]
                    }
                    }
                    chats = send_request(url,headers,rp).content;
                    return (chats.decode('utf-8'))

                else:
                    return "You are not a contributor"
            else:
                return "No issue id submitted"
        else:
            return "Please login and then continue"
    else:
        return "NO COOKIE"
  