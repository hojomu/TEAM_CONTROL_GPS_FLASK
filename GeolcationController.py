from flask import Blueprint, request
from flask_mysqldb import MySQL

GeolcationController = Blueprint('GeolcationController',__name__)

mysql = MySQL()

# 환자의 위치 정보 저장하기
@GeolcationController.route('/Geolocation', methods=['POST'])
def save_location():
    if request.method == 'POST':
        # post 방식을 이용하면 데이터가 본문(body)에 포함되기 때문에 request로 접근할 수 있다.
        name = request.form['name']
        phone = request.form['phone']
        x = request.form['x']
        y = request.form['y']

        cur = mysql.connection.cursor()
        cur.execute("""INSERT INTO locationdata (x, y, phone, getTime, name) 
                    VALUES (%s, %s, %s, now(), %s)""",
                    (x, y, phone, name))
        mysql.connection.commit()
        cur.close()

        return 'Location data saved successfully'

    return 'Invalid request'

