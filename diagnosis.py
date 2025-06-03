from __future__ import print_function
import joblib

from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_score, cross_val_predict
import matplotlib.pyplot as plt
import itertools
import sys
import pandas as pd

import numpy as np
from sklearn.preprocessing import StandardScaler  

import joblib

test_on_prediction = './prediction_data/Cardiac_parameters_minmax_k_16.csv'
full_training = './training_data/Cardiac_parameters_training.csv'

START_COL = 1
END_COL = 21

NOR = 'NOR'
# 30 patients with previous myocardial infarction
# (ejection fraction of the left ventricle lower than 40% and several myocardial segments with abnormal contraction) - MINF
MINF = 'MINF'
# 30 patients with dilated cardiomyopathy
# (diastolic left ventricular volume >100 mL/m2 and an ejection fraction of the left ventricle lower than 40%) - DCM
DCM = 'DCM'
# 30 patients with hypertrophic cardiomyopathy
# (left ventricular cardiac mass high than 110 g/m2,
# several myocardial segments with a thickness higher than 15 mm in diastole and a normal ejecetion fraction) - HCM
HCM = 'HCM'
# 30 patients with abnormal right ventricle (volume of the right ventricular
# cavity higher than 110 mL/m2 or ejection fraction of the rigth ventricle lower than 40%) - RV
RV = 'RV'

heart_disease_label_map = {NOR:0, MINF:1,DCM:2,HCM:3, RV:4}

def load_dataframe(csv_file, shuffle=False):
    """
    Load Patient information from the csv file as a dataframe
    """
    df = pd.read_csv(csv_file)
    if shuffle:
        df = df.sample(frac=1).reset_index(drop=True)
    # patient_data = df.to_dict("records")
    # return patient_data
    return df

def encode_target(df, target_column, label_map):
 
    df_mod = df.copy()
    targets = df_mod[target_column].unique()
    # map_to_int = {name: n for n, name in enumerate(targets)}
    df_mod[target_column] = df_mod[target_column].replace(label_map)

    return (df_mod, targets)

def CardiacDiagnosisModelTester(clf, final_test_path, name, scaler, save_dir=None, label_available=False, prediction_csv=None):
    """
    This code does the cardiac disease classification (5-classes)
    """
    class_names = [NOR, MINF, DCM, HCM, RV]
    df = load_dataframe(final_test_path)
    features = list(df.columns[np.r_[START_COL:END_COL]])
    X_df = df[features]
    print (features)
    X_scaled = scaler.transform(X_df)  
    y_pred = clf.predict(X_scaled)
    

    classes = {NOR: 0,MINF:0,DCM:0,HCM:0,RV:0}

    if label_available:
        y_true,_ = encode_target(df, 'GROUP', heart_disease_label_map)
        accuracy = accuracy_score(y_true['GROUP'], y_pred)
        
    else:
        if prediction_csv:
            df = load_dataframe(test_on_prediction)
            df['GROUP'] = [class_names[pred] for pred in y_pred]
            # print(df['GROUP'])
            df.to_csv(prediction_csv,  index=False)


class_names = [NOR, MINF, DCM, HCM, RV]
loaded_model = joblib.load('finalized_model.sav')

train_df, train_targets = encode_target(load_dataframe(full_training, shuffle=False), 'GROUP', heart_disease_label_map)
features = list(train_df.columns[np.r_[START_COL:END_COL]])
X = train_df[features]
y = train_df['GROUP']
scaler = StandardScaler() 
scaler.fit(X)


def diagnosis_stage_1():
    CardiacDiagnosisModelTester(loaded_model, test_on_prediction, name='EnsembleOnFinalTestSet', scaler=scaler, save_dir=None, label_available=False,
                                    prediction_csv=test_on_prediction)