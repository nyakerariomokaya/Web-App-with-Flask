from flask import Flask, render_template, flash, request, url_for, redirect, session, Response
from dbconnect import connection

from wtforms import Form, BooleanField, TextField, PasswordField, validators
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
import gc
import flask_excel as excel
import csv


app = Flask(__name__)
app.secret_key = 'super secret key'
app.config["DEBUG"] = True

@app.route('/')
def index():

	c, conn = connection()

	c.execute("SELECT * FROM tbl_profiles")
	Details = [dict(id=row[0],
				  name=row[1],
				  id_number=row[2],
				  phone_number=row[3],
				  debt_amount=row[4]) for row in c.fetchall()]
	c.close()	
	return render_template("main.html", Details=Details)

@app.route('/hello', methods=['POST'])
def hello():
	user_input=None
	try:			
		c, conn = connection()
		if request.method == "POST":		
			c.execute("SELECT * FROM tbl_users WHERE phone_number = %s", request.form["phone_number"])	
			data = c.fetchone()[2]
			if int(x) ==0:
				error = "No users by that phone number"

			user.input = (request.form['search'],)	
			return render_template("results.html", data=data, user_input=user_input)

	except Exception as e:
		error =(str(e))
		return render_template("main.html", error=error, user_input=user_input)
	

class RegistrationForm(Form):
	username = TextField('Username', [validators.Length(min=4, max=20)] )
	password = PasswordField('Password', [validators.Required(),
										   validators.EqualTo('confirm',message = "Passwords must match.")])
	confirm = PasswordField('Repeat Password')
	accept_tos = BooleanField('I accept the <a href="/tos/">Terms of Service </a> and the <a href="/privacy/">Privacy Notice</a>', [validators.Required()])
	#validators.required() one must input
@app.route('/sign',  methods = ['GET','POST'])
def sign():
	error=''
	try:
		form = RegistrationForm(request.form)

		if request.method == "POST" and form.validate():
			username = form.username.data
			password = sha256_crypt.encrypt((str(form.password.data)))
			c, conn = connection()

			x = c.execute("SELECT * FROM tbl_users WHERE username = (%s)",
						 (thwart(username),))
			#select returns rows of data
			if int (x) > 0:
				#if length of rows is more than 0 the username already exists
				flash("That username is already taken, please choose another")
				#query for checking if username already exists
				return render_template('signup.html', form=form, flash=flash)

			else:
				c.execute("INSERT INTO tbl_users (username, password) VALUES (%s, %s)",
					(thwart(username), thwart(password),)) 
						   #insert query
				conn.commit()
				#persist changes to db
				flash("Thanks for registering!")

				c.close()
				#close cursor to release memory
				conn.close()
				gc.collect()

				session ['logged_in'] = True
				session['username'] = username

				return redirect(url_for('index'))

		return render_template("signup.html", form = form)

	except Exception as e:
		return(str(e))



@app.route("/logout/")
def logout():
	session.clear()
	flash("You have been logged out!")
	gc.collect()
	return redirect(url_for("index"))
	
@app.route('/login/', methods = ['GET','POST'])
def login_page():
	error = ''
	try:
		c, conn = connection()
		if request.method == "POST": 

			data = c.execute("SELECT * FROM tbl_users WHERE username = (%s)",
							  thwart(request.form['username']))

			data = c.fetchone()[2]

			if int(data) ==0:
			
				error = "Invalid credentials, try again"
			#fetch username from database and its the  first index 

			if sha256_crypt.verify(request.form['password'], data):
				#returns boolean comparing password given and password in database
				session['logged_in'] = True
				session['username'] = request.form['username']
				session['role'] = 2

				flash("You are now logged in")

				return redirect(url_for('index'))

			else:
				error = "Invalid credentials, try again"
		gc.collect()

				
		return render_template("login.html", error = error)
			# if user credectials don't match , login page persists
	except Exception as e:
		error = "Invalid credentials, try again"
		return render_template("login.html", error = error)

		#view module should be imported after the application object is created
		
@app.route("/download", methods=['POST'])
def download_file(): 	
	c, conn = connection()

	c.execute("SELECT * FROM tbl_profiles")
	Details = [dict(id=row[0],
			  name=row[1],
			  id_number=row[2],
			  phone_number=row[3],
			  debt_amount=row[4]) for row in c.fetchall()]
	c.close()	
	return excel.make_response_from_array([[1,2], [3, 4]], "csv", file_name="export_data")

if __name__ == '__main__':
	
	app.run()
