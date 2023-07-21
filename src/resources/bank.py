from flask import request
from flask_restx import Resource, fields, Namespace

from models.bank import BankModel
from schemas.bank import BankSchema

BANK_NOT_FOUND = "Bank not fount 😱"

bank_ns = Namespace('bank', description="Bank related operations")
banks_ns = Namespace('banks', description="Banks related operations")

bank_schema = BankSchema()
bank_list_schema = BankSchema(many=True)

bank = bank_ns.model('Bank', {
    "name" : fields.String(),
    "description" : fields.String(),
    "status" : fields.Boolean()
})

class BankList(Resource):
    @bank_ns.doc("Get all the banks")
    def get(self):
        return bank_list_schema.dump(BankModel.find_all()),200
    
    @bank_ns.expect(bank)
    @bank_ns.doc("Create a bank")
    def post(self):
        bank_json = request.get_json()
        bank_data = bank_schema(bank_json)
        bank_data.save_to_db()

        return bank_schema.dump(bank_data)