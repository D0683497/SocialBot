from flask import Flask, escape, request, make_response, jsonify,  render_template
from flask_sqlalchemy import SQLAlchemy
import json

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'SECRET_KEY'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

class Vocabulary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.Integer)
    main_category = db.Column(db.String(80))
    sub_category = db.Column(db.String(80))
    chinese = db.Column(db.String(250))
    english = db.Column(db.String(250))

    def __repr__(self):
        return '<Vocabulary %r>' % self.chinese

def get_all_vocabulary():
    print('------------開始查詢------------')
    url = 'http://www.fcu.edu.tw/wSite/lp?ctNode=16185&mp=1'
    r = requests.get(url)
    soup = BeautifulSoup(r.text,"html.parser")
    pagesize = soup.find("section",{'class':'page'}).find('span').find('em').text

    url = 'http://www.fcu.edu.tw/wSite/lp?ctNode=16185&mp=1&idPath=&nowPage=1&pagesize=' + pagesize

    r = requests.get(url)
    soup = BeautifulSoup(r.text,"html.parser")

    table = soup.find("table",{'class':'tb'})

    for row in table.find_all("tr")[1:]:
        fields =  row.find_all("td")
        vocabulary = Vocabulary(serial_number=fields[0].text.strip(), main_category=fields[1].text.strip(), sub_category=fields[2].text.strip(), chinese=fields[3].text.strip(), english=fields[4].text.strip())
        db.session.add(vocabulary)
        db.session.commit()
    print('------------查詢結束------------')

def get_keyword_vocabulary(keyword):
    result = Vocabulary.query.filter(Vocabulary.chinese.contains(keyword)).all()
    msg = ''
    if result:
        for i in result:
            msg += "「" + i.chinese + '」 的英文是 「' + i.english + '」\n'
    else:
        msg += "查無 「" + keyword + "」 的英文"
    return msg

@app.route("/", methods=['GET'])
def index():
    return  render_template('index.html')

@app.route("/update", methods=['GET'])
def update():
    get_all_vocabulary()
    return "Success!"

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    print(req)

    if req['queryResult']['parameters']['any'] != '':
        keyword = req['queryResult']['parameters']['any']
        print(keyword)
    
    res_message = {"fulfillmentText": get_keyword_vocabulary(keyword)}
    print(res_message)
    
    return make_response(jsonify(res_message))

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=5000)