import json
from flask import Blueprint, render_template, request
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
            'phone': row[0],
            'name': row[1],
            'hospital': row[9]
        }
        patients.append(patient)
    
    return json.dumps(patients)

# 병원 환자 정보 INSERT
@MedicalMemberController.route('/member', methods=['POST'])
def insert_member():
    if request.method == 'POST':
        phone = request.form['phone']
        name = request.form['name']
        personalNumber = request.form['personalNumber']     
        disease = request.form['disease']
        address = request.form['address']
        guardianName = request.form['guardianName']
        guardianPhone = request.form['guardianPhone']
        raspberry = request.form['raspberry']    
        hospital = request.form['hospital']
        # 여기에서 필요한 데이터를 받아온 후 MySQL 데이터베이스에 삽입하는 쿼리를 실행합니다.
        cur = mysql.connection.cursor()
        cur.execute("""INSERT INTO register 
          (phone,name,personalNumber,inrollTime,disease,address,guardianName,guardianPhone,raspberry,hospital)
          VALUES (%s, %s, %s, now(), %s, %s, %s, %s, %s, %s)""", 
          (phone,name,personalNumber,disease,address,guardianName,guardianPhone,raspberry,hospital))
        mysql.connection.commit()
        cur.close()
        return 'member data saved successfully'
    return render_template('member.html')