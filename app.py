import requests

from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient('mongodb+srv://changsoon:tnsrh124!1@cluster0.ry8gyso.mongodb.net/?retryWrites=true&w=majority')
db = client.dbsparta

headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get('https://movie.daum.net/ranking/reservation', headers=headers)

soup = BeautifulSoup(data.text, 'html.parser')

app = Flask(__name__)
movies = soup.select('#mainContent > div > div.box_ranking > ol > li > div')

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

@app.route('/')
def home():
   return render_template('index.html')


@app.route("/movies", methods=["GET"])
def movies_get():
    movie_list = list(db.movies.find({},{'_id':False}))
    return jsonify({'orders': movie_list})


if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)