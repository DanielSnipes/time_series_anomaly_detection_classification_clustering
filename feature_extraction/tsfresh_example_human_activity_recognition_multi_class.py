import matplotlib.pylab as plt
import seaborn as sns
from tsfresh import extract_features, extract_relevant_features, select_features
from tsfresh.utilities.dataframe_functions import impute
from tsfresh.feature_extraction import ComprehensiveFCParameters
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pandas as pd
import numpy as np
import os
import logging
import ipdb

module_path = os.path.dirname(os.path.abspath(__file__))
data_file_name = os.path.join(module_path, 'data')
data_file_name_dataset = os.path.join(module_path, 'data', 'human-activity-dataset', 'train', 'Inertial Signals',
                                      'body_acc_x_train.txt')
data_file_name_classes = os.path.join(module_path, 'data', 'human-activity-dataset', 'train', 'y_train.txt')


def load_har_dataset():
    try:
        return pd.read_csv(data_file_name_dataset, delim_whitespace=True, header=None)
    except IOError:
        raise IOError('File {} was not found. Have you downloaded the dataset with download_har_dataset() '
                      'before?'.format(data_file_name_dataset))


def load_har_classes():
    try:
        return pd.read_csv(data_file_name_classes, delim_whitespace=True, header=None, squeeze=True)
    except IOError:
        raise IOError('File {} was not found. Have you downloaded the dataset with download_har_dataset() '
                      'before?'.format(data_file_name_classes))
N = 500
df = load_har_dataset()
y = load_har_classes()[:N]
X_1 = df.ix[:N-1,:]
ipdb.set_trace()

plt.title('body accelerometer reading')
plt.plot(df.ix[0,:])
plt.show()

#extract features
extraction_settings = ComprehensiveFCParameters()
# rearrange first 500 sensor readings column-wise, not row-wise
master_df = pd.DataFrame({0: df[:N].values.flatten(),
                          1: np.arange(N).repeat(df.shape[1])})
X = extract_features(master_df, column_id=1, impute_function=impute, default_fc_parameters=extraction_settings)
print ("Number of extracted features: {}.".format(X.shape[1]))

#Train and evaluate classifier
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2)
cl = DecisionTreeClassifier()
cl.fit(X_train, y_train)
print ('Extracted features:')
print(classification_report(y_test, cl.predict(X_test)))

#Multiclass feature selection
relevant_features = set()
for label in y.unique():
    y_train_binary = y_train == label
    X_train_filtered = select_features(X_train, y_train_binary)
    print("Number of relevant features for class {}: {}/{}".format(label, X_train_filtered.shape[1], X_train.shape[1]))
    relevant_features = relevant_features.union(set(X_train_filtered.columns))
X_train_filtered = X_train[list(relevant_features)]
X_test_filtered = X_test[list(relevant_features)]
cl = DecisionTreeClassifier()
cl.fit(X_train_filtered, y_train)
print ('Selected features:')
print(classification_report(y_test, cl.predict(X_test_filtered)))

#naive classification accuracy
X_1 = df.ix[:N-1,:]
X_train, X_test, y_train, y_test = train_test_split(X_1, y, test_size=.2)
cl = DecisionTreeClassifier()
cl.fit(X_train, y_train)
print ('naive features:')
print(classification_report(y_test, cl.predict(X_test)))

ipdb.set_trace()  
