from flask import Flask

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = 'microservices/app/src/uploads/'
# This line adds the hasura example routes form the hasura.py file.
# Delete these two lines, and delete the file to remove them from your project
# from .hasura import hasura_example
# app.register_blueprint(hasura_examples)

from .server import *
from .data import *
from .create_issue import *
from .imp import *
from .issueedit import *