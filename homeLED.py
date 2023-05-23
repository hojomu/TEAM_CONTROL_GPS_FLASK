import RPi.GPIO as GPIO
import bluepy.btle as btle
from flask import Flask, render_template, request, jsonify
from flask_sse import sse
import threading  # threading 모듈 추가

app = Flask(__name__)
app.config["REDIS_URL"] = "redis://localhost"  # Redis 서버 설정 (필요한 경우 수정)
app.register_blueprint(sse, url_prefix="/stream")  # SSE 블루프린트 등록

beacon_mac_address = "E4:5F:01:C0:F1:4D"

class BeaconConnectionDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)
        self.connected = False

    def handleNotification(self, cHandle, data):
        if cHandle == 0x04:  # 연결 상태 핸들을 나타내는 핸들값
            if data[0] == b'\x01':
                self.connected = True
                GPIO.output(23, GPIO.HIGH)  # RED LED 켜기
                notify_webpage(True)  # 웹 페이지에 알림 보내기
            else:
                self.connected = False
                GPIO.output(23, GPIO.LOW)  # RED LED 끄기
                notify_webpage(False)  # 웹 페이지에 알림 보내기

def notify_webpage(connected):
    # 웹 페이지에 알림을 보내는 로직을 구현해야 합니다.
    # 예를 들어, WebSocket 또는 SSE(Server-Sent Events)를 사용하여 실시간으로 알림을 보낼 수 있습니다.
    # 해당 방법에 대한 코드는 종속적인 라이브러리와 기술에 따라 달라지므로 자세한 구현 방법은 알려주셔야 합니다.
    # 웹 페이지에 알림을 보내기 위해 사용할 수 있는 옵션으로 Flask-SocketIO, Flask-SSE, Flask-SSE2 등이 있습니다.
    # 이를 활용하여 웹 페이지에 알림을 전달하는 코드를 추가해주셔야 합니다.
    # 웹 페이지에 전달할 데이터는 연결 상태(connected)에 따라 다르게 전달할 수 있습니다.
    pass

def check_beacon_connection():
    try:
        # 비콘 연결
        beacon = btle.Peripheral(beacon_mac_address)
        beacon.setDelegate(BeaconConnectionDelegate())

        # 연결 상태 확인
        while True:
            if not beacon.waitForNotifications(1.0):
                break

        # 비콘 연결 종료
        beacon.disconnect()

    except btle.BTLEException as e:
        print("비콘 연결 중 오류가 발생했습니다:", str(e))

# 불필요한 warning 제거, GPIO핀의 번호 모드 설정
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# pins란 딕셔너리를 만들고 GPIO 22, 23, 24 핀을 저장합니다.
pins = {
    23: {'name': 'RED LED', 'state': GPIO.LOW},
    24: {'name': 'Yellow LED', 'state': GPIO.LOW},
    25: {'name': 'Green LED', 'state': GPIO.LOW}
}

# pins 내에 있는 모든 핀들을 출력으로 설정하고 초기 LED OFF 설정
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

# 웹서버의 URL 주소로 접근하면 아래의 main() 함수를 실행
@app.route("/")
def main():
    # pins 내에 있는 모든 핀의 현재 핀 상태(ON/OFF)를 업데이트
    for pin in pins:
        pins[pin]['state'] = GPIO.input(pin)

    # templateData 에 저장
    templateData = {
        'pins': pins
    }

    # 업데이트 된 templateDate 값들을 homeLED.html로 리턴
    return render_template('homeLED.html', **templateData)

# URL 주소 끝에 “/핀번호/<action>”을 붙여서 접근시에 action 값에 따라 동작
@app.route("/<changePin>/<action>")
def action(changePin, action):
    # 현재 핀번호를 URL 주소로 받은 핀번호로 설정
    changePin = int(changePin)

    # 핀번호에 설정된 이름값을 불러옴
    deviceName = pins[changePin]['name']

    # action 값이 ‘on’일때
    if action == "on":
        GPIO.output(changePin, GPIO.HIGH)
        pins[changePin]['state'] = GPIO.HIGH

    # action 값이 ‘off’일때
    if action == "off":
        GPIO.output(changePin, GPIO.LOW)
        pins[changePin]['state'] = GPIO.LOW

    # 핀들의 값들을 업데이트 해서 templateData에 저장
    templateData = {
        'pins': pins
    }

    # 업데이트 된 templateDate 값들을 homeLED.html로 리턴
    return render_template('homeLED.html', **templateData)

@app.route("/notify/<connected>")
def notify(connected):
    message = "모바일 기기와 연결되었습니다." if connected == True else "모바일 기기와의 연결이 끊어졌습니다."
    sse.publish({"message": message}, type="notification")
    return "OK"

if __name__ == "__main__":
    # 비콘 연결 확인을 위한 스레드 시작
    beacon_thread = threading.Thread(target=check_beacon_connection)
    beacon_thread.daemon = True
    beacon_thread.start()

    app.run(host='192.168.204.222', port=5001, debug=False)
import RPi.GPIO as GPIO
import bluepy.btle as btle
from flask import Flask, render_template, request, jsonify
from flask_sse import sse
import threading  # threading 모듈 추가

app = Flask(__name__)
app.config["REDIS_URL"] = "redis://localhost"  # Redis 서버 설정 (필요한 경우 수정)
app.register_blueprint(sse, url_prefix="/stream")  # SSE 블루프린트 등록

beacon_mac_address = "E4:5F:01:C0:F1:4D"

class BeaconConnectionDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)
        self.connected = False

    def handleNotification(self, cHandle, data):
        if cHandle == 0x04:  # 연결 상태 핸들을 나타내는 핸들값
            if data[0] == b'\x01':
                self.connected = True
                GPIO.output(23, GPIO.HIGH)  # RED LED 켜기
                notify_webpage(True)  # 웹 페이지에 알림 보내기
            else:
                self.connected = False
                GPIO.output(23, GPIO.LOW)  # RED LED 끄기
                notify_webpage(False)  # 웹 페이지에 알림 보내기

def notify_webpage(connected):
    # 웹 페이지에 알림을 보내는 로직을 구현해야 합니다.
    # 예를 들어, WebSocket 또는 SSE(Server-Sent Events)를 사용하여 실시간으로 알림을 보낼 수 있습니다.
    # 해당 방법에 대한 코드는 종속적인 라이브러리와 기술에 따라 달라지므로 자세한 구현 방법은 알려주셔야 합니다.
    # 웹 페이지에 알림을 보내기 위해 사용할 수 있는 옵션으로 Flask-SocketIO, Flask-SSE, Flask-SSE2 등이 있습니다.
    # 이를 활용하여 웹 페이지에 알림을 전달하는 코드를 추가해주셔야 합니다.
    # 웹 페이지에 전달할 데이터는 연결 상태(connected)에 따라 다르게 전달할 수 있습니다.
    pass

def check_beacon_connection():
    try:
        # 비콘 연결
        beacon = btle.Peripheral(beacon_mac_address)
        beacon.setDelegate(BeaconConnectionDelegate())

        # 연결 상태 확인
        while True:
            if not beacon.waitForNotifications(1.0):
                break

        # 비콘 연결 종료
        beacon.disconnect()

    except btle.BTLEException as e:
        print("비콘 연결 중 오류가 발생했습니다:", str(e))

# 불필요한 warning 제거, GPIO핀의 번호 모드 설정
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# pins란 딕셔너리를 만들고 GPIO 22, 23, 24 핀을 저장합니다.
pins = {
    23: {'name': 'RED LED', 'state': GPIO.LOW},
    24: {'name': 'Yellow LED', 'state': GPIO.LOW},
    25: {'name': 'Green LED', 'state': GPIO.LOW}
}

# pins 내에 있는 모든 핀들을 출력으로 설정하고 초기 LED OFF 설정
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

# 웹서버의 URL 주소로 접근하면 아래의 main() 함수를 실행
@app.route("/")
def main():
    # pins 내에 있는 모든 핀의 현재 핀 상태(ON/OFF)를 업데이트
    for pin in pins:
        pins[pin]['state'] = GPIO.input(pin)

    # templateData 에 저장
    templateData = {
        'pins': pins
    }

    # 업데이트 된 templateDate 값들을 homeLED.html로 리턴
    return render_template('homeLED.html', **templateData)

# URL 주소 끝에 “/핀번호/<action>”을 붙여서 접근시에 action 값에 따라 동작
@app.route("/<changePin>/<action>")
def action(changePin, action):
    # 현재 핀번호를 URL 주소로 받은 핀번호로 설정
    changePin = int(changePin)

    # 핀번호에 설정된 이름값을 불러옴
    deviceName = pins[changePin]['name']

    # action 값이 ‘on’일때
    if action == "on":
        GPIO.output(changePin, GPIO.HIGH)
        pins[changePin]['state'] = GPIO.HIGH

    # action 값이 ‘off’일때
    if action == "off":
        GPIO.output(changePin, GPIO.LOW)
        pins[changePin]['state'] = GPIO.LOW

    # 핀들의 값들을 업데이트 해서 templateData에 저장
    templateData = {
        'pins': pins
    }

    # 업데이트 된 templateDate 값들을 homeLED.html로 리턴
    return render_template('homeLED.html', **templateData)

@app.route("/notify/<connected>")
def notify(connected):
    message = "모바일 기기와 연결되었습니다." if connected == True else "모바일 기기와의 연결이 끊어졌습니다."
    sse.publish({"message": message}, type="notification")
    return "OK"

if __name__ == "__main__":
    # 비콘 연결 확인을 위한 스레드 시작
    beacon_thread = threading.Thread(target=check_beacon_connection)
    beacon_thread.daemon = True
    beacon_thread.start()

    app.run(host='192.168.204.222', port=5001, debug=False)
