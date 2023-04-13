# Purpose - This file is used to create a classifier and store it in a pickle file. 

import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn import metrics
from scipy.io import arff

import joblib
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.preprocessing import OneHotEncoder, LabelEncoder, OrdinalEncoder

#data = []
data  = arff.loadarff('dataset/Training Dataset.arff')
df = pd.DataFrame(data[0])
str_df = df.select_dtypes([np.object]) 
str_df = str_df.stack().str.decode('utf-8').unstack()
for col in str_df.columns:
    str_df[col] = str_df[col].astype(int)

complete_training = str_df
complete_training['Result'].value_counts()

reduced_df = complete_training[['having_IP_Address', 'URL_Length', 'Shortining_Service',
       'having_At_Symbol', 'double_slash_redirecting', 'Prefix_Suffix',
       'having_Sub_Domain', 'SSLfinal_State', 'Domain_registeration_length',
       'Favicon', 'HTTPS_token', 'Request_URL', 'URL_of_Anchor',
       'Links_in_tags', 'SFH', 'Submitting_to_email', 'Redirect', 'on_mouseover', 'RightClick', 'Iframe',
       'age_of_domain', 'DNSRecord', 'web_traffic', 'Page_Rank',
       'Statistical_report', 'Result']]

def convertEncodingToPositive(dataframe):

  mapping = {-1: 2, 0: 0, 1: 1}

  col_map = {}

  for col in dataframe:
    col_map[col] = mapping

  for i in range(dataframe.shape[0]):
    # if (i%100 == 0):
    #   print(i)
    for j in range(dataframe.shape[1]):
      dataframe.loc[i][j] = mapping[dataframe.loc[i][j]]

convertEncodingToPositive(reduced_df)

#print(reduced_df)

from sklearn.model_selection import train_test_split, KFold

X_reduced = reduced_df.iloc[:,0:25]
y_reduced = reduced_df.iloc[:, -1]

X_train_red, X_test_red, y_train_red, y_test_red = train_test_split(X_reduced, y_reduced, test_size=0.2, random_state=7, stratify=y_reduced)
print(X_test_red.shape)

kf = KFold(n_splits=5, shuffle=True, random_state=786)
X_train_red = X_train_red.to_numpy()
X_test_red = X_test_red.to_numpy()
y_train_red = y_train_red.to_numpy()
y_test_red = y_test_red.to_numpy()
for train, test in kf.split(X_train_red):
  print(X_train_red[train].shape, y_train_red[train].shape, X_train_red[test].shape, y_train_red[test].shape)

from sklearn.metrics import confusion_matrix
def plot_cm(y_val, y_pred):
  labels = [1, 0]
  cm = confusion_matrix(y_val, y_pred, labels)
  # print(cm)
  fig = plt.figure()
  ax = fig.add_subplot(111)
  cax = ax.matshow(cm)
  plt.title('Confusion matrix of the classifier')
  fig.colorbar(cax)
  ax.set_xticklabels([''] + labels)
  ax.set_yticklabels([''] + labels)
  plt.xlabel('Predicted')
  plt.ylabel('True')

import pickle
from sklearn.preprocessing import OneHotEncoder
encoder = OneHotEncoder(sparse=False)
X_train_red_onehot = encoder.fit_transform(X_train_red)
X_test_red_onehot = encoder.transform(X_test_red)
pickle.dump(encoder, open("classifier/One_Hot_Encoder", 'wb'))

from sklearn import svm
from sklearn.model_selection import GridSearchCV

def grid_search_svm(X_train_red_onehot, y_train_red):
  svm_clf = svm.SVC()
  param_grid = {'C': [0.1, 1, 10, 100],  
                'gamma': [1, 0.1, 0.01, 0.001], 
                'kernel': ['rbf', 'linear']}  

  gs_svm = GridSearchCV(svm.SVC(), param_grid, cv = 3)
  gs_results = gs_svm.fit(X_train_red_onehot, y_train_red)

  return gs_results.best_params_

bestparams_svm = grid_search_svm(X_train_red_onehot, y_train_red)
print(bestparams_svm)

def to_use_SVM(X_train_red_onehot, y_train_red):
  accuracy_scores_svm = []
  for train, val in kf.split(X_train_red_onehot):
    svm_clf = svm.SVC(kernel='rbf', gamma = 0.1, C = 10, probability=True)
    svm_clf = svm_clf.fit(X_train_red_onehot[train], y_train_red[train])
    tp, fn, fp, tn = metrics.confusion_matrix(y_train_red[val], svm_clf.predict(X_train_red_onehot[val])).ravel()
    plot_cm(y_train_red[val], svm_clf.predict(X_train_red_onehot[val]))
    
    accuracy = (tn+tp)/(fp+fn+tp+tn)
    precision = tp/(tp+fp)
    recall = tp/(tp+fn)
    fpr = fp/(fp+tn)
    f1 = 2*precision*recall/(precision + recall)
    accuracy_scores_svm.append((accuracy, precision, recall, fpr, f1))


  return np.mean(accuracy_scores_svm, axis=0)

metric_svm = to_use_SVM(X_train_red_onehot, y_train_red)
print(metric_svm)

def to_test_SVM(X_test_red_onehot, y_test_red, X_train_red_onehot, y_train_red):
  svm_clf = svm.SVC(kernel='rbf', gamma = 0.1, C = 10, probability=True)
  svm_clf = svm_clf.fit(X_train_red_onehot, y_train_red)
  tp, fn, fp, tn = metrics.confusion_matrix(y_test_red, svm_clf.predict(X_test_red_onehot)).ravel()
  accuracy = (tn+tp)/(fp+fn+tp+tn)
  precision = tp/(tp+fp)
  recall = tp/(tp+fn)
  fpr = fp/(fp+tn)
  f1 = 2*precision*recall/(precision + recall)
  pickle.dump(svm_clf, open("./classifier/SVM_Final_Model", 'wb'))
  return accuracy

test_accuracy = to_test_SVM(X_test_red_onehot, y_test_red, X_train_red_onehot, y_train_red)
print(test_accuracy)


