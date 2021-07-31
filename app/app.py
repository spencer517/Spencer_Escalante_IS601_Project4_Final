from typing import List, Dict
import simplejson as json
from flask import Flask, request, Response, redirect
from flask import render_template
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor

app = Flask(__name__)
mysql = MySQL(cursorclass=DictCursor)


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
def get_edit(patient_id):
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tableHeightWeight WHERE id=%s', patient_id)
    result = cursor.fetchall()
    return render_template('edit.html', title='Home', patient=result[0])

@app.route('/edit/<int:patient_id>', methods=['POST'])
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
def new_patient_insert():
    cursor = mysql.get_db().cursor()
    data = (request.form.get('fldIndex'), request.form.get('fldHeight_Inches'), request.form.get('fldWeight_Pounds'))
    new_patient_query = """INSERT into tableHeightWeight (fldIndex,fldHeight_Inches,fldWeight_Pounds) VALUES (%s, %s,%s)"""
    cursor.execute(new_patient_query, data)
    mysql.get_db().commit()
    return redirect("/", code=302)

@app.route('/delete/<int:patient_id>', methods=['POST'])
def remove_patient(patient_id):
    cursor = mysql.get_db().cursor()
    delete_patient_query = """DELETE FROM tableHeightWeight WHERE id = %s """
    cursor.execute(delete_patient_query, patient_id)
    mysql.get_db().commit()
    return redirect("/", code=302)

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
