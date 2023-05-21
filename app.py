from flask import Flask, render_template
from flask_mysqldb import MySQL
from GeolcationController import GeolcationController
from MedicalMemberController import MedicalMemberController
from LocationDataController import LocationDataController
from moveController import moveController

app = Flask(__name__)

# MySQL 연결 설정
app.config['MYSQL_HOST'] = 'localhost'  # MySQL 호스트 주소
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'root'  # MySQL 사용자명
app.config['MYSQL_PASSWORD'] = '0000'  # MySQL 비밀번호
app.config['MYSQL_DB'] = 'control_second_project'  # 사용할 데이터베이스명

# MySQL 초기화
mysql = MySQL(app)

# DB 연결 블루 프린트 ( CONTROLLER )
app.register_blueprint(GeolcationController)
app.register_blueprint(MedicalMemberController)
app.register_blueprint(LocationDataController)

# 이동용 블루 프린트 ( 삭제 예정 )
app.register_blueprint(moveController)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()



# db insert 예제 ( 삭제 예정 )
# @app.route('/insert', methods=['POST'])
# def insert_data():
#     if request.method == 'POST':
#         name = request.form['name']
#         # 여기에서 필요한 데이터를 받아온 후 MySQL 데이터베이스에 삽입하는 쿼리를 실행합니다.
#         cur = mysql.connection.cursor()
#         cur.execute("INSERT INTO register (name) VALUES (%s)", (name,))
#         mysql.connection.commit()
#         cur.close()
#         return 'Data inserted successfully'
#     return render_template('insert.html')