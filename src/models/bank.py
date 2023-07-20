import datetime
from db import db
from typing import List

class BankModel(db.Model):
    __tablename__ = "banks"

    bank_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(200))
    status = db.Column(db.Boolean)
    #Relationship
    creation_date = db.Column(db.DateTime, default=datetime.datetime.now())
    accounts = db.relationship("Account", back_populates="bank", cascade="all, \
                               delete-orphan" )
    
    def __init__(self, name, description, status, creation_date):
        self.name = name
        self.description = description
        self.status = status
        self.creation_date = creation_date
    
    def json(self):
        return {
            "name" : self.name,
            "description" : self.description,
            "status" : self.status,
            "creation_date" : self.creation_date
        }
    
    @classmethod
    def find_by_name(cls, name) -> "BankModel":
        return cls.query.filter_by(name=name).first()
    
    @classmethod
    def find_by_name(cls, bank_id) -> "BankModel":
        return cls.query.filter_by(bank_id=bank_id).first()
    
    @classmethod
    def find_all(cls) -> List["BankModel"]:
        return cls.query.all()
    
    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()