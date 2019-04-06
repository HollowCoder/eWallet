from flask import render_template, flash, redirect, url_for, request, jsonify 
from app.forms import RegistrationForm, LoginForm, AddCustomerForm, AddCardForm, PayBillForm 
from app import app, db
from flask_login import current_user, login_user, login_required, logout_user
from app.models import User, Card, UtilityBill
from tasks import getUtilityBill
from redis import Redis
import rq
from rq import get_current_job, Queue
from rq.job import Job
import simplify
import json
import requests
import time

simplify.public_key = "sbpb_Njc3ZDkyMmYtYTE0OS00MTRjLWE5YmUtZjQ3MTI5ZWUzNmE3"
simplify.private_key = "3KzZq8dCCUhQMh1dTCU6jPrwdG0O4wwwizAP82LcfpN5YFFQL0ODSXAOkNtXTToq"
job_id = ''
queue = rq.Queue(connection=Redis.from_url('redis://'))
queue.delete(delete_jobs=True)
queue = rq.Queue('tasks', connection=Redis.from_url('redis://'))


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

@app.route('/selectBill', methods=['GET','POST'])
def selectBill():
	return render_template('selectBill.html', title='Select Bill')

@app.route('/selectUtility', methods=['GET','POST'])
def selectUtility():
	return render_template('selectUtility.html', title='Select Utility')

@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
	# mylist = []
	# payments = simplify.Payment.list({"max": 30})
	# paymentlist = payments.list
	# for payment in paymentlist:
	# 	mylist.append[{"y": payment[0]}]
	return render_template('dashboard.html', title='Dashboard')

@app.route('/getdashboard', methods=['GET','POST'])
def getdashboard():
	mylist = []
	payments = simplify.Payment.list({"max": 50})
	paymentlist = payments.list
	for payment in paymentlist:
		newlist = []
		bill = payment["amount"]
		newlist.append(bill)
		mylist.append(newlist)
	jsonify(mylist)
	print(mylist)
	return jsonify(mylist)


@app.route('/viewRecentBills', methods=['GET','POST'])
def viewRecentBills():
	global queue
	global job_id
	job = queue.enqueue('app.tasks.getUtilityBill')
	job.refresh()
	job_id = str(job.get_id())
	loading = """
	<div class="d-flex justify-content-center">
  		<div class="spinner-border" role="status">
    	<span class="sr-only">Loading...</span>
  		</div>
		</div>
	"""
	return render_template('viewRecentBills.html', title='Due Bill', loading=loading)	

@app.route('/notifications')
def notifications():
	global queue
	global job_id
	result = ''	
	# myjobs = queue.jobs
	# mylength = len(myjobs)
	myJobId = job_id
	job = queue.fetch_job(myJobId)
	#job = Job.fetch("b3893fc8-a6ea-4637-abb9-2e01e19f8f97", connection=Redis.from_url('redis://'))
	job.refresh()
	if job.is_finished:
		# meta = job.meta
		# progress = meta["progress"]
		utilityBills = UtilityBill.query.all()
		latestBill = utilityBills[-1]
		billId = latestBill.billId
		result= """
		<div class="list-group">
  		<a href="#" class="list-group-item list-group-item-action active">
    	<div class="d-flex w-100 justify-content-between">
      	<h4 class="mb-1">Due Bill</h4>
    	</div>
		<a href="#" class="list-group-item list-group-item-action">
    	<div class="d-flex w-100 justify-content-between">
      	<h5 class="mb-1">ConEd</h5>
      	<small class="text-muted">"""+latestBill.usage+""" kwh</small>
    	</div>
    	<p class="mb-1">$"""+latestBill.duePayment+"""</p>
    	<small class="text-muted">Account: """+latestBill.accountNumber+"""
    	Contact: """+latestBill.accountHolder+"""</small>
    	<small class="text-muted">"""+latestBill.billingAddress+"""</small>
  		</a>
  		<a href="/payBillForm" class="btn btn-primary">Pay Now</a>
		"""
		# result = "Completed"
		bill = UtilityBill.query.filter_by(billId=billId).first()
		bill.complete = True
		db.session.commit()
		queue.delete(delete_jobs=True)
	else:
		# meta = job.meta
		# progress = meta["progress"]
		result = """
		<div align="center">
		<div class="spinner-grow text-primary" role="status">
  		<span class="sr-only">Loading...</span>
		</div>
		<br>
		<br>
		<span>Downloading...</span>
		</div>
		</div>"""
	return result

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
		flash ('Payment was succesfully!')
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
# <<<<<<<<<<<<This is IMAYA's CODE BEGIN>>>>>>>>>>>>>>>>>>>>>

@app.route('/recentpayments', methods=["GET"])
def recentpayments():
	payments = simplify.Payment.list({"max": 30})
	paymentlist = payments.list
	return render_template('recentpayments.html',title='Recent Payments', paymentlist = paymentlist) 

@app.route('/payments', methods=["GET"])
def paymentdetail():
	payment_detail = simplify.Payment.find(request.args.get(id))
	return render_template('paymentdetail.html', payment_detail = payment_detail)
# <<<<<<<<<<<<This is IMAYA's CODE END>>>>>>>>>>>>>>>>>>>>> 
