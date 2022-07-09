from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import datetime

app = Flask(__name__)

# pymongo
from pymongo import MongoClient

client = MongoClient('mongodb+srv://test:sparta@cluster0.lpapihe.mongodb.net/?retryWrites=true&w=majority')
db = client.dbsparta

# bs4
from bs4 import BeautifulSoup

headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get('https://movie.daum.net/ranking/reservation', headers=headers)

soup = BeautifulSoup(data.text, 'html.parser')

movies = soup.select('#mainContent > div > div.box_ranking > ol > li > div')


# 잡거
import hashlib
import jwt





SECRET_KEY = 'FREE'

# 영화 크롤링
for movie in movies:
    a = movie.select_one('div.thumb_cont > strong > a')


    if a is not None:
        title = a.text
        rank = movie.select_one('div > div.thumb_item > div.poster_movie > span.rank_num').text
        grade = movie.select_one('div.thumb_cont > span.txt_append > span:nth-child(1) > span').text
        rate = movie.select_one('div.thumb_cont > span.txt_append > span:nth-child(2) > span').text
        date = movie.select_one('div.thumb_cont > span.txt_info > span').text
        img = movie.select_one('div.thumb_item > div.poster_movie > img')['src']

        doc = {
            'rank': rank,
            'title': title,
            'rate': rate,
            'date': date,
            'img': img,
            'grade': grade
        }



        db.movies.insert_one(doc)






# 메인페이지
@app.route('/')
def home():
    token_receive = request.cookies.get('token')


    try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            user_info = db.login.find_one({'id':payload['id']})
            return render_template('index.html' , id=user_info['id'])
    except jwt.ExpiredSignatureError:
            return redirect(url_for('copy', msg='타임오버'))
    except jwt.exceptions.DecodeError:
            return redirect(url_for('copy', msg='틀림'))



# 이거 붙여넣엇음
@app.route("/movies", methods=["GET"])
def movies_get():
    movie_list = list(db.movies.find({},{'_id':False}).limit(20))
    return jsonify({'orders': movie_list})


# 회원가입화면
@app.route('/signup')
def singup():
    return render_template('signup.html')
# 0709 카피페이지
@app.route('/copy')
def copy():
    return render_template('copy.html')


# 로그인화면
@app.route('/login')
def login():
    return render_template('login.html')

# 디테일페이지
@app.route('/detailpage')
def detail():
    token_receive = request.cookies.get('token')

    if token_receive is not None:
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            user_info = db.login.find_one({'id': payload['id']})
            return render_template('landing.html', id=user_info['id'])
        except jwt.ExpiredSignatureError:
            return redirect(url_for('login', msg='타임오버'))
        except jwt.exceptions.DecodeError:
            return redirect(url_for('login', msg='틀림'))



# 코멘트 저장
@app.route("/Detail", methods=["POST"])
def comment_post():
    comment_receive = request.form['comment_give']


    doc = {'comment':comment_receive}
    db.comment.insert_one(doc)
    
    return jsonify({'msg':'저장완료'})

# 코멘트 불러오기
@app.route("/Detail", methods=["GET"])
def comment_get():
    comment_list = list(db.comment.find({}, {'_id': False}))
    return jsonify({'comment': comment_list})


# 여기는 아이디와 pw저장 api
@app.route("/api/signup", methods=["POST"])
def api_signup():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()


    doc = {'id': id_receive, 'pw': pw_hash}
    db.login.insert_one(doc)

    return jsonify({'msg': '저장완료'})

# 저장된 정보로 로그인하기
@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    result = db.login.find_one({'id':id_receive, 'pw':pw_hash})

    if result is not None:
        payload = {
            'id' : id_receive,
            'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=300)
        }
        # 타임도 조정해주기 ㅇㅇ
        # ec2로 올릴때 이거 붙이기 .decode('utf-8')
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'msg' : '저장완료', 'token':token})
    else:
        return jsonify({'msg' : '틀림'})





if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)