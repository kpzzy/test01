from flask import Flask, render_template, request, jsonify,redirect, url_for
import requests
import datetime
import certifi

ca = certifi.where()

app = Flask(__name__)

# pymongo
from pymongo import MongoClient


client = MongoClient('mongodb+srv://test:sparta@cluster0.lpapihe.mongodb.net/?retryWrites=true&w=majority', tlsCAFile=ca)
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
f = []
# 영화 크롤링
for movie in movies:
    a = movie.select_one('div.thumb_cont > strong > a')
    if a is not None:
        f.append(a)
        title = a.text
        rank = movie.select_one('div > div.thumb_item > div.poster_movie > span.rank_num').text
        grade = movie.select_one('div.thumb_cont > span.txt_append > span:nth-child(1) > span').text
        rate = movie.select_one('div.thumb_cont > span.txt_append > span:nth-child(2) > span').text
        date = movie.select_one('div.thumb_cont > span.txt_info > span').text
        img = movie.select_one('div.thumb_item > div.poster_movie > img')['src']
        count = len(f)
        doc = {
            'rank': rank,
            'title': title,
            'rate': rate,
            'date': date,
            'img': img,
            'grade': grade,
            'num': count
        }
        db.movies.insert_one(doc)


# 디테일 크롤링
sub = 'https://movie.daum.net/ranking/reservation'
data2 = requests.get(sub, headers=headers)

soup2 = BeautifulSoup(data2.text, 'html.parser')

infos = soup2.select('#mainContent > div > div.box_ranking > ol > li > div')
#mainContent > div > div.box_boxoffice > ol > li:nth-child(1) > div > div.thumb_cont > strong > a

d = []

for info in infos:
    b = info.select_one('div > div.thumb_cont > strong > a')
    comments = b['href']
    details = (sub[0:22]+comments)
    data3 = requests.get(details, headers=headers)
    soup3 = BeautifulSoup(data3.text, 'html.parser')
    infos2 = soup3.select('#mainContent > div > div.box_basic > div.info_detail')
    for info2 in infos2:
        d.append(info2)
        detail_title = info2.select_one('div.detail_tit > h3 > span').text
        og_title = info2.select_one(' div.detail_tit > div.head_origin > span').text
        de_date = info2.select_one('div.detail_cont > div > dl > dd').text
        genre = info2.select_one('div.detail_cont > div:nth-child(1) > dl:nth-child(2) > dd').text
        time = info2.select_one('div.detail_cont > div:nth-child(1) > dl:nth-child(5) > dd').text
        audience = info2.select_one('div.detail_cont > div:nth-child(2) > dl:nth-child(2) > dd').text
        de_star = info2.select_one('div.detail_cont > div:nth-child(2) > dl:nth-child(1) > dd').text
        count = len(d)
        doc2 = {
            'detail_title': detail_title,
            'og_title': og_title,
            'de_date': de_date,
            'genre': genre,
            'time': time,
            'audience': audience,
            'de_star': de_star,
            'num': count
        }
        db.movies_detail.insert_one(doc2)



# 메인페이지
@app.route('/')
def home():
    token_receive = request.cookies.get('token')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.login.find_one({'id':payload['id']})
        return render_template('index.html', id=user_info['id'])
    except jwt.ExpiredSignatureError:
        return redirect(url_for('login', msg='타임오버'))
    except jwt.exceptions.DecodeError:
        return redirect(url_for('login', msg='틀림'))

# 메인페이지 크롤링
@app.route("/movies", methods=["GET"])
def movies_get():
    movie_list = list(db.movies.find({},{'_id':False}).limit(20))
    return jsonify({'orders': movie_list})


# 회원가입화면
@app.route('/signup')
def singup():
    return render_template('signup.html')


# 로그인화면
@app.route('/login')
def login():
    return render_template('login.html')


#디테일 화면
@app.route('/landing', methods=["get"])
def landing():
    return render_template('landing.html')

#디테일 정보 불러오기
# @app.route('/detail_info_num', methods=["GET"])
# def get_details():
#     detail_list = list(db.movies_detail.find({},{'_id':False}).limit(20))
#     user = db.users.find_one({'name': 'bobby'})
#     return jsonify({'details': detail_list})


@app.route('/detail_info', methods=["GET"])
def get_details():

    detail_list = list(db.movies_detail.find({}, {'_id': False}))

    return jsonify({'details': detail_list})

# @app.route('/detail_info2', methods=["GET"])
# num_receive = requests.form['num_give']
# db.movies_detail2.insert_one(detail_list)
# detail_list = list(db.movies_detail.find({}, {'_id': False}).limit(20))


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
            'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=300)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'msg' : '저장완료', 'token':token})
    else:
        return jsonify({'msg' : '틀림'})





if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)