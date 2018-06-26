from src import app
from flask import render_template
from flask import request
from .backend import * 
import json, requests, datetime 


@app.route("/ill_edit/<issue>",endpoint='try_edit')
def try_edit(issue):
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
            url = "https://data.enamor68.hasura-app.io/v1/query"
            if is_contributor(issue,hasura_id,headers):
                rp = {
                    "type" : "select" ,
                    "args" : {
                        "table" : "issues",
                        "columns":[
                            "resolved"
                        ],
                        "where" : {
                            "id" : {
                                "$eq" : issue
                            }
                        }
                    }
                }
                resolved = json.loads(send_request(url,headers,rp).content.decode('utf-8'))[0]['resolved']
                if resolved == True:
                    return "This issue has already been resolved"
                
                rp = {
                        "type": "select",
                        "args": {
                            "table": "issue_edit",
                            "columns" : [
                                "*"
                            ],
                            "where": {
                                "issueid": {
                                    "$eq": issue
                                }
                            }
                        }
                    }
                resp = send_request(url,headers,rp).content
                resp = json.loads(resp.decode('utf-8'))
                if len(resp) > 0:
                    etime = resp[0]['timestamp']
                    tnow = datetime.datetime.now().isoformat()
                    tdiff = timediff(etime,tnow)
                    if etime is None or tdiff >= 15:
                        rp = { 
                            "type": "update",
                            "args": {
                            "table": "issue_edit",
                            "where": {
                                    "issueid": {
                                    "$eq": issue
                                    }
                                },
                            "$set": {
                                    "hasura_id": hasura_id,
                                    "timestamp" : tnow,
                                    "editor" : username
                            }
                            }
                            }
                        update = send_request(url,headers,rp).content
                        update = json.loads(update.decode('utf-8'))
                        return json.dumps(rp)
                    else:
                        return "You can only request the currrent user to ABORT EDITING till the editor finishes editing"
                        
                else:
                    return "INTERNAL ERROR OCCURED"
                
            else:
                return "You are not a contributor"
    else:
        return "Please login and then continue"

@app.route("/issue_editor/<issue>",endpoint = 'fetch_editor')
def fetch_editor(issue):
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
            url = "https://data.enamor68.hasura-app.io/v1/query"
            rp = {
                "type" : "select",
                "args" : {
                    "table" : "issue_edit",
                    "columns" : [
                        "*"
                    ],
                    "where" : {
                        "issueid" : {
                            "$eq" : issue
                        }
                    }
                }
            }
            ehid = send_request(url,headers,rp).content
            ehid = json.loads(ehid.decode('utf-8'))
            if len(ehid) > 0:
                tnow = datetime.datetime.now().isoformat()
                if not ehid[0]['timestamp'] is None:
                    if timediff(ehid[0]['timestamp'] , tnow) >= 15:
                        rp = { 
                            "type": "update",
                            "args": {
                            "table": "issue_edit",
                            "where": {
                                    "issueid": {
                                    "$eq": issue
                                    }
                                },
                            "$set": {
                                    "hasura_id": 0,
                                    "timestamp" : None,
                                    "editor" : ""
                            }
                            }
                            }
                        none_editor = send_request(url,headers,rp).content
                        none_editor= json.loads(none_editor.decode('utf-8'))
                        if none_editor['affected_rows'] == 1:
                            return json.dumps({"editor" : None})
                        else:
                            return json.dumps({"editor" : "DB_ERROR"})
                    else:
                        return json.dumps({"editor" : ehid[0]['editor']})
                else:
                    return json.dumps({"editor" : None})
            else:
                return "Some internal error occured..."
            
@app.route("/requestAbort/<issue>",endpoint='request_abort')
def request_abort(issue):
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
            url = "https://data.enamor68.hasura-app.io/v1/query"
            if is_contributor(issue,hasura_id,headers):
                rp = {
                "type": "insert",
                "args": {
                "table": "request_abort",
                "objects": [
                                {               
                                    "answer": None,
                                    "issue_id": issue,
                                    "hasura_id": hasura_id,
                                    "username": username
                                }
                            ]
                        }
                    }
                ra = json.loads(send_request(url,headers,rp).content.decode('utf-8'))
                if ra['affected_rows'] == 1:
                    return json.dumps({"status" : "sent"})
                else:
                    return json.dumps({"status" : "failed"})
            else:
                return "You are not a contributor"
    else:
        return "Please login and then continue"
            
@app.route("/abort_requests/<issue>" , endpoint = 'abort_requests') 
def abort_requests(issue):
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
            client = app.test_client()
            response = json.loads(client.get("/issue_editor/"+issue, headers=list(request.headers)).data)
            if response['editor'] == username:
                url = "https://data.enamor68.hasura-app.io/v1/query"
                rp = {
                "type": "select",
                "args": {
                "table": "request_abort",
                "columns": [
                        "*"
                    ],
                "where": {
                "issue_id": {
                        "$eq": issue
                            },
                "answer" : {
                    "$eq" : None
                            },
                    "hasura_id" :{
                        "$ne" : hasura_id
                    }
                        }
                    }
                    }
                ar_list = send_request(url,headers,rp).content.decode('utf-8')
                json_list = json.loads(ar_list)
                send_list = []
                for index in range(0,len(json_list)):
                    is_present = False
                    for index2 in range(0,len(send_list)):
                        if json_list[index]['hasura_id'] == send_list[index2]['hasura_id']:
                            is_present = True
                            break
                    if  not is_present:
                        send_list.append(json_list[index])
                        
                return json.dumps(send_list)
            
            else:
                return "You are not editor of the issue"
            
    else:
        return "Please login and then continue"
    

@app.route("/actionabort/<issue>/<action>",methods=["POST"],endpoint='actionabort')
def actionabort(issue,action):
    ar_users = request.form["ar_users"]
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
            url = "https://data.enamor68.hasura-app.io/v1/query"
            if is_contributor(issue,hasura_id,headers):
                rp = {
                    "type": "update",
                    "args": {
                    "table": "request_abort",
                    "where": {
                        "username": {
                            "$in": ar_users.split(",")
                                },
                        "issue_id" : {
                            "$eq" : issue
                        }
                            },
                        "$set": {
                        "answer": action
                    }
                        }
                    }
                return send_request(url,headers,rp).content.decode('utf-8')
            else:
                return "You are not a contributor of this issue"
    else:
        return "Please login and then continue"

@app.route("/finish_edit/<issue>",endpoint='finish_edit')
def finish_edit(issue):
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
            url = "https://data.enamor68.hasura-app.io/v1/query"
            client = app.test_client()
            response = json.loads(client.get("/issue_editor/"+issue, headers=list(request.headers)).data)
            if response['editor'] == username:
                rp = { 
                            "type": "update",
                            "args": {
                            "table": "issue_edit",
                            "where": {
                                    "issueid": {
                                    "$eq": issue
                                    }
                                },
                            "$set": {
                                    "hasura_id": 0,
                                    "timestamp" : None,
                                    "editor" : ""
                            }
                            }
                            }
                f_edit = send_request(url,headers,rp).content
                if json.loads(f_edit.decode('utf-8'))['affected_rows'] == 1:
                    return json.dumps({'status' : 'edit_finished'})
                else:
                    return json.dumps({'status': 'failed_finish'})
            else:
                return "You are not the current editor"
    else:
        return "Please login and then continue"
    
@app.route("/source_update/<issue>",methods=["POST","GET"],endpoint='sourcecode_update')
def sourcecode_update(issue):
    source_code = request.values.get("source_code")
    line_num = request.values.get("line_num")
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
            url = "https://data.enamor68.hasura-app.io/v1/query"
            client = app.test_client()
            response = json.loads(client.get("/issue_editor/"+issue, headers=list(request.headers)).data)
            if response['editor'] == username:
                rp = {
                    "type":"update",
                    "args" : {
                        "table" : "updated_source",
                        "where" : {
                            "issue_id" :{
                                "$eq" : issue
                            }
                        },
                        "$set" :{
                            "source_code" : source_code,
                            "line_num" : line_num
                        }
                    }
                }
                update_source= send_request(url,headers,rp).content
                if(json.loads(update_source.decode('utf-8'))['affected_rows'] == 1):
                    return json.dumps({"status" : "updated"})
                else:
                    return json.dumps({"status" : "not_updated"})
            else:
                return "You are not the current editor"
    else :
        return "Please login and then continue"

@app.route("/load_source/<issue>",endpoint='load_source')
def load_source(issue):
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
            url = "https://data.enamor68.hasura-app.io/v1/query"
            if is_contributor(issue,hasura_id,headers):
                rp = {
                    "type" : "select",
                    "args" : {
                        "table" : "updated_source",
                        "columns" : [
                            "*"
                        ],
                        "where" :{
                            "issue_id":{
                                "$eq" : issue
                            }
                        }
                    }
                }
                get_source = send_request(url,headers,rp).content
                js_gs = json.loads(get_source.decode('utf-8'))
                if len(js_gs) > 0 :
                    return json.dumps(js_gs[0])
                else:
                    return json.dumps({"status" : "failed"})
            else:
                return "You are not the contributor"
    else:
        return "Please login and then continue"
            
@app.route("/ar_status/<issue>",endpoint='ar_status')
def ar_status(issue):
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
            url = "https://data.enamor68.hasura-app.io/v1/query"
            if is_contributor(issue,hasura_id,headers):
                rp = {
                    "type": "update",
                    "args": {
                    "table": "request_abort",
                    "where": {
                        "issue_id": {
                            "$eq": issue
                        },
                        "answer" : {
                            "$ne" : None
                        },
                        "seen" : {
                            "$eq" : False
                        },
                        "hasura_id" :{
                            "$eq" : hasura_id
                        }
                        },
                    "$set": {
                        "seen": True
                        },
                    "returning": [
                            "answer"
                        ]
                    }
                }
                get_arstatus = send_request(url,headers,rp).content
                json_ars = json.loads(get_arstatus.decode('utf-8'))
                return json.dumps(json_ars['returning'])
            else:
                return "You are not a contributor of  this issue"
    else:
        return "Please login and then continue"
    
@app.route("/contributors_list/<issue>",endpoint='contrib_list')
def contrib_list(issue):
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
            url = "https://data.enamor68.hasura-app.io/v1/query"
            rp = {
            "type" : "select",
            "args" : {
            "table" : "contributors",
            "columns" : [
                "username"
            ],
            "where" : {
                "issueid" : {
                    "$eq" : issue
                }
            }
            }
            }
            c_list = send_request(url,headers,rp).content
            return c_list.decode('utf-8')
    else:
        return "Please login and then continue"
        
@app.route("/view_problem/<issue>",endpoint='view_problem')
def view_problem(issue):
    url = "https://data.enamor68.hasura-app.io/v1/query"
    headers = {
        "Content-Type": "application/json"
    }
    rp ={
    "type": "select",
    "args": {
        "table": "issues",
        "columns": [
            "problem"
        ],
        "where": {
            "id": {
                "$eq": issue
            }
        }
    }
    }
    
    problem =  send_request(url,headers,rp).content
    return problem

@app.route("/markresolve/<issue>",endpoint='mark_resolve')
def mark_resolve(issue):
    auth_d = request.cookies.get("hasura_auth_uikit")
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
            url = "https://data.enamor68.hasura-app.io/v1/query"
            rp = {
                "type" : "update",
                "args" : {
                    "table" : "issues",
                    "where" : {
                        "id" : {
                            "$eq" : issue
                        },
                        "creater" : {
                            "$eq" : username
                        }
                    },
                    "$set" : {
                        "resolved" : True
                    }
                }
            }
            mark_resolve = send_request(url,headers,rp).content
            mr = json.loads(mark_resolve.decode('utf-8'))
            if mr['affected_rows'] == 1:
                return json.dumps({"status" : "marked"})
            else:
                return "Error Marking Issue as Resolved"
    else:
        return "Please login and then continue"
    
def is_contributor(issue,hasura_id,headers):
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
                            "$eq": issue
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
        return True
    else:
        return False
                
def timediff(s1,s2):
    
    if s1 is None:
        return 17
    
    s1_fc = s1.index(':')
    s1_h = int(s1[s1_fc-2:s1_fc])
    s1_m = int(s1[s1_fc+1:s1.index(':',s1_fc+1)])
    s1_s = int(s1[s1.index(':',s1_fc+1)+1:s2.index(':',s1_fc+1)+3])
    
    s2_fc = s2.index(':')
    s2_h = int(s2[s1_fc-2:s2_fc])
    s2_m = int(s2[s2_fc+1:s2.index(':',s2_fc+1)])
    s2_s = int(s2[s2.index(':',s2_fc+1)+1:s2.index(':',s2_fc+1)+3])
    
    
    elapsed_time=0
    
    if s2_h > s1_h:
        elapsed_time += (60 - s1_m) + ((s2_h - (s1_h+1))*60) + (s2_m)
    elif s2_h == s1_h:
        elapsed_time += s2_m - s1_m
    elif s1_h > s2_h:
        elapsed_time += (60 - s2_m) + ((s1_h - (s2_h+1))*60) + (s1_m)
    
    return elapsed_time
