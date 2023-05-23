from flask import Flask, render_template
from flask_mysqldb import MySQL
from GeolcationController import GeolcationController
from MedicalMemberController import MedicalMemberController
from LocationDataController import LocationDataController
import config

app = Flask(__name__)
# config 객체 생성
app.config.from_object(config)

# MySQL 연결 설정
app.config['MYSQL_HOST'] = config.MYSQL_HOST  # MySQL 호스트 주소
app.config['MYSQL_PORT'] = config.MYSQL_PORT
app.config['MYSQL_USER'] = config.MYSQL_USER  # MySQL 사용자명
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD  # MySQL 비밀번호
app.config['MYSQL_DB'] = config.MYSQL_DB  # 사용할 데이터베이스명


# MySQL 초기화
mysql = MySQL(app)


# DB 연결 블루 프린트 ( CONTROLLER )
app.register_blueprint(GeolcationController)
app.register_blueprint(MedicalMemberController)
app.register_blueprint(LocationDataController)
app.register_blueprint(HomeLEDController)

@app.route('/')
def index():
    return render_template('index.html')


# 이동용 route
@app.route('/Geolocation')
def Geolocation():
    return render_template('Geolocation.html')

@app.route('/locationManagement')
def locationManagement():
    KAKAOMAP_API_KEY = app.config['KAKAOMAP_API_KEY']
    return render_template('locationManagement.html', KAKAOMAP_API_KEY = KAKAOMAP_API_KEY)

@app.route('/member')
def member():
    return render_template('member.html')

@app.route('/a')
def a():
    KAKAOMAP_API_KEY = app.config['KAKAOMAP_API_KEY']
    return render_template('a.html', KAKAOMAP_API_KEY = KAKAOMAP_API_KEY)

@app.route('/homeLED')
def homeLED():
    return render_template('homeLED.html')
# 이동용 route 끝


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