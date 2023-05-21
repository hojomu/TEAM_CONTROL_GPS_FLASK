from flask import Blueprint, render_template

moveController = Blueprint('moveController',__name__)

# 홈에서 html로 이동하기 위한 controller
@moveController.route('/Geolocation')
def Geolocation():
    return render_template('Geolocation.html')

@moveController.route('/locationManagement')
def locationManagement():
    return render_template('locationManagement.html')

@moveController.route('/member')
def member():
    return render_template('member.html')

@moveController.route('/a')
def a():
    return render_template('a.html')
# 이동용 Controller 끝
