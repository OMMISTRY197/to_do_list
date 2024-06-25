from flask import Flask,redirect,render_template,request,url_for,session,send_from_directory
from flask_mysqldb import MySQL
import MySQLdb.cursors
import base64
from datetime import date, timedelta
from flask_bcrypt import Bcrypt 
import os

app = Flask(__name__)
bcrypt = Bcrypt(app) 

app.secret_key = 'happpyyyy_birthdayyyy_om'
# app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(seconds=5)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345'
app.config['MYSQL_DB'] = 'todolist'

mysql = MySQL(app)

@app.route('/favicon.ico')
def fav():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico')

@app.route('/index')
def index():
    if 'loggedin' in session:
        username = session['username']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('select * from todoreg where username=%s',(username,))
        account = cur.fetchone()
        
        encoded_image = base64.b64encode(account['image']).decode('utf-8')
        account['encoded_image'] = encoded_image

        if account:
            return render_template('index.html',account=account)
        else:
            return render_template('login.html')
    else:
        return redirect(url_for('login'))

@app.route('/register')
def insert():
    msg = ''
    return render_template('registration.html',msg = msg)

@app.route('/addtask/<int:id>',methods = ['GET','POST'])
def addtask(id):
    if request.method == 'POST':
        if 'id' in session:
            task_name = request.form['taskName']
            start_date = date.today()
            print(str(start_date))
            comp_date = request.form['completionDate']
            status = request.form['status']
            user_id = session['id']

            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute('insert into todotask(task_name, start_date, complition_date, status, user_id) values (%s,%s,%s,%s,%s)',(task_name,start_date,comp_date,status,user_id,))
            mysql.connection.commit()

            return redirect(url_for('index'))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('select * from todoreg where user_id = %s',(id,))
    account = cur.fetchone()

    encoded_image = base64.b64encode(account['image']).decode('utf-8')
    account['encoded_image'] = encoded_image

    return render_template('addTask.html', account = account)

@app.route('/viewtask/<int:id>',methods = ['GET','POST'])
def viewtask(id):
    if 'id' in session:
        user_id = session['id']

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('select * from todoreg where user_id = %s',(user_id,))
        account = cur.fetchone()

        encoded_image = base64.b64encode(account['image']).decode('utf-8')
        account['encoded_image'] = encoded_image

        cur.execute("select * from todotask where user_id = %s and status != 'completed'",(user_id,))
        account1 = cur.fetchall()

        return render_template('allTask.html', account = account, account1 = account1)
    
@app.route('/completedtask/<int:id>',methods = ['GET','POST'])
def completedtask(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('select * from todoreg where user_id = %s',(id,))
    account = cur.fetchone()

    encoded_image = base64.b64encode(account['image']).decode('utf-8')
    account['encoded_image'] = encoded_image

    cur.execute("select * from todotask where user_id = %s and status = 'completed'",(id,))
    account1 = cur.fetchall()

    return render_template('completedTask.html', account = account, account1 = account1)

@app.route('/updatetaskstatus/<int:id>', methods = ['GET','POST'])
def updatetaskstatus(id):
    if request.method == 'POST':
        status = request.form['status']

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('update todotask set status = %s where task_id = %s',(status,id,))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('viewtask', id = id))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('select * from todotask where task_id = %s',(id,))
    result1 = cur.fetchone()
    cur.close()

    uId = session['id']
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('select * from todoreg where user_id = %s',(uId,))
    result = cur.fetchone()
    cur.close()

    encoded_image = base64.b64encode(result['image']).decode('utf-8')
    result['encoded_image'] = encoded_image   

    return render_template('updateTaskStatus.html',account1 = result1, account = result)

@app.route('/store',methods = ['GET','POST'])
def store():
    if request.method == 'POST':
        u_name = request.form['username']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('select * from todoreg where username=%s',(u_name,))
        account = cur.fetchone()

        if account:
            msg = 'Account Already Exists!!'
            render_template('registration.html',msg=msg)
        else:
            u_name = request.form['username']
            f_name = request.form['fname']
            m_name = request.form['mname']
            l_name = request.form['lname']
            mobile = request.form['mobile']
            email = request.form['email']
            dob = request.form['dob']
            gender = request.form['gender']
            address = request.form['address']
            state = request.form['state']
            city = request.form['city']
            hobby = request.form.getlist('hobby')
            hobbies = ','.join(hobby)
            password = request.form['password']
            f = request.files['file']

            hashed_password = bcrypt.generate_password_hash (password).decode('utf-8') 
            print(hashed_password)
            
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute('insert into todoreg(username, firstname, middlename, lastname, mobile, email, birthdate, gender, address, state, city, hobbies, password, filename, image) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',(u_name,f_name,m_name,l_name,mobile, email, dob, gender, address, state,city,hobbies,hashed_password,f.filename,f.read(),))
            mysql.connection.commit()

            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute('select * from todoreg where username = %s', (u_name,))
            account = cur.fetchone()

            encoded_image = base64.b64encode(account['image']).decode('utf-8')
            account['encoded_image'] = encoded_image

            return redirect(url_for('login'))
        
    return render_template('registration.html')

@app.route('/delete/<int:id>')
def delete(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('delete from todoreg where user_id = %s',(id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('alldisplay'))

@app.route('/userdelete/<int:id>')
def userdelete(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('delete from todoreg where user_id = %s',(id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('login'))

@app.route('/update/<int:id>', methods=['GET','POST'])
def update(id):
    if request.method == 'POST':
        u_name = request.form['username']
        f_name = request.form['fname']
        m_name = request.form['mname']
        l_name = request.form['lname']
        mobile = request.form['mobile']
        email = request.form['email']
        dob = request.form['dob']
        gender = request.form['gender']
        address = request.form['address']
        state = request.form['state']
        city = request.form['city']
        hobby = request.form.getlist('hobby')
        hobbies = ','.join(hobby)
        f = request.files['file']

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('update todoreg set username = %s, firstname = %s, middlename = %s, lastname = %s, mobile = %s, email = %s, birthdate = %s, gender = %s, address = %s, state = %s, city = %s, hobbies = %s, filename = %s,image = %s where user_id = %s',(u_name,f_name,m_name,l_name,mobile,email,dob,gender,address,state,city,hobbies,f.filename,f.read(),id,))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('index'))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('select * from todoreg where user_id = %s',(id,))
    result = cur.fetchone()

    encoded_image = base64.b64encode(result['image']).decode('utf-8')
    result['encoded_image'] = encoded_image
    
    return render_template('update.html',account = result)

@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password1 = request.form['password']

        mycursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        mycursor.execute('select * from todoreg where username = %s ',(username,))
        account = mycursor.fetchone()

        if account and bcrypt.check_password_hash(account['password'], password1):
            encoded_image = base64.b64encode(account['image']).decode('utf-8')
            account['encoded_image'] = encoded_image

            session['loggedin'] = True
            session['id'] = account['user_id']
            session['username'] = account['username']
            return redirect(url_for('index',account=account['username']))
        
        else:
            msg = 'Incorrect Username/Password !'
            return render_template('login.html',msg=msg)

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/updatepass/<int:id>',methods = ['POST','GET'])
def updatepass(id):
    msg = ''
    if request.method == 'POST' and 'oldPassword' in request.form and 'newPassword' in request.form:
        oPassword = request.form['oldPassword']
        nPassword = request.form['newPassword']
        username = session['username']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('select * from todoreg where username=%s',(username,))
        account = cur.fetchone()
        is_true = bcrypt.check_password_hash(account['password'], oPassword)
        if is_true:
            if account:
                cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                hashed_password = bcrypt.generate_password_hash (nPassword).decode('utf-8')
                print(hashed_password)
                cur.execute('UPDATE todoreg set password = %s where user_id = %s', (hashed_password,id,))
                mysql.connection.commit()
                
                return redirect(url_for('index'))
        else:
            msg = "Old Password is Doesn't match"
            
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('select * from todoreg where user_id=%s',(id,))
    account = cur.fetchone()

    encoded_image = base64.b64encode(account['image']).decode('utf-8')
    account['encoded_image'] = encoded_image

    return render_template('updatepass.html', account=account, msg = msg)

#----------------------------------------------------------
#---------------------- ADMIN VIEWS -----------------------
#----------------------------------------------------------

@app.route('/adminindex')
def adminindex():
    if 'loggedin' in session:
        username = session['username']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('select * from todoadmin where username=%s',(username,))
        account = cur.fetchone()
        
        encoded_image = base64.b64encode(account['image']).decode('utf-8')
        account['encoded_image'] = encoded_image

        if account:
            return render_template('adminIndex.html',account=account)
        else:
            return render_template('adminLogin.html')
    else:
        return redirect(url_for('adminlogin'))

@app.route('/adminstore',methods = ['GET','POST'])
def adminstore():
    if request.method == 'POST':
        u_name = request.form['username']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('select * from todoadmin where username=%s',(u_name,))
        account = cur.fetchone()

        if account:
            msg = 'Account Already Exists!!'
            render_template('adminRegistration.html',msg=msg)
        else:
            u_name = request.form['username']
            email = request.form['email']
            password = request.form['password']
            f = request.files['file']

            hashed_password = bcrypt.generate_password_hash (password).decode('utf-8') 
            
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute('insert into todoadmin(username, email, password, image) values(%s,%s,%s,%s)',(u_name,email,hashed_password,f.read(),))
            mysql.connection.commit()

            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute('select * from todoadmin where username = %s', (u_name,))
            account = cur.fetchone()

            encoded_image = base64.b64encode(account['image']).decode('utf-8')
            account['encoded_image'] = encoded_image

            return redirect(url_for('adminlogin'))
        
    return render_template('adminRegister.html')

@app.route('/adminUpdate/<int:id>', methods=['GET','POST'])
def adminupdate(id):
    if request.method == 'POST':
        u_name = request.form['username']
        email = request.form['email']
        f = request.files['file']

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('update todoadmin set username = %s, email = %s, image = %s where id = %s',(u_name,email,f.read(),id,))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('adminindex'))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('select * from todoadmin where id = %s',(id,))
    account = cur.fetchone()

    encoded_image = base64.b64encode(account['image']).decode('utf-8')
    account['encoded_image'] = encoded_image

    return render_template('adminUpdate.html',account = account)

@app.route('/admin', methods=['GET','POST'])
def adminlogin():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        mycursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        mycursor.execute('select * from todoadmin where username = %s ',(username,))
        account = mycursor.fetchone()

        if account and bcrypt.check_password_hash(account['password'], password):
            encoded_image = base64.b64encode(account['image']).decode('utf-8')
            account['encoded_image'] = encoded_image

            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('adminindex',account=account['username']))
        
        else:
            msg = 'Incorrect Username/Password !'
            return render_template('adminLogin.html',msg=msg)
        
    return render_template('adminLogin.html')

@app.route('/adminlogout')
def adminlogout():
    session.clear()
    return redirect(url_for('adminlogin'))

@app.route('/admindelete/<int:id>')
def admindelete(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('delete from todoadmin where id = %s',(id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('adminlogin'))

@app.route('/adminupdatepass/<int:id>',methods = ['POST','GET'])
def adminupdatepass(id):
    msg = ''
    if request.method == 'POST' and 'oldPassword' in request.form and 'newPassword' in request.form:
        oPassword = request.form['oldPassword']
        nPassword = request.form['newPassword']
        username = session['username']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('select * from todoadmin where username=%s',(username,))
        account = cur.fetchone()
        is_true = bcrypt.check_password_hash(account['password'], oPassword)
        if is_true:
            if account:
                cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                hashed_password = bcrypt.generate_password_hash (nPassword).decode('utf-8')
                print(hashed_password)
                cur.execute('UPDATE todoadmin set password = %s where id = %s', (hashed_password,id,))
                mysql.connection.commit()
                
                return redirect(url_for('adminindex'))
        else:
            msg = "Old Password is Doesn't match"

    user_id = session['id']
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('select * from todoadmin where id=%s',(user_id,))
    account = cur.fetchone()

    encoded_image = base64.b64encode(account['image']).decode('utf-8')
    account['encoded_image'] = encoded_image

    return render_template('adminUpdatePass.html', account=account, msg = msg)

@app.route('/adminallusers',methods = ['GET'])
def adminallusers():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('select * from todoreg')
    account = cur.fetchall()

    encoded_images = []
    for row in account:
        id = row['user_id']
        usename = row['username']
        email = row['email']
        image = row['image']

        encoded_image = base64.b64encode(image).decode('utf-8')
        encoded_images.append({'id': id, 'username':usename, 'email':email, 'encoded_image': encoded_image})

    return render_template('adminAllUsers.html',account = encoded_images)

@app.route('/adminalltasks',methods = ['GET'])
def adminalltasks():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('select * from todotask inner join todoreg on todotask.user_id = todoreg.user_id')
    account = cur.fetchall()

    return render_template('adminAllTask.html',account = account)

@app.route('/adminoneuser/<int:id>',methods = ['GET'])
def adminoneuser(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('select * from todoreg where user_id = %s',(id,))
    account = cur.fetchone()
    
    encoded_image = base64.b64encode(account['image']).decode('utf-8')
    account['encoded_image'] = encoded_image

    if account:
        return render_template('adminOneUser.html',account=account)
    
@app.route('/adminonetask/<int:id>',methods = ['GET'])
def adminonetask(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('select * from todotask where user_id = %s',(id,))
    account = cur.fetchall()

    return render_template('adminOneTask.html',account=account)

if __name__ == '__main__':
    app.run(debug=True)