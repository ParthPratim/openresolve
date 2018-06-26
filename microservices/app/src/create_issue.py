import requests, json , os
from flask import request, render_template, redirect
from werkzeug import secure_filename
from .backend import *
from src import app



@app.route('/create_issue', methods=['GET', 'POST'])
def create_issue():
    form_data = request.values;
    issue_title = form_data.get('title')
    issue_problem = form_data.get('problem')
    issue_plang = form_data.get('plang_name')
    f = request.files['files[]']
    #f.save(os.path.abspath(app.config['UPLOAD_FOLDER']+ secure_filename(f.filename)))
    url = "https://filestore.enamor68.hasura-app.io/v1/file"
    uinfo = request.cookies.get('hasura_auth_uikit')
    if uinfo:
        uinfo = json.loads(uinfo)
        auth = uinfo['user_info']['auth_token'];
        headers = {
            "Authorization": "Bearer "+auth,
            "X-Hasura-Role": "user"
        }
        resp = requests.post(url, data=f.read(),headers=headers)
        
        fudata = json.loads(resp.content)
        url = "https://data.enamor68.hasura-app.io/v1/query"
        
        requestPayload = {
            "type": "insert",
            "args": {
                "table": "issues",
                "objects": [
                    {
                        "title": issue_title,
                        "problem": issue_problem,
                        "src_link": fudata['file_id'],
                        "language": issue_plang,
                        "creater": uinfo['user_info']['username']
                    }
                ],
                "returning" : [
                    "id"
                ]
            }
        }
        headers = {
            "Authorization": "Bearer "+auth,
            "X-Hasura-Role": "user" ,
            "Content-Type": "application/json"
        }
        resp = send_request(url,headers,requestPayload).content
        id = json.loads(resp.decode('utf-8'))['returning'][0]['id']
        rp = {
                        "type" : "insert",
                        "args" : {
                                "table" : "issue_edit",
                            "objects" :[{
                                "issueid" : id,
                                "hasura_id" : 0,
                                "editor" : ""
                            }]
                        }
                }
        resp = send_request(url,headers,rp)
        rp = {
                        "type" : "insert",
                        "args" : {
                                "table" : "updated_source",
                            "objects" :[{
                                "issue_id" : id,
                                "source_code" : ""
                            }]
                        }
                }
        resp = send_request(url,headers,rp)
        return redirect("https://openresolve.enamor68.hasura-app.io/?ci_status=success",302)

    else:
        return redirect("https://auth.enamor68.hasura-app.io/ui/login?redirect_url=https://openresolve.enamor68.hasura-app.io",302)