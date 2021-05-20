from .db import db
from datetime import datetime
from mongoengine import SequenceField

class Invoice(db.Document):
  _id= db.SequenceField(primary_key=True)
  customer = db.StringField(required=True)
  date = db.DateTimeField(default=datetime.now)
  total_quantity = db.IntField(default=0)
  total_amount = db.DecimalField(required=True)
 

class Transaction(db.Document):
    _id= db.SequenceField(primary_key=True)
    product = db.StringField(required=True)
    quantity = db.IntField(default=0)
    price = db.DecimalField(required=True)
    line_total = db.DecimalField(required=True)
    invoice = db.ReferenceField(Invoice)