import requests
import xml.etree.ElementTree as ET
import mysql.connector

# MySQL 연결 정보
MYSQL_HOST = '192.168.30.13'
MYSQL_PORT = 3306
MYSQL_USER = 'jht0725'
MYSQL_PASSWORD = '1234'
MYSQL_DB = 'mydb'

# API 호출 및 데이터 수신
url = 'https://apis.data.go.kr/B551182/hospInfoServicev2/getHospBasisList'
service_key = 'h2ypgTwYrtNcvQ3ZsS%2B5Nz0kFSgTSkQWd1FXJYNRncmkSaVyPtpiFz5R3qxWUQwBIWuAdRKDI2his%2FECaRPniA%3D%3D'

params = {
    'ServiceKey': service_key,
    'numOfRows': 1,
    'pageNO':1 
}

total_data = []
response = requests.get(url, params=params)

    # XML 형식의 응답을 파싱하여 데이터 추출
root = ET.fromstring(response.content)
items = root.findall('.//item')

for item in items:
    # 필요한 데이터 추출
    hospital_name = item.findtext('yadmNm')
    sido_cd_nm = item.findtext('sidoCdNm')
    telno = item.findtext('telno')
    x = float(item.findtext('XPos'))
    y = float(item.findtext('YPos'))
    address = item.findtext('addr')

    total_data.append({'hospital_name': hospital_name, 'sido_cd_nm': sido_cd_nm, 'telno': telno, 'x': x, 'y': y, 'address': address})


print(total_data)

# MySQL에 데이터 저장
conn = mysql.connector.connect(
    host=MYSQL_HOST,
    port=MYSQL_PORT,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DB
)

cursor = conn.cursor()

for data in total_data:
    hospital_name = data['hospital_name']
    sido_cd_nm = data['sido_cd_nm']
    telno = data['telno']
    x = data['x']
    y = data['y']
    address = data['address']

    # INSERT 쿼리 실행
    query = "INSERT INTO hospital (hospitalName, sidoCdNm, telno, X, y, addr) VALUES (%s, %s, %s, %s, %s, %s)"
    values = (hospital_name, sido_cd_nm, telno, x, y, address)
    cursor.execute(query, values)

conn.commit()
conn.close()