#importing required libraries

from flask import Flask, request, render_template
import numpy as np
import pandas as pd
from sklearn import metrics 
import warnings
warnings.filterwarnings('ignore')


import json
from pandas import json_normalize

import pickle

from features import generate_features

import pickle
from sklearn.preprocessing import StandardScaler
from keras.models import load_model


import json
from flask import Flask, render_template, url_for, request, redirect, abort
import os
from flask.helpers import flash
from werkzeug.utils import secure_filename

# Ramdonforest

with open("static/model_rf.pkl", 'rb') as file:
    rf = pickle.load(file)

# One class support vector machines
# One class support vector machines
# sacle

sc = pickle.load(open('static/scale_ocsvm.pkl','rb'))

#autoencoder

# load the model from file

encoder = load_model('static/encoder.h5')


# load the model ocsvm
clf = pickle.load(open('static/model_ocsvm_ae.pkl', 'rb'))






#Blacklist
f = open('static/blacklist.json',encoding="utf8")

json_object = json.load(f)

df = json_normalize(json_object['abc']) 

df.drop(['_id', 'type', 'level', 'created'], axis=1, inplace=True)
df['url']= df['url'].apply(lambda i: i.split("//")[-1].replace('*','').rstrip("/").strip("."))

#Whitelist
f_white = open('static/whitelist.json',encoding="utf8")

json_object_white = json.load(f_white)

df_white = json_normalize(json_object_white['abc']) 

df_white.drop(['_id', 'created'], axis=1, inplace=True)
df_white['url']= df_white['url'].apply(lambda i: i.split("//")[-1].replace('*','').rstrip("/").strip("."))


# URL model
def url_model(url):
    #Blacklist
    print("kiet oi =>>>>>>>>>>>>>>>>>>>> chay den day")
    for i in range(len(df)):
        if url.find(df['url'].iloc[i]) != -1:
            print("May chet !!! Blacklist nhe")
            return 1

    #Whitelist
    for i in range(len(df_white)):
        if url.find(df_white['url'].iloc[i]) != -1:
            print("trong whitelist roi ong chau oi!!!")
            return 0 

    print("ko co trong rule1")
    url_features = generate_features(url) # Extracting features
    print("ko co trong rule2")
    sacle_ = sc.fit_transform(url_features) # scale
    print("ko co trong rule3")
    ae_ = encoder.predict(sacle_) # autoencoder

    print("done input ae")
    try:
        # RandomForest
        rf_ = rf.predict(ae_)[0] 
        print("ok random forest !!!")
        # one class support vector machines
        ocsvm_ = clf.predict(ae_)[0] 
        print("ok one class")
        if ocsvm_ == 1 and rf_ == 1:
            return 1
        elif ocsvm_ == 0 and rf_ == 0:
            return 0
        else:
            return 0.5
        
    except:
        return -2

#web

app = Flask(__name__)
app.secret_key = "doan"
app.config['UPLOAD_EXTENSIONS'] = ['.txt', '.doc', '.docx','.csv']


cwd = os.getcwd()
FILES_FOLDER = os.path.join(cwd, 'files')
app.config['FILES_FOLDER'] = FILES_FOLDER


@app.route("/")
def index():
    # return render_template("index.html", xx= -1)
    return render_template("new.html")


# nhận 1 url
@app.route("/get_url", methods= ["POST"])
def get_url():
    try:
        if request.method == 'POST':
            text_url = request.values.get('url')
            print("co dua test => ", text_url)
            if text_url != None:
                # xử lý detect url
                # ...
                x = url_model(text_url)

                if x == 1:
                    predict_url = "UNSAFE"
                elif x == 0:
                    predict_url = "SAFE"
                else:
                    predict_url = "SUSPICIOUS"


                data = {
                    "url": text_url,
                    "predict": predict_url
                }
                return json.dumps(data, ensure_ascii=False)
    except Exception as e:
        print("\tError ne kiet", e)
        return redirect(url_for('index'))
    return redirect(url_for('index'))

# nhận file csv
@app.route("/get_file", methods=["POST"])
def get_file():
    try:
        if request.method == 'POST':
            if request.files:
                f = request.files['file']
                fileName = f.filename
                filename = secure_filename(fileName)
                if filename != '':
                    file_exten = os.path.splitext(filename)[1]
                    if file_exten not in app.config['UPLOAD_EXTENSIONS']:
                        flash("Please upload files with the following extensions: '.txt', '.doc', '.docx'!")
                        abort(400)
                f.save(os.path.join(app.config['FILES_FOLDER'],fileName))
                # đọc file
                # temp_file = 
                df = pd.read_csv("files\\"+filename,names=['url'])
                # # xử lý detect
                # out_list = f.readlines()
                # return redirect(url_for('home'))

                df["predict"] = ''

                for i in range(len(df)):
                    x = url_model(df['url'].iloc[i])
                    if x == 1:
                        predict_url = "UNSAFE"
                    elif x == 0:
                        predict_url = "SAFE"
                    else:
                        predict_url = "SUSPICIOUS"
                    df['predict'].iloc[i] = predict_url

                data = df.to_json(orient = "records")
                data = json.loads(data)
                # print(a)

                # data = [
                #         ["url", filename, "predict" , "Độc hại"],
                #         ["url", data, "predict" , "Bình thường"],
                #         ["url", df['url'].iloc[1], "predict" , "Tốt"]
                #     ]
                
                # data = [{"url":"https:\/\/www.facebook.com\/","predict":"SAFE"},{"url":"https:\/\/www.google.com.vn\/","predict":"SAFE"},{"url":"https:\/\/binhchonhoakhoivietnammua9.weebly.com\/","predict":"UNSAFE"}]
                return json.dumps(data, ensure_ascii=False)
    except Exception as e:
        print("\tError", e)
        return redirect(url_for('index'))
    return redirect(url_for('index'))


@app.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "POST":

        url = request.form["url"]

        x = url_model(url)

        if x == 1:
            return render_template('index.html',xx = 1,url=url )
        elif x == 0:
            return render_template('index.html',xx = 0,url=url )
        elif x == 0.5:
            return render_template('index.html',xx = 0.5,url=url )
        else:
            return render_template('index.html',xx = -2,url=url )
    return render_template("index.html", xx =-1)


@app.route("/extension", methods=["GET", "POST"])
def predict_1():
    # a = str(request)
    try:
        if request.method == "POST":

            url = request.args.get('url')

            x = url_model(url)

            if x == 1:
                predict_url = "UNSAFE"
            elif x == 0:
                predict_url = "SAFE"
            else:
                predict_url = "SUSPICIOUS"
            return predict_url
    except:
        return "error"
    return "DUNG"
    
@app.route("/web", methods=["GET", "POST"])
def web():
    # a = str(request.args.get('url'))
    if request.method == "POST":

        url = request.args.get('url')

        x = url_model(url)

        if x == 1:
            return "1"
        elif x == 0:
            return "0"
        elif x == 0.5:
            return "0.5"
        else:
            return "-2"

    return "-1"


from pusher import Pusher
pusher = Pusher(app_id="1496129", key="e0f057db90b68cb7a529", secret="95f3c0e4626c0df3d2e7", cluster="ap1")


@app.route('/dashboard')
def dashboard():
	return render_template('dashboard.html')

@app.route('/url', methods=['POST'])
def url():
    if request.method == "POST":
        url_request = request.args.get('url')
        #xử lý detect url
        print("co dua test ==>", url_request)
        temp_url = url_model(url_request)

        if temp_url == 1:
            predict_url = "UNSAFE"
        elif temp_url == 0:
            predict_url = "SAFE"
        else:
            predict_url = "SUSPICIOUS"


        pusher.trigger('url', 'add_1', {
            'url': url_request,
            'type': predict_url
        })
    return url_request

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3400, debug=True)