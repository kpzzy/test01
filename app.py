from flask import Flask, render_template, request, jsonify
import datetime

app = Flask(__name__)

from pymongo import MongoClient

client = MongoClient('mongodb+srv://test:sparta@cluster0.lpapihe.mongodb.net/?retryWrites=true&w=majority')
db = client.dbsparta

import hashlib
import jwt
import bcrypt

SECRET_KEY = 'FREE'



# 메인페이지
@app.route('/')
def home():
    return render_template('repeat1.html')
# 회원가입화면
@app.route('/signup')
def singup():
    return render_template('signup.html')
# 로그인화면
@app.route('/login')
def login():
    return render_template('login.html')

# 여기는 아이디와 pw저장 api
@app.route("/api/signup", methods=["POST"])
def api_signup():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()


    doc = {'id': id_receive, 'pw': pw_hash}
    db.login.insert_one(doc)

    return jsonify({'msg': '저장완료'})

# 저장된 정보로 로그인하기 이거 왜안돼 씨발
@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    result = db.login.find_one({'id':id_receive, 'pw':pw_hash})

    if result is not None:
        payload = {
            'id' : id_receive,
            'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=10)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'msg' : '저장완료', 'token':token})
    else:
        return jsonify({'msg' : '틀림'})





if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)