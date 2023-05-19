from flask import Flask, render_template, request
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = '192.168.30.13'  # MySQL 호스트 주소
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'jht0725'  # MySQL 사용자명
app.config['MYSQL_PASSWORD'] = '1234'  # MySQL 비밀번호
app.config['MYSQL_DB'] = 'mydb'  # 사용할 데이터베이스명

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/Geolocation')
def Geolocation():
    return render_template('Geolocation.html')

@app.route('/locationManagement')
def locationManagement():
    return render_template('locationManagement.html')

@app.route('/member')
def member():
    return render_template('member.html')

@app.route('/a')
def a():
    return render_template('a.html')

# db insert 예제
@app.route('/insert', methods=['POST'])
def insert_data():
    if request.method == 'POST':
        name = request.form['name']
        # 여기에서 필요한 데이터를 받아온 후 MySQL 데이터베이스에 삽입하는 쿼리를 실행합니다.
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO Bluetooth (name) VALUES (%s)", (name,))
        mysql.connection.commit()
        cur.close()
        return 'Data inserted successfully'
    return render_template('insert.html')

if __name__ == '__main__':
    app.run()

