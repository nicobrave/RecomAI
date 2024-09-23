# models.py
from db import db

class Contract:
    collection = db['contracts']

    @staticmethod
    def find_by_number(number):
        return Contract.collection.find_one({'number': number})

    @staticmethod
    def insert(contract_data):
        Contract.collection.insert_one(contract_data)

class ITO:
    collection = db['itos']

    @staticmethod
    def find_by_contract_number(contract_number):
        return ITO.collection.find_one({'contract_number': contract_number})

    @staticmethod
    def insert(ito_data):
        ITO.collection.insert_one(ito_data)

class Invoice:
    collection = db['invoices']

    @staticmethod
    def insert(invoice_data):
        Invoice.collection.insert_one(invoice_data)

    @staticmethod
    def find_pending():
        return Invoice.collection.find({'status': 'Pendiente'})
