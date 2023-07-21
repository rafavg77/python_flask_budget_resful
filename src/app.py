from flask import Flask, jsonify, Blueprint
from flask_restx import Api
#from flask_restplus import Api

from db import db
from ma import ma

from resources.bank import BankList, bank_ns, banks_ns
from marshmallow import ValidationErrors

app = Flask(__name__)
blueprint = Blueprint('api', __name__, url_prefix='/api')
api = Api(blueprint, doc='/doc', title = 'Python Flask Restful BudgetApp')

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/presupuesto_colli.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True

api.add_namespace(bank_ns)
api.add_namespace(banks_ns)

@app.before_first_request
def create_tables():
    db.create_all()

@app.errorhandler(ValidationError)
def handle_validation_error(error):
    return jsonify(error.messages), 400

banks_ns.add_resource(BankList, "")

if __name__ == '__name__':
    db.init_app(app)
    ma.init_app(app)
    app.run(port=5000, debug=True, host='0.0.0.0')