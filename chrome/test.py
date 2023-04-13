# Purpose - Receive the call for testing a page from the Chrome extension and return the result (SAFE/PHISHING)
# for display. This file calls all the different components of the project (The ML model, features_extraction) and
# consolidates the result.

import joblib
import features_extraction
import sys
import numpy as np
import pickle
#import ipdb
from features_extraction import LOCALHOST_PATH, DIRECTORY_NAME

from sklearn.preprocessing import OneHotEncoder

def convertEncodingToPositive(data):
  mapping = {-1: 2, 0: 0, 1: 1}
  i = 0
  for col in data:
    data[i] = mapping[col]
    i+=1
  return data

def get_prediction_from_url(test_url):
    features_test = features_extraction.main(test_url)
    # Due to updates to scikit-learn, we now need a 2D array as a parameter to the predict function.
    features_test = np.array(features_test).reshape((1, -1))
    with open("./classifier/SVM_Final_Model") as file_x:
      xread = file_x.readlines()
    clf = pickle.load(LOCALHOST_PATH + DIRECTORY_NAME + '/classifier/SVM_Final_Model')
    #ipdb.set_trace();
    pred = clf.predict(features_test)
    return int(pred[0])

def predict(url):
  features_extracted = features_extraction.main(url)
  features_extracted = convertEncodingToPositive(features_extracted)
  one_hot_enc = pickle.load(open(LOCALHOST_PATH + DIRECTORY_NAME +'/classifier/One_Hot_Encoder', "rb"))
  transformed_point = one_hot_enc.transform(np.array(features_extracted).reshape(1, -1))
  features_extracted = np.array(features_extracted).reshape(1, -1)
  model = pickle.load(open(LOCALHOST_PATH + DIRECTORY_NAME +'/classifier/SVM_Final_Model', "rb"))
  status = model.predict(transformed_point)
  """ prob = model.predict_proba(transformed_point)
  print('Features=', transformed_point, 'The predicted probability is - ', prob, 'The predicted label is - ', status)
  print("The probability of this site being a phishing website is ", transformed_point[0]) """
  #status = model.predict(features_extracted)
  return int(status[0])

def main():
    url = sys.argv[1]

    prediction = predict(url)

    # Print the probability of prediction (if needed)
    # prob = clf.predict_proba(features_test)
    # print 'Features=', features_test, 'The predicted probability is - ', prob, 'The predicted label is - ', pred
    #    print "The probability of this site being a phishing website is ", features_test[0]*100, "%"

    if prediction == 1:
        # print "The website is safe to browse"
        print("SAFE")
    elif prediction == 2:
        # print "The website has phishing features. DO NOT VISIT!"
        print("PHISHING")

        # print 'Error -', features_test


if __name__ == "__main__":
    main()
