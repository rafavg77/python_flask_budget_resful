from ma import ma 
from models.bank import BankModel

"""
class BankSchema(ma.Schema):
    bank_id = ma.fields.Int()
    name = ma.fields.Str()
    description = ma.fields.Str()
    status = ma.fields.Bool()
"""

class BankSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = BankModel
        load_instance = True
        load_only = ("accounts")
        #include_fk = True