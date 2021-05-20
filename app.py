from flask import Flask, request, Response, jsonify
from database.db import initialize_db
from database.models import *
from datetime import datetime
from decimal import *

app = Flask(__name__)

app.config['MONGODB_SETTINGS'] = {'host': 'mongodb://localhost/test'}

initialize_db(app)


# add new invoice
@app.route('/invoices', methods=['POST'])
def add_invoice():
    data_dict = request.get_json()
    invoice_obj = Invoice(customer=data_dict['customer'],
                          total_quantity=0,
                          total_amount=0)
    invoice_obj.save()
    total_amount = 0
    total_quantity = 0
    for transaction in data_dict['transactions']:
      try:
          line_total = 0
          transaction_obj = Transaction(product=transaction['product'],
                                        quantity=transaction['quantity'],
                                        price=Decimal(transaction['price']),
                                        invoice=invoice_obj)
                                        
          line_total = Decimal(transaction['quantity']) * Decimal(
              transaction['price'])
          transaction_obj.line_total = Decimal(line_total)
          transaction_obj.save()
          total_amount = Decimal(total_amount) + line_total
          total_quantity = total_quantity + transaction['quantity']
      except Exception as e:
          invoice_obj.delete()
          print("Exception: {} - {}".format(type(e).__name__, type(e).__module__))
          return {type(e).__name__:  type(e).__module__}, 400
    invoice_obj.total_amount = total_amount
    invoice_obj.total_quantity = total_quantity
    invoice_obj.save()
    return {'id': str(invoice_obj._id)}, 200


# get all invoice
@app.route('/invoices')
def get_invoice():
    data_list = []
    for invoice in Invoice.objects.all():
        data_dict = {
            'id': str(invoice.id),
            'customer': invoice.customer,
            'total_amount': str(invoice.total_amount),
            'total_quantity': invoice.total_quantity,
            'date': invoice.date,
            'transactions': []
        }
        transactions_obj = Transaction.objects.filter(invoice=invoice)
        for transaction in transactions_obj:
            temp_dict = {}
            temp_dict['id'] = str(transaction.id)
            temp_dict['product'] = transaction.product
            temp_dict['quantity'] = transaction.quantity
            temp_dict['price'] = str(transaction.price)
            temp_dict['line_total'] = str(transaction.line_total)
            data_dict['transactions'].append(temp_dict)
        data_list.append(data_dict)
    return jsonify(data_list), 200


# get one particular invoice by id
@app.route('/invoices/<id>', methods=['GET'])
def get_single_invoice(id):
    invoice = Invoice.objects.get(_id=id)
    data_dict = {
        'id': str(invoice.id),
        'customer': invoice.customer,
        'total_amount': str(invoice.total_amount),
        'total_quantity': invoice.total_quantity,
        'date': invoice.date,
        'transactions': []
    }
    transactions_obj = Transaction.objects.filter(invoice=invoice)
    for transaction in transactions_obj:
        temp_dict = {}
        temp_dict['id'] = str(transaction.id)
        temp_dict['product'] = transaction.product
        temp_dict['quantity'] = transaction.quantity
        temp_dict['price'] = str(transaction.price)
        temp_dict['line_total'] = str(transaction.line_total)
        data_dict['transactions'].append(temp_dict)
    return jsonify(data_dict), 200


# get one particular invoice by id
@app.route('/invoices/<id>', methods=['PUT'])
def update_invoice(id):
    data_dict = request.get_json()
    invoice_obj = Invoice.objects.get(_id=id)

    total_amount = 0
    total_quantity = 0
    transaction_id_list = []

    # remove the transaction which are removed from JSON

    for transaction in data_dict['transactions']:
        transaction_id_list.append(transaction['id'])
      
    for transaction_id in Transaction.objects.filter(invoice=invoice_obj).values_list('_id'):
      if transaction_id not in transaction_id_list:
        Transaction.objects.filter(_id=transaction_id).delete()

    for transaction in data_dict['transactions']:
      line_total = 0
      if Transaction.objects.filter(_id=transaction['id']):
          line_total = Decimal(transaction['quantity']) * Decimal(transaction['price'])
          Transaction.objects.filter(_id=transaction['id']).update(
              product=transaction['product'],
              quantity=transaction['quantity'],
              price=Decimal(transaction['price']),
              line_total=Decimal(line_total))
          total_amount = total_amount + line_total
          total_quantity = total_quantity + transaction['quantity']
      else:
          transaction_obj = Transaction(product=transaction['product'],
                                        quantity=transaction['quantity'],
                                        price=Decimal(transaction['price']),
                                        invoice=invoice_obj)
          line_total = Decimal(transaction['quantity']) * Decimal(transaction['price'])
          transaction_obj.line_total = Decimal(line_total)
          transaction_obj.save()
          total_amount = total_amount + line_total
          total_quantity = total_quantity + transaction['quantity']

    Invoice.objects.filter(_id=id).update(total_amount=total_amount,
                                          total_quantity=total_quantity,
                                          customer=data_dict['customer'])

    return {'id': str(id)}, 200


# remove particular data
@app.route('/invoices/<id>', methods=['DELETE'])
def delete_invoice(id):
    Invoice.objects.get(_id=id).delete()
    return '', 200


# it cleans all the invoice data
@app.route('/delete')
def delete_all_invoice():
    Invoice.objects.all().delete()
    return '', 200


if __name__ == "__main__":
    app.run(debug=True, port=8000)