import datetime
from db import db

class AccountModel(db.Model):
    __tablename__ = "accounts"

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