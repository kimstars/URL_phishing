import pandas as pd
# from app import url_model
import json
from pandas import json_normalize
# f = pd.read_csv("files\\"+"test_file.csv",names=['url'])

# f["predict"] = ''

# for i in range(len(f)):
#     x = url_model(f['url'].iloc[i])
#     if x == 1:
#         predict_url = "UNSAFE"
#     elif x == 0:
#         predict_url = "SAFE"
#     else:
#         predict_url = "SUSPICIOUS"

#     f['predict'].iloc[i] = predict_url

# out = f.to_json(orient = "records")
# print(type(out))
# print(out)

# import json
# # data = [
# #                         {"url": "http://localhost:3000", "predict" : "Độc hại"},
# #                         {"url": "http://localhost:3000", "predict" : "Bình thường"},
# #                         {"url": "http://localhost:3000", "predict" : "Tốt"}
# #                     ]
# data = [{"url":"https:\/\/www.facebook.com\/","predict":"SAFE"},{"url":"https:\/\/www.google.com.vn\/","predict":"SAFE"},{"url":"https:\/\/binhchonhoakhoivietnammua9.weebly.com\/","predict":"UNSAFE"}]


# print(type(data))
# print(data)
# print(type(json.dumps(data, ensure_ascii=False)))

#Blacklist
f = open('static\\blacklist.json',encoding="utf8")

json_object = json.load(f)

df = json_normalize(json_object['abc']) 

df.drop(['_id', 'type', 'level', 'created'], axis=1, inplace=True)
df['url']= df['url'].apply(lambda i: i.split("//")[-1].replace('*','').rstrip("/").strip("."))

print(df)