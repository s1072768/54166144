import requests, json
from bs4 import BeautifulSoup

from flask import Flask, render_template, request, make_response, jsonify, abort
from datetime import datetime, timezone, timedelta

import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()+

from linebot import(
    LineBotApi, WebhookHandler
)

from linebot.exceptions import(
    InvalidSignatureError
)
from linebot.models import(
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
)

line_bot_api = LineBotApi("")
handler = WebhookHandler("")
app = Flask(__name__)

@app.route("/callback", methods=["POST"]) 
def callback():
    signature = request.headers["X-Line-Signature"]

    body = request.get_data(as_text=True)
    app.logger.info("Request body"+body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message.text
    if(message[:8].upper == "Mcdonald"):
        res = searchMenu(message[9:])
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = res))
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text = "您輸入：" + event.message.text)
        )
def searchMenu(keyword):
    info = "您要查詢餐點，關鍵字為：" + keyword +"\n"
    collection_ref = db.collection("Mcdonald")
    docs = collection_ref.order_by("name").get()
    found = False
    for doc in docs:
        if keyword in doc.to_dict()["name"]:
            found = True
            info = ""
            info = ""
            info = ""
            
    if not found:
        info = "沒有這東東，你要不要看看自己在寫甚麼？"
    return info

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json(force=True)
    action =  req.get("queryResult").get("action")

    if (action == "Mac_menu"):
        cond = req.get("queryResult").get("action").get("mac_menu")
        info = ""
        result = jsonify({
            "fulfillmentText":info,
            "fulfillmentMessage":[
                ("image":
                 {
                     "imageUrl": ""
                 })
            ]
        })
        
    elif(action == "category"):
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
    