import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import NoResultFound
from flask_restful import Api, Resource
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

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    telegram_id = db.Column(db.String(200), nullable=True)
    status = db.Column(db.Boolean)
    creation_date = db.Column(db.DateTime, default=datetime.datetime.now())
    #Relationship
    accounts = db.relationship("Account", back_populates="user", cascade="all, \
                               delete-orphan" )

class Account(db.Model):
    account_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(200), nullable=False)
    status = db.Column(db.Boolean)
    creation_date = db.Column(db.DateTime, default=datetime.datetime.now())
    bank_id = db.Column(db.Integer, db.ForeignKey("bank.bank_id"),nullable=False)
    #Relationship
    bank = db.relationship("Bank", back_populates ="accounts", uselist = True, \
                           single_parent = True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"),nullable=False)
    user = db.relationship("User", back_populates = "accounts", uselist = True, \
                           single_parent = True)
        
def must_not_be_blank(data):
    if not data:
        return ValidationError("Data not provided! 😱")

class BankSchema(Schema):
    bank_id = fields.Int()
    name = fields.Str()
    description = fields.Str()
    status = fields.Bool()

class UserSchema(Schema):
    user_id = fields.Int()
    name = fields.Str()
    email = fields.Str()
    telegram_id = fields.Str()
    status = fields.Bool()

class AccountSchema(Schema):
    account_id = fields.Int(dump_only=True)
    name =  fields.Str(required=True, validate=must_not_be_blank)
    type = fields.Str(required=True, validate=must_not_be_blank)
    status =  fields.Bool()
    bank = fields.Nested(BankSchema,valitate=must_not_be_blank)
    user = fields.Nested(UserSchema,valitate=must_not_be_blank)

    @pre_load
    def get_bank(self, data, **kwargs):
        bank_id = data['bank']
        bank = Bank.query.filter(Bank.bank_id == bank_id).one()
        bank_dict = dict(bank_id=bank.bank_id, name=bank.name)
        data['bank'] = bank_dict

        user_id = data['user']
        user = User.query.get_or_404(user_id)
        user_dict = dict(user_id=user.user_id, name=user.name, email= user.email)
        data['user'] = user_dict
        return data

        
bank_schema = BankSchema()
banks_schema = BankSchema(many=True)

user_schema = UserSchema()
users_schema = UserSchema(many=True)

account_schema = AccountSchema()
accounts_schema = AccountSchema(many=True)

## API ##

class BanksResource(Resource):
    def get(self):
        banks = Bank.query.all()
        return banks_schema.dump(banks)
    
    def post(self):
        new_bank = Bank(
            name = request.json['name'],
            description = request.json['description'],
            status = request.json['status'],
        )
        db.session.add(new_bank)
        db.session.commit()
        return bank_schema.dump(new_bank)
    
class BankResource(Resource):
    def get(self,bank_id):
        bank = Bank.query.get_or_404(bank_id)
        return bank_schema.dump(bank)
            
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

        return jsonify({
            "message" : "Bank {} deleted successfuly".format(bank_id)
            })

class UsersResource(Resource):
    def get(self):
        users = User.query.all()
        return users_schema.dump(users)
    
    def post(self):
        new_user = User(
            name = request.json['name'],
            email = request.json['email'],
            telegram_id = request.json['telegram_id'],
            status = request.json['status'],
        )
        db.session.add(new_user)
        db.session.commit()

        return user_schema.dump(new_user)

class UserResource(Resource):
    def get(self,user_id):
        """try:
            account = Account.query.filter(account.bank_id == account_id).one()
        except NoResultFound:
            return {"message": "Group could not be found."}, 400
        """
        try:
            user = User.query.filter(User.user_id == user_id).one()
        except NoResultFound:
            return {"message": "Group could not be found."}, 400
        
        user_result = user_schema.dump(user)
        account_result = accounts_schema.dump(user.accounts.all())
        
        return {
            "user" : user_result,
            "accounts" : account_result
        }

class AccountsResource(Resource):
    def get(self):
        accounts = Account.query.all()
        return accounts_schema.dump(accounts)
    
    def post(self):

        data = account_schema.load(request.json)
        print(data)

        new_account = Account(
            name = data['name'],
            type = data['type'],
            status = data['status'],
            bank = Bank.query.get_or_404(data['bank']['bank_id']),
            user = User.query.get_or_404(data['user']['user_id'])
        )

        db.session.add(new_account)
        db.session.commit()
        return account_schema.dump(new_account)
    
class AccountResource(Resource):
    def get(self,account_id):
        account = Account.query.get_or_404(account_id)
        return account_schema.dump(account)
    
    def put(self,account_id):
        account = Account.query.get_or_404(account_id)
        print(account)

        if 'name' in request.json:
            account.name = request.json['name']
        if 'type' in request.json:
            account.type = request.json['type']
        if 'status' in request.json:
            account.status = request.json['status']
        if 'bank' in request.json:
            bank = Bank.query.get_or_404(request.json['bank'])
            print(bank)
            account.bank = bank
        if 'user' in request.json:
            user = User.query.get_or_404(request.json['user'])
            print(user)
            account.user = user
        db.session.commit()

        return account_schema.dump(account)
    
    def delete(self,account_id):
        account = Account.query.get_or_404(account_id)
        db.session.delete(account)
        db.session.commit()

        return jsonify({
            "message" : "Account {} deleted successfuly".format(account_id)
            })

api.add_resource(BanksResource, '/bank')
api.add_resource(BankResource, '/bank/<int:bank_id>')

api.add_resource(UsersResource, '/user')
api.add_resource(UserResource, '/user/<int:user_id>')

api.add_resource(AccountsResource, '/accounts')
api.add_resource(AccountResource, '/account/<int:account_id>')
    
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True,port=5000)