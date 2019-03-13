from flask import render_template, flash, redirect, url_for, request 
from app.forms import RegistrationForm, LoginForm, AddCustomerForm, AddCardForm, PayBillForm 
from app import app, db
from flask_login import current_user, login_user, login_required, logout_user
from app.models import User, Card
import simplify

simplify.public_key = "sbpb_Njc3ZDkyMmYtYTE0OS00MTRjLWE5YmUtZjQ3MTI5ZWUzNmE3"
simplify.private_key = "3KzZq8dCCUhQMh1dTCU6jPrwdG0O4wwwizAP82LcfpN5YFFQL0ODSXAOkNtXTToq"

@app.route('/')
@app.route('/index')
# @login_required
def index():
	return render_template('index.html')

@app.route('/login',methods=['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))
		login_user(user, remember= form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')
	return redirect(url_for('index'))
	return render_template('login.html',title='Sign In', form=form)


@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))


@app.route('/register', methods=['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(email = form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Congratulations, you are now registered!')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

@app.route('/manageCard',methods=['GET','POST'])
def manageCard():
	return render_template('manageCard.html',title='Manage Card')

@app.route('/manageBill',methods=['GET','POST'])
def manageBill():
	return render_template('manageBill.html',title='Manage Bill')

@app.route('/viewCards',methods=['GET','POST'])
def viewCards():
	cards = Card.query.all()
	return render_template('viewCards.html',title='View Cards', cards=cards)

@app.route('/addCardForm',methods=['GET','POST'])
def cardform():
	form = AddCardForm()
	if form.validate_on_submit():
		card = Card(addressState=form.addressState.data,expMonth=form.expMonth.data, expYear=form.expYear.data,
			addressCity=form.addressCity.data,addressZip=form.addressZip.data,cvv=form.cvv.data, number=form.number.data)
		db.session.add(card)
		db.session.commit()
		flash ('Card was added succesfully!')
		# flash('Add requested for the card {}'.format(
		# 	form.number.data))
		return redirect(url_for('index'))
	return render_template('addCardForm.html',title='Add Card', form=form)

@app.route('/payBillForm',methods=['GET','POST'])
def payBillForm():
	form = PayBillForm()
	cards = Card.query.all()
	if form.validate_on_submit():
		mycard = request.form.get('card')
		mycard = mycard.split(",")
		payment = {
		"amount": form.amount.data,
		"description": form.description.data, 
		"card": 
		{"number": mycard[0],
		"cvv": mycard[1], 
		"expMonth": mycard[2],
		"expYear": mycard[3]}
		 }
		payment = simplify.Payment.create(payment)
		# card = Card(addressState=form.addressState.data,expMonth=form.expMonth.data, expYear=form.expYear.data,
		# 	addressCity=form.addressCity.data,addressZip=form.addressZip.data,cvv=form.cvv.data, number=form.number.data)
		flash ('Card was added succesfully!')
		return redirect(url_for('index'))
	return render_template('payBillForm.html',title='Pay Bill', form=form,cards=cards)

@app.route('/',methods=["POST"])
def getValue():
	number = request.form['number']
	cvv = request.form['cvv']
	expMonth = request.form['expMonth']
	expYear = request.form['expYear']
	amount = request.form['amount']
	description = request.form['description']
	currency = request.form['currency']

	payment = simplify.Payment.create({
       "card" : {
            "number": number,
            "expMonth": expMonth,
            "expYear": expYear,
            "cvc": cvv
        },
        "amount" : amount,
        "description" : description,
        "currency" : currency
	})
	return redirect(url_for('index'))