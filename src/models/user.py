import datetime
from db import db

class UserModel(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    telegram_id = db.Column(db.String(200), nullable=True)
    status = db.Column(db.Boolean)
    creation_date = db.Column(db.DateTime, default=datetime.datetime.now())
    #Relationship
    accounts = db.relationship("Account", back_populates="user", cascade="all, \
                               delete-orphan" )