import requests, json
from bs4 import BeautifulSoup

from flask import Flask, render_template, request, make_response, jsonify, abort
from datetime import datetime, timezone, timedelta

import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)
@app.route("/")
def index():
     homepage = "<h1>mcdonald</h1>"
     homepage += "<a href=/webhook>webhook</a><br>"
     return homepage

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json(force=True)
    action =  req.get("queryResult").get("action")
        
    if(action == "category"):
        cond = req.get("queryResult").get("action").get("category")
        info = "這裡是關於" + cond + "的全部料理" +"\n\n"
        collection_ref = db.collection("mcdonald")
        docs = collection_ref.get()
        found = False
        for doc in docs:
            if cond in doc.to_dict()["category"]:
                found = True
                info += doc.to_dict()["name"] + "\n"
        if not found:
            info = "沒有這東東，你要不要看看自己在寫甚麼？"
        result = jsonify({"fulfillmentText":info})
        
    elif(action == "order"):
        cond = req.get("queryResult").get("action").get("any") 
        info = ""
        collection_ref = db.collection("mcdonald")
        docs = collection_ref.get()
        found = False
        for doc in docs:
                if cond in doc.to_dict()["name"]:
                    found = True
                    info += "一份" + cond + "。請問您還需要什麼來增加自己的體脂？"
        if not found:
                info = "沒有這東東，你要不要看看自己在寫甚麼？"
        result = jsonify({"fulfillmentText":info})

    elif(action == "information"):
        cond = req.get("queryResult").get("action").get("") 
        info = ""
        collection_ref = db.collection("mcdonald")
        docs = collection_ref.get()
        found = False
        for doc in docs:
                if cond in doc.to_dict()["name"]:
                    found = True
                    info += "這些是" + cond + "的資訊。放心，我們不會放上卡洛里的。\n\n"
                    info += "類別：" + doc.to_dict["category"] + "\n"
                    info += "名稱：" + doc.to_dict["name"] + "\n"
                    info += "價格：" + doc.to_dict["price"] + "\n"       
        if not found:
                info = "沒有這東東，您要不要看看自己在寫甚麼？"
        result = jsonify({"fulfillmentText":info})
    