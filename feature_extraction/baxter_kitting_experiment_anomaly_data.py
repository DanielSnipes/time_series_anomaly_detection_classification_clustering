import matplotlib.pylab as plt
from tsfresh import extract_features, extract_relevant_features, select_features
from tsfresh.utilities.dataframe_functions import impute
from tsfresh.feature_extraction import ComprehensiveFCParameters
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pandas as pd
import numpy as np
import os
from HMM.hmm_for_baxter_using_only_success_trials import training_config
import ipdb

def load_baxter_kitting_anomaly_data_as_df():
    dataset_path = training_config.anomaly_data_path
    try:
        X = np.load(os.path.join(dataset_path, 'X.npy'))
        y = np.load(os.path.join(dataset_path, 'y.npy'))
        labels  = np.load(os.path.join(dataset_path, 'labels_list.npy'))

        raw_x_train = np.load(os.path.join(dataset_path, 'X_train.npy'))        
        raw_y_train = np.load(os.path.join(dataset_path, 'y_train.npy'))        
        raw_x_test  = np.load(os.path.join(dataset_path, 'X_test.npy'))
        raw_y_test  = np.load(os.path.join(dataset_path, 'y_test.npy'))
        
    except IOError:
        print('Error occured trying to read the file, please check the path: ' + TRAIN_TEST_DATASET_PATH)
    n_dim, n_len =  X[0].shape
    df_rows = []
    for i in range(len(X)):
        # data format in tsfresh
        time = 0
        xT = X[i].T
        for j in range(n_len):
            df_rows.append([i, time] + xT[j].tolist())
            time += 1
    training_config.interested_data_fields.pop()
    df = pd.DataFrame(df_rows, columns = ['id', 'time'] + training_config.interested_data_fields)
    y  = pd.Series(y)
    return df, y, labels, raw_x_train, raw_y_train, raw_x_test, raw_y_test
    
if __name__=="__main__":
    df, y, labels, raw_x_train, raw_y_train, raw_x_test, raw_y_test = load_baxter_kitting_anomaly_data_as_df()
    print labels
    col = ['time'] + training_config.interested_data_fields
    df[df.id == 3][col].plot(x='time', title='(id 3)', figsize=(12, 6))
    plt.show()

    #extract features
    extraction_settings = ComprehensiveFCParameters()
    X = extract_features(df, 
                         column_id='id', column_sort='time',
                         default_fc_parameters=extraction_settings,
                         impute_function= impute)
    
    X_filtered = extract_relevant_features(df, y, 
                                       column_id='id', column_sort='time', 
                                       default_fc_parameters=extraction_settings)
    #Train and evaluate classifier
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.5, stratify=y)
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

    '''
    ipdb.set_trace()
    #naive classification accuracy
    cl = DecisionTreeClassifier()
    cl.fit(raw_x_train, raw_y_train)
    print ('naive features:')
    print(classification_report(raw_y_test, cl.predict(raw_x_test)))
    '''
    
