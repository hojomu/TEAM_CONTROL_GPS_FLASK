import json
from flask import Blueprint
from flask_mysqldb import MySQL

MedicalMemberController = Blueprint('MedicalMemberController',__name__)

mysql = MySQL()

# 병원의 환자 정보 불러오기
@MedicalMemberController.route('/getPatientsData/<hospital>')
def get_patients_data(hospital):
    cur = mysql.connection.cursor()
    cur.execute("""select * from register where hospital = %s""", (hospital,))
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