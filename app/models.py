from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db, login
from flask_login import UserMixin


class User(UserMixin, db.Model):
	email = db.Column(db.String(120), index=True, primary_key=True)
	password_hash = db.Column(db.String(128))

	def set_password(self,password):
		self.password_hash = generate_password_hash(password)

	def check_password(self,password):
		return check_password_hash(self.password_hash,password)

def __repr__(self):
	return '<User {}>'.format(self.email)

class Customer(db.Model):
	email = db.Column(db.String(120), index=True, primary_key=True)
	addressState = db.Column(db.String(120))
	expMonth = db.Column(db.Integer)
	expYear = db.Column(db.Integer)
	addressCity = db.Column(db.String(40))
	addressZip = db.Column(db.Integer)
	cvv =db.Column(db.Integer)
	cardNumber = db.Column(db.Integer, primary_key=True)

def __repr__(self):
	return '<Customer {}>'.format(self.body)

class Card(db.Model):
	addressState = db.Column(db.String(120))
	expMonth = db.Column(db.Integer)
	expYear = db.Column(db.Integer)
	addressCity = db.Column(db.String(40))
	addressZip = db.Column(db.Integer)
	cvv =db.Column(db.Integer)
	number = db.Column(db.Integer, primary_key=True)

# class UtilityBill(db.Model):
# 	billId = db.Column()
# 	accountNumber = db.Column(db.String(40))
# 	accountHolder = db.Column(db.String(120))
# 	billingAddress = db.Column(db.String(120))
# 	usage = db.Column(db.String(20))
# 	duePayment = db.Column(db.String(40))

# class Bill(db.Model):
# 	billId = db.Column(db.Integer, primary_key=True)
# 	billType = db.Column(db.String(40), default="Utility")
# 	bill = db.Column(UtilityBill)



def __repr__(self):
	return '<Card {}>'.format(self.body)


@login.user_loader
def load_user(email):
	return User.query.get(email)