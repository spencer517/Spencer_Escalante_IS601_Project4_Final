from typing import List, Dict
import simplejson as json
from flask import Flask, request, Response, redirect, flash
from flask import render_template
from flaskext.mysql import MySQL
from flask_login import LoginManager, login_user, login_required, logout_user
from pymysql.cursors import DictCursor
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models import MyUser

app = Flask(__name__)
mysql = MySQL(cursorclass=DictCursor)
login_manager = LoginManager()
login_manager.init_app(app)

app.config['SECRET_KEY'] = 'GDtfDCFYjD'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_HOST'] = 'db'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_DB'] = 'heightWeight'
mysql.init_app(app)


@app.route('/', methods=['GET'])
def index():
    user = {'username' : 'Spencer'}
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tableHeightWeight')
    heightWeight = cursor.fetchall()
    return render_template('index.html', title='Home', user=user, heightsAndWeights = heightWeight)

@app.route('/view/<int:patient_id>', methods=['GET'])
def rec_view(patient_id):
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tableHeightWeight WHERE id=%s', patient_id)
    result = cursor.fetchall()
    return render_template('view.html', title='Home', patient=result[0])

@app.route('/edit/<int:patient_id>', methods=['GET'])
@login_required
def get_edit(patient_id):
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tableHeightWeight WHERE id=%s', patient_id)
    result = cursor.fetchall()
    return render_template('edit.html', title='Home', patient=result[0])

@app.route('/edit/<int:patient_id>', methods=['POST'])
@login_required
def update_post(patient_id):
    cursor = mysql.get_db().cursor()
    data = (request.form.get('fldIndex'), request.form.get('fldHeight_Inches'), request.form.get('fldWeight_Pounds'), patient_id)
    update_query = """UPDATE tableHeightWeight hw SET hw.fldIndex = %s, hw.fldHeight_Inches = %s, hw.fldWeight_Pounds = %s  WHERE hw.id = %s """
    cursor.execute(update_query, data)
    mysql.get_db().commit()
    return redirect("/", code=302)

@app.route('/patients/new', methods=['GET'])
def new_patient():
    return render_template('newpatient.html', title='New Patient')

@app.route('/patients/new', methods=['POST'])
@login_required
def new_patient_insert():
    cursor = mysql.get_db().cursor()
    data = (request.form.get('fldIndex'), request.form.get('fldHeight_Inches'), request.form.get('fldWeight_Pounds'))
    new_patient_query = """INSERT into tableHeightWeight (fldIndex,fldHeight_Inches,fldWeight_Pounds) VALUES (%s, %s,%s)"""
    cursor.execute(new_patient_query, data)
    mysql.get_db().commit()
    return redirect("/", code=302)

@app.route('/delete/<int:patient_id>', methods=['POST'])
@login_required
def remove_patient(patient_id):
    cursor = mysql.get_db().cursor()
    delete_patient_query = """DELETE FROM tableHeightWeight WHERE id = %s """
    cursor.execute(delete_patient_query, patient_id)
    mysql.get_db().commit()
    return redirect("/", code=302)

@app.route('/patients/signup', methods=['GET'])
def signup_patient():
    return render_template('signup.html', title='Patient Signup')

@app.route('/patients/signup', methods=['POST'])
def signup_patient_insert():
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM users WHERE email=%s', request.form.get('fldEmail'))
    result = cursor.fetchall()
    if len(result) is 0:
        pswd = generate_password_hash(
            request.form.get('fldPassword'),
            method='sha256'
        )
        data =(request.form.get('fldEmail'),pswd)
        new_patient_signup = """INSERT into users (email, password) VALUES (%s,%s)"""
        cursor.execute(new_patient_signup, data)
        mysql.get_db().commit()
        flash('Signup Successful')
        return redirect("/", code=302)
    flash('Error there is already a user with that email please enter a new email.')
    return render_template('signup.html', title='Patient Signup')

@app.route('/patients/login', methods=['GET'])
def login_page_render():
    return render_template('login.html', title='Patient Login')

@app.route('/patients/login', methods=['POST'])
def login_patient():
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM users WHERE email=%s', request.form.get('fldEmail'))
    result = cursor.fetchall()
    checked = check_password_hash(result[0]['password'], request.form.get('fldPassword'))
    if checked:
        user = MyUser(result[0]['id'],result[0]['email'],result[0]['password'])
        login_user(user)
        flash('Login Success')
        return redirect("/", code=302)
    flash('Either the password you entered is wrong or there is no account with that email please try again.')
    return render_template('login.html', title='Patient Login')

@login_manager.user_loader
def loadUser(user_id):
    if user_id is not None:
        cursor = mysql.get_db().cursor()
        cursor.execute('SELECT * FROM users WHERE id=%s', user_id)
        result = cursor.fetchall()
        if len(result) != 0:
            user = MyUser(result[0]['id'], result[0]['email'], result[0]['password'])
            return user
        else:
            return None
    return None

@login_manager.unauthorized_handler
def please_login():
    flash("Please login before continuing.")
    return redirect("/patients/login", code=302)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout Successful")
    return redirect("/", code=302)

#API Section:
@app.route('/api/v1/heightWeight', methods=['GET'])
def browseHeightsAndWeights() -> str:
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tableHeightWeight')
    result = cursor.fetchall()
    js = json.dumps(result)
    resp = Response(js, status=200, mimetype='application/json')
    return resp

@app.route('/api/v1/heightWeight/<int:patient_id>', methods=['GET'])
def retrieve(patient_id) -> str:
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tableHeightWeight WHERE id = %s', patient_id)
    result = cursor.fetchall()
    js = json.dumps(result)
    resp = Response(js, status=200, mimetype='application/json')
    return resp

@app.route('/api/v1/heightWeight', methods=['POST'])
def add() -> str:
    content = request.json
    cursor = mysql.get_db().cursor()
    patientData = (content['fldIndex'], content['fldHeight_Inches'], content['fldWeight_Pounds'])
    new_patient_query = """INSERT into tableHeightWeight (fldIndex,fldHeight_Inches,fldWeight_Pounds) VALUES (%s, %s,%s)"""
    cursor.execute(new_patient_query, patientData)
    mysql.get_db().commit()
    resp = Response(status=201, mimetype='application/json')
    return resp

@app.route('/api/v1/heightWeight/<int:patient_id>', methods=['PUT'])
def edit(patient_id) -> str:
    content = request.json
    cursor = mysql.get_db().cursor()
    patientData = (content['fldIndex'], content['fldHeight_Inches'], content['fldWeight_Pounds'], patient_id)
    update_patient_query = """UPDATE tableHeightWeight hw SET hw.fldIndex = %s, hw.fldHeight_Inches = %s, hw.fldWeight_Pounds = %s  WHERE hw.id = %s """
    cursor.execute(update_patient_query, patientData)
    mysql.get_db().commit()
    resp = Response(status=200, mimetype='application/json')
    return resp

@app.route('/api/v1/heightWeight/<int:patient_id>', methods=['DELETE'])
def delete(patient_id) -> str:
    cursor = mysql.get_db().cursor()
    delete_patient_query = """DELETE FROM tableHeightWeight WHERE id = %s """
    cursor.execute(delete_patient_query, patient_id)
    mysql.get_db().commit()
    resp = Response(status=200, mimetype='application/json')
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0')
