import pandas as pd


def take_data():
    data = pd.read_csv('./prediction_data/Cardiac_parameters_minmax_k_16.csv')


    parameter = {}

    parameter['ED[vol(LV)]'] = data['ED[vol(LV)]'].values[0]
    parameter['ES[vol(LV)]'] = data['ES[vol(LV)]'].values[0]

    parameter['ED[vol(RV)]'] = data['ED[vol(RV)]'].values[0]
    parameter['ES[vol(RV)]'] = data['ES[vol(RV)]'].values[0]

    parameter['ED[vol(LV)/vol(RV)]'] = data['ED[vol(LV)/vol(RV)]'].values[0]
    parameter['ES[vol(LV)/vol(RV)]'] = data['ES[vol(LV)/vol(RV)]'].values[0]


    if data['GROUP'].values[0] == 'NOR':
        parameter['GROUP'] = 'Normal'
    elif data['GROUP'].values[0] == 'MINF':
        parameter['GROUP'] =  "Myocardial Infarction"
    elif data['GROUP'].values[0] == 'DCM':
        parameter['GROUP'] =  " Dilated Cardiomyopathy"
    elif data['GROUP'].values[0] == 'HCM':
        parameter['GROUP'] =  "Hypertrophic Cardiomyopathy"
    elif data['GROUP'].values[0] == 'RV':
        parameter['GROUP'] =  " Abnormal Right Ventricle"

    
    return parameter
