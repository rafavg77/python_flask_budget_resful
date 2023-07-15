import datetime
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from sqlalchemy.exc import NoResultFound
from marshmallow import Schema, fields, ValidationError, pre_load

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/presupuesto_colli.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = False
db = SQLAlchemy(app)
api = Api(app)

## MODDELS ##

class Bank(db.Model):
    bank_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(200))
    status = db.Column(db.Boolean)
    creation_date = db.Column(db.DateTime, default=datetime.datetime.now())
    #Relationship
    accounts = db.relationship("Account", back_populates="bank", cascade="all, \
                               delete-orphan" )

class Account(db.Model):
    account_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(200), nullable=False)
    status = db.Column(db.Boolean)
    creation_date = db.Column(db.DateTime, default=datetime.datetime.now())
    bank_id = db.Column(db.Integer, db.ForeignKey("bank.bank_id"),nullable=False)
    #Relationship
    bank = db.relationship("Bank", back_populates ="accounts", uselist = False, \
                           single_parent = True)

def must_not_be_blank(data):
    if not data:
        return ValidationError("Data not provided! 😱")

class BankSchema(Schema):
    bank_id = fields.Int()
    name = fields.Str()
    description = fields.Str()
    status = fields.Bool()

class AccountSchema(Schema):
    account_id = fields.Int(dump_only=True)
    name =  fields.Str(required=True, validate=must_not_be_blank)
    type = fields.Str(required=True, validate=must_not_be_blank)
    status =  fields.Bool(required=True, validate=must_not_be_blank)
    bank = fields.Nested(BankSchema,valitate=must_not_be_blank)

    @pre_load
    def get_bank(self, data, **kwargs):
        bank_id = data['bank']
        bank = Bank.query.filter(Bank.bank_id == bank_id).one()
        bank_dict = dict(bank_id=bank.bank_id, name=bank.name)
        data['bank'] = bank_dict
        return data
        
bank_schema = BankSchema()
banks_schema = BankSchema(many=True)
account_schema = AccountSchema()
accounts_schema = AccountSchema(many=True)

## API ##

class BankResource(Resource):
    def get(self,bank_id):
        bank = Bank.query.get_or_404(bank_id)
        return bank_schema.dump(bank)
    
    def post(self):
        new_bank = Bank(
            name = request.json['name'],
            description = request.json['description'],
            status = request.json['status'],
        )
        db.session.add(new_bank)
        db.session.commit()
        return bank_schema.dump(new_bank)
    
    def put(self, bank_id):
        bank = Bank.query.get_or_404(bank_id)

        if 'name' in request.json:
            bank.name = request.json['name']
        if 'description' in request.json:
            bank.description = request.json['description']
        if 'status' in request.json:
            bank.status = request.json['status']
        
        db.session.commit()
        return bank_schema.dump(bank)
    
    def delete(self,bank_id):
        bank = Bank.query.get_or_404(bank_id)
        db.session.delete(bank)
        db.session.commit()
        return "{'message' : 'Bank {} delteted'}".format(bank_id),204
    
api.add_resource(BankResource, '/bank')
    
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True,port=5000)