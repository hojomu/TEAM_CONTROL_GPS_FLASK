import json
from flask import Blueprint
from flask_mysqldb import MySQL

LocationDataController = Blueprint('LocationDataController',__name__)

mysql = MySQL()

# 병원의 환자 정보 불러오기
@LocationDataController.route('/getPatientsData/<hospital>')
def get_patients_data(hospital):
    cur = mysql.connection.cursor()
    cur.execute("select * from register where hospital = %s", (hospital,))
    data = cur.fetchall()
    cur.close()
    
    patients = []
    for row in data:
        patient = {
            'name': row[0],
            'phone': row[1]
        }
        patients.append(patient)
    
    return json.dumps(patients)


# 환자 위치 정보 불러오기
@LocationDataController.route('/getLocationData/<hospital>')
def get_location_data(hospital):
    cur = mysql.connection.cursor()
    cur.execute("""SELECT ld.* FROM locationdata ld INNER 
                JOIN ( SELECT name, phone FROM register WHERE hospital = %s GROUP BY name, phone) 
                r ON ld.name = r.name AND ld.phone = r.phone INNER 
                JOIN ( SELECT name, phone, MAX(getTime) as maxTime FROM locationdata GROUP BY name, phone ) 
                t ON ld.name = t.name AND ld.phone = t.phone AND ld.getTime = t.maxTime""", (hospital,))
    data = cur.fetchall()
    cur.close()
    
    location_data = []
    for row in data:
        location = {
            'x': row[0],
            'y': row[1],
            'name': row[2]
        }
        location_data.append(location)
    
    return json.dumps(location_data)

# 집중 관찰 환자 위치 불러오기
@LocationDataController.route('/focusToPatient/<name>/<phone>')
def get_focused_patient_location(name,phone):
    cur = mysql.connection.cursor()
    cur.execute("""SELECT * FROM locationdata 
                WHERE name = %s AND phone = %s AND getTime = ( SELECT MAX(getTime) 
                FROM locationdata WHERE name = %s AND phone = %s )""", (name,phone,name,phone,))
    data = cur.fetchall()
    cur.close()

    location_data = []
    for row in data:
        location = {
            'x': row[0],
            'y': row[1],
            'name': row[2]
        }
        location_data.append(location)

    return json.dumps(location_data)
