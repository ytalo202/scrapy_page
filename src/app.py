from flask import Flask, jsonify, request, make_response
# from sunat import ask_sunat
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import json
import argparse
from datetime import datetime, timedelta, timezone
# from werkzeug.security import safe_str_cmp
import logging
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_restful import reqparse
from functools import wraps

import pymysql

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from selenium.common.exceptions import NoSuchElementException
import os
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import chromedriver_binary  # Adds chromedriver binary to path
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from pyvirtualdisplay import Display

app = Flask(__name__)
# mysql://username:password@server/db
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/ask_sunat_db'
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://um063ag6rja9nwzn:jFzCLIyN9IEzPhjI70C@bbs3pdwzqsro6q4ufblj-mysql.services.clever-cloud.com:21004/bbs3pdwzqsro6q4ufblj'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'lolxD'
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(weeks=5215)
display = Display(visible=0, size=(1024, 768))
display.start()

jwt = JWTManager(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)


# class Task(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(70), unique=True)
#     description = db.Column(db.String(100))
#
#     def __init__(self, title, description):
#         self.title = title
#         self.description = description

@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if username != "test" or password != "test":
        return jsonify({"msg": "Bad username or password"}), 401
    access_token = create_access_token(identity=username)
    return jsonify({'access_token': access_token})


@app.route("/", methods=["GET"])
def index():
    # raise ValueError('A very specific bad thing happened.')
    # Exception("Sorry, no numbers below zero")
    return jsonify({'test': 'oks'})


class Voucher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # string_obj_voucher = db.Column(db.String(4294000000))
    # string_obj_voucher = db.Column(db.String(21845))
    string_obj_voucher = db.Column(db.String(10000))
    number = db.Column(db.Integer)
    ruc = db.Column(db.String(11))
    serie = db.Column(db.String(4))
    sun_document = db.Column(db.String(11))
    type = db.Column(db.Integer, default=0)
    reason_id = db.Column(db.Integer, default=0)

    # 0 tipo comienza la busqueda
    # 1 tipo encontrado
    # 2 no encontrado
    # 3 algun error
    # 4 procesando...

    def __init__(self, number, ruc, serie, sun_document, type):
        self.number = number
        self.ruc = ruc
        self.serie = serie
        self.sun_document = sun_document
        self.type = type


db.create_all()


# class TaskSchema(ma.Schema):
#     class Meta:
#         fields = ('id', 'title', 'description')

class VoucherSchema(ma.Schema):
    class Meta:
        fields = ('id', 'number', 'ruc', 'serie', 'sun_document', 'type', 'string_obj_voucher', 'reason_id')


voucher_schema = VoucherSchema()
vouchers_schema = VoucherSchema(many=True)


class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __str__(self):
        return "User(id='%s')" % self.id


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'password')


users = [
    User(1, username='user1', password='abcxyz'),
    User(2, username='user2', password='abcxyz')
]

user_schema = UserSchema()

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}


# task_schema = TaskSchema()
# tasks_schema = TaskSchema(many=True)

# @app.route('/tasks', methods=['POST'])
# def create_task():
#     title = request.json['title']
#     description = request.json['description']
#     new_task = Task(title, description)
#     db.session.add(new_task)
#     db.session.commit()
#     return task_schema.jsonify(new_task)
#
# @app.route('/tasks', methods=['GET'])
# def get_tasks():
#     tasks = Task.query.all()
#     # result = tasks_schema.dump(tasks)
#     # return jsonify(result)
#     return tasks_schema.jsonify(tasks)
#
# @app.route('/tasks/<id>', methods=['GET'])
# def get_task(id):
#     task = Task.query.get(id)
#     return task_schema.jsonify(task)
#
# @app.route('/tasks_title/<title>', methods=['GET'])
# def get_task_title(title):
#     # missing = Task.query.filter_by(description=title).first()
#     missing = Task.query.filter_by(description=title).first_or_404()
#     return task_schema.jsonify(missing)
#
#
# @app.route('/tasks/<id>', methods=['PUT'])
# def update_task(id):
#     task = Task.query.get(id)
#     title = request.json['title']
#     description = request.json['description']
#     task.title = title
#     task.description = description
#     db.session.commit()
#     return task_schema.jsonify(task)
#
# @app.route('/tasks/<id>', methods=['DELETE'])
# def delete_task(id):
#     task = Task.query.get(id)
#     db.session.delete(task)
#     db.session.commit()
#     return task_schema.jsonify(task)

def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity


@jwt_required
def create_dev_token():
    username = get_jwt_identity()
    expires = datetime.timedelta(days=365)
    token = create_access_token(username, expires_delta=expires)
    return jsonify({'token': token}), 201


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and safe_str_cmp(user.password.encode('utf-8'), password.encode('utf-8')):
        return user

@app.route('/validate-voucher', methods=['POST'])
@jwt_required()
def validateVoucher():
    ruc = request.json['ruc']
    serie = request.json['serie']
    number = request.json['number']
    sun_document = request.json['sun_document']

    voucher = Voucher.query.filter_by(number=number) \
        .filter_by(serie=serie) \
        .filter_by(ruc=ruc) \
        .filter_by(sun_document=sun_document) \
        .first()

    if (voucher.type == 1):
        voucher.string_obj_voucher = json.loads(voucher.string_obj_voucher)

    return voucher_schema.jsonify(voucher)

@app.route('/delete-voucher', methods=['POST'])
@jwt_required()
def endVoucher():
    ruc = request.json['ruc']
    serie = request.json['serie']
    number = request.json['number']
    sun_document = request.json['sun_document']

    voucher = Voucher.query.filter_by(number=number) \
        .filter_by(serie=serie) \
        .filter_by(ruc=ruc) \
        .filter_by(sun_document=sun_document) \
        .first()

    db.session.delete(voucher)
    db.session.commit()
    return jsonify({"result": "ok"})


@app.route('/ask-voucher', methods=['POST'])
@jwt_required()
def askVoucher():
    ruc = request.json['ruc']
    serie = request.json['serie']
    number = request.json['number']
    sun_document = request.json['sun_document']

    voucher = Voucher.query.filter_by(number=number) \
        .filter_by(serie=serie) \
        .filter_by(ruc=ruc) \
        .filter_by(sun_document=sun_document) \
        .first()

    if voucher is None:
        voucher = Voucher(number, ruc, serie, sun_document, 0)
        db.session.add(voucher)
        db.session.commit()

    sun_user = request.json['sun_user']
    sun_password = request.json['sun_password']

    # if voucher.type != 4 and voucher.type != 1:
    #     voucher.type = 4
    if voucher.type != 1:
        # voucher.type = 4
        # db.session.commit()
        # try:
        result = ask_sunat(ruc, serie, number, sun_document, sun_user, sun_password)
        if result['type'] == 1:
            stringify_data = json.dumps(result['data'], separators=(',', ':'))
            voucher.string_obj_voucher = stringify_data

        voucher.type = result['type']
        voucher.reason_id = result['reason_id']
        db.session.commit()
        # except Exception:
        #     voucher.type = 3
        #     db.session.commit()

    if (voucher.type == 1):
        voucher.string_obj_voucher = json.loads(voucher.string_obj_voucher)

    if (voucher.type == 4):
        voucher.type = 3
        db.session.commit()
        return jsonify({"result": "error", "message": "Procesando..."})

    return voucher_schema.jsonify(voucher)

@app.route('/test-voucher', methods=['GET'])
def test_sunat():
    ruc = '20501493156'
    serie = 'F005'
    number = '75298'

    sun_document = '20601732751'
    sun_user = 'WECLUB20'
    sun_password = 'iV123456789'
    return jsonify({'result':ask_sunat(ruc, serie, number, sun_document, sun_user, sun_password)})


def ask_sunat(ruc, serie, number, sun_document, sun_user, sun_password):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1280x1696')
    chrome_options.add_argument('--user-data-dir=/tmp/user-data')
    chrome_options.add_argument('--hide-scrollbars')
    chrome_options.add_argument('--enable-logging')
    chrome_options.add_argument('--log-level=0')
    chrome_options.add_argument('--v=99')
    chrome_options.add_argument('--multiple-process')
    chrome_options.add_argument('--data-path=/tmp/data-path')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--homedir=/tmp')
    chrome_options.add_argument('--disk-cache-dir=/tmp/cache-dir')
    chrome_options.add_argument(
        'user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')

    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get(
        'https://api-seguridad.sunat.gob.pe/v1/clientessol/4f3b88b3-d9d6-402a-b85d-6a0bc857746a/oauth2/loginMenuSol?originalUrl=https://e-menu.sunat.gob.pe/cl-ti-itmenu/AutenticaMenuInternet.htm&state=rO0ABXNyABFqYXZhLnV0aWwuSGFzaE1hcAUH2sHDFmDRAwACRgAKbG9hZEZhY3RvckkACXRocmVzaG9sZHhwP0AAAAAAAAx3CAAAABAAAAADdAAEZXhlY3B0AAZwYXJhbXN0AEsqJiomL2NsLXRpLWl0bWVudS9NZW51SW50ZXJuZXQuaHRtJmI2NGQyNmE4YjVhZjA5MTkyM2IyM2I2NDA3YTFjMWRiNDFlNzMzYTZ0AANleGVweA==')

    # login
    WebDriverWait(driver, 5) \
        .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                           'input#txtRuc'))) \
        .send_keys(sun_document)

    WebDriverWait(driver, 5) \
        .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                           'input#txtUsuario'))) \
        .send_keys(sun_user)

    WebDriverWait(driver, 5) \
        .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                           'input#txtContrasena'))) \
        .send_keys(sun_password)

    WebDriverWait(driver, 5) \
        .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                           'button#btnAceptar'))) \
        .click()

    # menu principal
    try:
        WebDriverWait(driver, 8) \
            .until(EC.element_to_be_clickable((By.ID,
                                               'divOpcionServicio2'))) \
            .click()
    except Exception:
        driver.close()
        return {"type": 3, "reason_id": 1}  # autentificacion

    WebDriverWait(driver, 5) \
        .until(EC.element_to_be_clickable((By.ID,
                                           'nivel1_11'))) \
        .click()

    try:
        WebDriverWait(driver, 5) \
            .until(EC.element_to_be_clickable((By.ID,
                                               'nivel2_11_9'))) \
            .click()
    except Exception:
        driver.close()
        return {"type": 3, "reason_id": 2}

    try:
        WebDriverWait(driver, 5) \
            .until(EC.element_to_be_clickable((By.ID,
                                               'nivel3_11_9_5'))) \
            .click()
    except Exception:
        driver.close()
        return {"type": 3, "reason_id": 2}

    try:
        WebDriverWait(driver, 5) \
            .until(EC.element_to_be_clickable((By.ID,
                                               'nivel4_11_9_5_1_1'))) \
            .click()
    except Exception:
        driver.close()
        return {"type": 3, "reason_id": 2}

    # formulario de busqueda de comprobante

    try:
        WebDriverWait(driver, 13) \
            .until(EC.element_to_be_clickable((By.XPATH,
                                               '//*[@id="iframeApplication"]')))
        driver.switch_to.frame(driver.find_element_by_id("iframeApplication"))
    except Exception:
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            driver.close()
        return {"type": 3, "reason_id": 3}  # problemas con lentitud de sunat

    WebDriverWait(driver, 8) \
        .until(EC.element_to_be_clickable((By.XPATH,
                                           '//*[@id="criterio.tipoConsulta"]'))) \
        .clear()

    WebDriverWait(driver, 5) \
        .until(EC.element_to_be_clickable((By.XPATH,
                                           '//*[@id="criterio.tipoConsulta"]'))) \
        .send_keys('FE Recibidas')

    WebDriverWait(driver, 5) \
        .until(EC.element_to_be_clickable((By.XPATH,
                                           '/html/body/div[1]/table/tbody/tr/td/div/div/form/table/tbody/tr/td/table/tbody/tr/td/table[4]/tbody/tr/td/table/tbody/tr[2]/td[3]/div/div/div[3]/input'))) \
        .send_keys('')

    WebDriverWait(driver, 5) \
        .until(EC.element_to_be_clickable((By.XPATH,
                                           '//*[@id="criterio.ruc"]'))) \
        .send_keys(ruc)

    WebDriverWait(driver, 5) \
        .until(EC.element_to_be_clickable((By.XPATH,
                                           '/html/body/div[1]/table/tbody/tr/td/div/div/form/table/tbody/tr/td/table/tbody/tr/td/table[4]/tbody/tr/td/table/tbody/tr[3]/td[3]/div/div/div[3]/input'))) \
        .send_keys(serie)

    WebDriverWait(driver, 5) \
        .until(EC.element_to_be_clickable((By.XPATH,
                                           '/html/body/div[1]/table/tbody/tr/td/div/div/form/table/tbody/tr/td/table/tbody/tr/td/table[4]/tbody/tr/td/table/tbody/tr[4]/td[3]/div/div/div[3]/input'))) \
        .send_keys(number)

    WebDriverWait(driver, 5) \
        .until(EC.element_to_be_clickable((By.XPATH,
                                           '//*[@id="criterio.btnContinuar"]'))) \
        .click()

    try:
        WebDriverWait(driver, 12) \
            .until(EC.element_to_be_clickable((By.XPATH,
                                               '//*[@id="recibido.facturasGrid-page-0"]/div/table/tbody/tr/td[2]/a'))) \
            .click()
    except Exception:
        driver.close()
        return {"type": 2, "reason_id": 0}  # documento no encontrado

    time.sleep(1)

    if len(driver.window_handles) == 1:
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            driver.close()
        return {"type": 3, "reason_id": 3}  # problemas con lentitud de sunat

    driver.switch_to.window(driver.window_handles[1])

    if check_exists_by_xpath(driver,
                             '/html/body/center/table/tbody/tr/td/table/tbody/tr[3]/td/table/tbody/tr[2]/td[2]'):
        date = driver.find_element_by_xpath(
            '/html/body/center/table/tbody/tr/td/table/tbody/tr[3]/td/table/tbody/tr[2]/td[2]') \
            .text.replace(' ', '').replace(':', '')
    else:
        return {"type": 3, "reason_id": 3}  # problemas con lentitud de sunat

    if check_exists_by_xpath(driver,
                             '/html/body/center/table/tbody/tr/td/table/tbody/tr[3]/td/table/tbody/tr[2]/td[5]'):
        currency = driver.find_element_by_xpath(
            '/html/body/center/table/tbody/tr/td/table/tbody/tr[3]/td/table/tbody/tr[2]/td[5]') \
            .text.replace(' ', '').replace(':', '')
    else:
        return {"type": 3, "reason_id": 3}  # problemas con lentitud de sunat

    if check_exists_by_xpath(driver, '/html/body/center/table/tbody/tr/td/table/tbody/tr[9]/td/table/tbody//tr/td'):
        lines = driver.find_elements_by_xpath(
            '/html/body/center/table/tbody/tr/td/table/tbody/tr[9]/td/table/tbody//tr/td')
    else:
        return {"type": 3, "reason_id": 3}  # problemas con lentitud de sunat

    items = []
    for i in range(0, len(lines), 8):
        if i != 0:
            items.append({
                "quantity": float(lines[i].text),
                "unit": lines[i + 1].text,
                "name": lines[i + 3].text,
                "unit_price": float(lines[i + 5].text),
            })

    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        driver.close()

    return {"type": 1, "data": {"date": date, 'currency': currency, 'items': items}, "reason_id": 0}


def check_exists_by_xpath(driver, xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            driver.close()
        return False
    return True


def check_exists_by_css_selector(driver, id):
    try:
        driver.find_elements_by_css_selector(id)
    except NoSuchElementException:
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            driver.close()
        return False
    return True


def check_exists_by_id(driver, id):
    try:
        driver.find_element_by_id(id)
    except Exception:
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            driver.close()
        return False
    return True

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4000, debug=True)
