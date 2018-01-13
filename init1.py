#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import datetime
import hashlib

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='pricosha',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route to hello function
@app.route('/')
def hello():
	return render_template('index.html')

#Define route for login
@app.route('/login')
def login():
	return render_template('login2.html')

#Define route for register
@app.route('/register')
def register():
	return render_template('register.html')

#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']
	m = hashlib.md5(password.encode())
	hash_password = m.hexdigest()

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM person WHERE username = %s and password = %s'
	cursor.execute(query, (username, hash_password))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['username'] = username
		return redirect(url_for('home'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('login2.html', error=error)

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']
	fname = request.form['fname']
	lname = request.form['lname']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM person WHERE username = %s'
	cursor.execute(query, (username))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('register2.html', error = error)
	else:
		ins = 'INSERT INTO person VALUES(%s, %s, %s, %s)'
		cursor.execute(ins, (username, password, fname, lname))
		conn.commit()
		cursor.close()
		return render_template('home.html')

@app.route('/home')
def home():
	username = session['username']
	cursor = conn.cursor();
	query = 'SELECT item_date, caption FROM content WHERE poster_username = %s ORDER BY item_date DESC'
	query_2 = 'SELECT pro_pic FROM person WHERE username = %s'
	query_3 = 'SELECT * FROM person'
	#'SELECT ts, blog_post FROM blog WHERE username = %s ORDER BY ts DESC'
	cursor.execute(query, (username))
	data = cursor.fetchall()
	cursor.execute(query_2, (username))
	pic = cursor.fetchall()
	cursor.execute(query_3)
	people = cursor.fetchall()
	cursor.close()
	return render_template('home.html', username=username, proPic=pic, posts=data, users=people)



		
@app.route('/post', methods=['GET', 'POST'])
def post():
	username = session['username']
	now = datetime.datetime.now()
	cap = request.form['blog']
	cursor = conn.cursor();
	#blog = request.form['blog']
	query = 'INSERT INTO content (poster_username, item_date, caption, is_pub) VALUES(%s, %s, %s, %s)'
	if(request.form.get('private')):
		cursor.execute(query, (username, now, cap, 0))
	else:
		cursor.execute(query, (username, now, cap, 1))


	conn.commit()
	cursor.close()
	return redirect(url_for('home'))

@app.route('/logout')
def logout():
	session.pop('username')
	return redirect('/')

@app.route('/dash')
def dash():
	username = session['username']
	cursor = conn.cursor()
	query = 'SELECT * FROM content WHERE is_pub GROUP BY item_date DESC'
	query_2 = 'SELECT pro_pic FROM person WHERE username = %s'
	query_3 = 'SELECT * FROM tag NATURAL JOIN (SELECT * FROM content JOIN person ON username=poster_username)a WHERE status = 1'

	cursor.execute(query)
	data = cursor.fetchall()
	cursor.execute(query_2, (username))
	pic = cursor.fetchall()
	cursor.execute(query_3,)
	tagged = cursor.fetchall()
	return render_template('dash2.html', feed=data, proPic=pic, tagged=tagged)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
	username =session['username']
	cursor = conn.cursor()
	query = 'SELECT * FROM person WHERE username = %s'
	query_2 = 'SELECT pro_pic FROM person WHERE username = %s'
	cursor.execute(query, (username))
	data = cursor.fetchall()
	cursor.execute(query_2, (username))
	pic = cursor.fetchall()
	return render_template('profile.html', info=data, proPic=pic, username=username)

@app.route('/friends', methods=['GET','POST'])
def friends():
	username = session['username']
	cursor = conn.cursor();
	query = 'SELECT * FROM friends WHERE friend1=%s OR friend2=%s'
	query_2 = 'SELECT pro_pic FROM person WHERE username = %s'
	cursor.execute(query, (username, username))
	data = cursor.fetchall()
	cursor.execute(query_2, (username))
	pic = cursor.fetchall()
	return render_template('friends.html', data=data, proPic=pic)
		
@app.route('/friendRequest', methods=['GET','POST'])
def friendRequest():
	username = session['username']
	cursor = conn.cursor()
	query = 'SELECT * FROM content WHERE poster_username = %s'
	query_2 = 'SELECT pro_pic FROM person WHERE username = %s'
	query_3 = 'SELECT * FROM person '
	cursor.execute(query, (username))
	content = cursor.fetchall()
	cursor.execute(query_2, (username))
	pic = cursor.fetchall()
	cursor.execute(query_3)
	users = cursor.fetchall()
	return render_template('friendRequest.html', proPic=pic, content=content, users=users)

@app.route('/searchFriends', methods=['POST'])
def searchFriends():
	searching = request.form['search']
	cursor = conn.cursor()
	query = 'SELECT * FROM person WHERE first_name = %s'
	cursor.execute(query,(searching))
	data = cursor.fetchall()
	cursor.close()
	return render_template('friendRequest.html', newfriends=data)

@app.route('/sendRequest', methods=['GET', 'POST'])
def sendRequest():
	sender = session['username']
	reciever = request.form['user']
	cursor = conn.cursor()
	query = 'INSERT INTO friendrequests (ID, requester, requestee) VALUES(NULL, %s, %s)'
	cursor.execute(query,(sender, reciever))
	conn.commit()
	cursor.close()
	return render_template('friendRequest.html')

@app.route('/friendGroups', methods=['GET', 'POST'])
def friendGroups():
	username = session['username']
	cursor = conn.cursor()
	query = 'SELECT * FROM friendgroup WHERE owner_username = %s'
	query_2 = 'SELECT pro_pic FROM person WHERE username = %s'
	query_3 = 'SELECT * FROM person '
	cursor.execute(query, (username))
	data = cursor.fetchall()
	cursor.execute(query_2, (username))
	pic = cursor.fetchall()
	cursor.execute(query_3)
	people = cursor.fetchall()
	cursor.close()

	return render_template('friendGroups.html', groups=data, proPic=pic, users=people)

@app.route('/content', methods=['POST'])
def content():
	cont = request.form.get('the_content')
	return cont #render_template('content.html')

@app.route('/tagRequest', methods=['POST'])
def tagRequest():
	username = session['username']
	content = request.form['content']
	user = request.form['users']
	now = datetime.datetime.now()
	cursor = conn.cursor()
	query = 'INSERT INTO tag VALUES(%s, %s, %s, 0, %s)'
	cursor.execute(query, (user, username, now, content))
	conn.commit()
	cursor.close()
	return render_template('friendRequest.html')

@app.route('/yourRequests', methods=['POST', 'GET'])
def yourRequests():
	username = session['username']
	cursor = conn.cursor()
	query = 'SELECT * FROM friendrequests WHERE requestee = %s'
	tagrequests = 'SELECT * FROM tag NATURAL JOIN content WHERE tagee = %s AND status = 0'
	query_2 = 'SELECT pro_pic FROM person WHERE username = %s'
	cursor.execute(query, (username))
	data = cursor.fetchall()
	cursor.execute(tagrequests, (username))
	data2 = cursor.fetchall()
	cursor.execute(query_2, (username))
	pic = cursor.fetchall()
	cursor.close();
	return render_template('yourRequests.html', the_requests=data, tag_requests=data2, proPic=pic)

@app.route('/acceptRequest', methods=['POST', 'GET'])
def acceptRequest():
	username = session['username']
	the_request = request.form['select_request']
	cursor = conn.cursor()
	query = 'INSERT INTO friends VALUES(%s, %s, NULL); DELETE FROM friendrequests WHERE requestee=%s AND requester=%s'
	cursor.execute(query, (username, the_request, username, the_request))
	cursor.close();
	return render_template('yourRequests.html')

@app.route('/acceptTag', methods=['POST', 'GET'])
def acceptTag():
	username = session['username']
	the_tag = request.form['select_tag']
	cursor = conn.cursor()
	query = 'UPDATE tag SET status = 1 WHERE ID = %s AND tagee = %s'
	query_2 = 'DELETE FROM tag WHERE ID = %s AND tagee = %s'
	
	if (request.form.get('choice')):
		cursor.execute(query, (the_tag, username))
	else:
		cursor.execute(query_2, (the_tag, username))

	cursor.execute(query, (the_tag, username))
	conn.commit()
	#cursor.execute(query, (username, the_request, username, the_request))
	cursor.close();
	return redirect(url_for('yourRequests'))

@app.route('/rejectRequest', methods=['POST', 'GET'])
def rejectRequests():
	return 'test'

@app.route('/changePic', methods=['POST', 'GET'])
def changePic():
	username =session['username']
	picURL = request.form['newProPic']
	cursor = conn.cursor()
	query = 'SELECT * FROM person WHERE username = %s'
	query_2 = 'SELECT pro_pic FROM person WHERE username = %s'
	query_3 = 'UPDATE person SET pro_pic = %s WHERE username = %s'
	cursor.execute(query_3, (picURL, username))
	conn.commit()
	cursor.execute(query, (username))
	data = cursor.fetchall()
	cursor.execute(query_2, (username))
	pic = cursor.fetchall()
	return render_template('profile.html', info=data, proPic=pic, username=username)

@app.route('/taggedList', methods=['POST','GET'])
def taggedList():
	ID = request.form['cont_ID']
	cursor = conn.cursor()
	query = 'SELECT * FROM (tag JOIN person ON username=tagee) NATURAL JOIN content WHERE status = 1 AND ID = %s'
	cursor.execute(query, (ID))
	data = cursor.fetchall()
	return render_template('taggedList.html', tagged=data)

@app.route('/commentList', methods=['POST','GET'])
def commentList():
	ID = request.form['cont_ID']
	cursor = conn.cursor()
	query = 'SELECT * FROM comments NATURAL JOIN content WHERE ID = %s'
	cursor.execute(query, (ID))
	data = cursor.fetchall()
	return render_template('commentList.html', comments=data)

@app.route('/addToFriendGroup', methods=['POST','GET'])
def addToFriendGroup():
	username = session['username']
	user = request.form['users']
	group = request.form['groups']
	cursor = conn.cursor()
	query = 'INSERT INTO member VALUES(%s, %s, %s)'
	cursor.execute(query, (user, group, username))
	conn.commit()
	cursor.close()
	return render_template('friendGroups.html')


@app.route('/makegroup', methods=['GET', 'POST'])
def makegroup():
	username = session['username']
	title= request.form.get("title")
	friend = request.form.get("fuser1")
	cursor = conn.cursor()
	query='SELECT username FROM person WHERE username = %s'
	cursor.execute(query, (friend,))
	data = cursor.fetchone()
	if(data):
		cursor = conn.cursor()
		groupalreadyexist='SELECT name FROM friendgroup WHERE owner_username = %s AND name=%s'
		cursor.execute(groupalreadyexist,(username,title,))
		data1 = cursor.fetchone()
	if(data1 ==None):
		n='INSERT INTO friendgroup(Name, owner_username) VALUES(%s,%s)'
		cursor.execute(n, (title, username))
		p='INSERT INTO member(member,owner,Name) VALUES(%s,%s,%s)'
		cursor.execute(p, (friend, username,title))
	cursor.close()
	return redirect(url_for('friendgroup'))

app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
