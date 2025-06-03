"""
    This code is for extraction of cardiac features from ACDC testing database segmentations (predictions)
"""
import os, re
import numpy as np
import pandas as pd
import sys
# print sys.path

# Custom
from utils_heart import * 


HEADER = ["Name", "ED[vol(LV)]", "ES[vol(LV)]", "ED[vol(RV)]", "ES[vol(RV)]",
          "ED[mass(MYO)]", "ES[vol(MYO)]", "EF(LV)", "EF(RV)", "ED[vol(LV)/vol(RV)]", "ES[vol(LV)/vol(RV)]", "ED[mass(MYO)/vol(LV)]", "ES[vol(MYO)/vol(LV)]",
          "ES[max(mean(MWT|SA)|LA)]", "ES[stdev(mean(MWT|SA)|LA)]", "ES[mean(stdev(MWT|SA)|LA)]", "ES[stdev(stdev(MWT|SA)|LA)]", 
          "ED[max(mean(MWT|SA)|LA)]", "ED[stdev(mean(MWT|SA)|LA)]", "ED[mean(stdev(MWT|SA)|LA)]", "ED[stdev(stdev(MWT|SA)|LA)]", "GROUP"]

def calculate_metrics_from_pred(data_path, pred_name='prediction'):
    pred_files = next(os.walk(data_path))[2]
    print(os.walk(data_path))
    res=[]
    seen_patient = []
    for patient in sorted(pred_files):
        m = re.match("patient(\d{3})", patient)
        patient_No = int(m.group(1))
        print(patient_No)
        if patient_No not in seen_patient:
            print (patient)
            seen_patient.append(patient_No)       
            # print patient_No
            ed = "patient%03d_ED.nii" %(patient_No)
            es = "patient%03d_ES.nii" %(patient_No)
            # Load data
            ed_data = nib.load(os.path.join(data_path, ed))
            es_data = nib.load(os.path.join(data_path, es))

            ed_lv, ed_rv, ed_myo = heart_metrics(ed_data.get_data(),
                            ed_data.header.get_zooms())
            es_lv, es_rv, es_myo = heart_metrics(es_data.get_data(),
                            es_data.header.get_zooms())
            ef_lv = ejection_fraction(ed_lv, es_lv)
            ef_rv = ejection_fraction(ed_rv, es_rv)


            myo_properties = myocardial_thickness(os.path.join(data_path, es))
            es_myo_thickness_max_avg = np.amax(myo_properties[0])
            es_myo_thickness_std_avg = np.std(myo_properties[0])
            es_myo_thickness_mean_std = np.mean(myo_properties[1])
            es_myo_thickness_std_std = np.std(myo_properties[1])

            myo_properties = myocardial_thickness(os.path.join(data_path, ed))
            ed_myo_thickness_max_avg = np.amax(myo_properties[0])
            ed_myo_thickness_std_avg = np.std(myo_properties[0])
            ed_myo_thickness_mean_std = np.mean(myo_properties[1])
            ed_myo_thickness_std_std = np.std(myo_properties[1])
            # print (es_myo_thickness_max_avg, es_myo_thickness_std_avg, es_myo_thickness_mean_std, es_myo_thickness_std_std,
            #      ed_myo_thickness_max_avg, ed_myo_thickness_std_avg, ed_myo_thickness_std_std, ed_myo_thickness_std_std)

            heart_param = {'EDV_LV': ed_lv, 'EDV_RV': ed_rv, 'ESV_LV': es_lv, 'ESV_RV': es_rv,
                   'ED_MYO': ed_myo, 'ES_MYO': es_myo, 'EF_LV': ef_lv, 'EF_RV': ef_rv,
                   'ES_MYO_MAX_AVG_T': es_myo_thickness_max_avg, 'ES_MYO_STD_AVG_T': es_myo_thickness_std_avg, 'ES_MYO_AVG_STD_T': es_myo_thickness_mean_std, 'ES_MYO_STD_STD_T': es_myo_thickness_std_std,
                   'ED_MYO_MAX_AVG_T': ed_myo_thickness_max_avg, 'ED_MYO_STD_AVG_T': ed_myo_thickness_std_avg, 'ED_MYO_AVG_STD_T': ed_myo_thickness_mean_std, 'ED_MYO_STD_STD_T': ed_myo_thickness_std_std,}
            r=[]
            pid = 'patient{:03d}'.format(patient_No)
            r.append(pid)
            r.append(heart_param['EDV_LV'])
            r.append(heart_param['ESV_LV'])
            r.append(heart_param['EDV_RV'])
            r.append(heart_param['ESV_RV'])
            r.append(heart_param['ED_MYO'])
            r.append(heart_param['ES_MYO'])
            r.append(heart_param['EF_LV'])
            r.append(heart_param['EF_RV'])
            r.append(ed_lv/ed_rv)
            r.append(es_lv/es_rv)
            r.append(ed_myo/ed_lv)
            r.append(es_myo/es_lv)
            r.append(heart_param['ES_MYO_MAX_AVG_T'])
            r.append(heart_param['ES_MYO_STD_AVG_T'])
            r.append(heart_param['ES_MYO_AVG_STD_T'])
            r.append(heart_param['ES_MYO_STD_STD_T'])

            r.append(heart_param['ED_MYO_MAX_AVG_T'])
            r.append(heart_param['ED_MYO_STD_AVG_T'])
            r.append(heart_param['ED_MYO_AVG_STD_T'])
            r.append(heart_param['ED_MYO_STD_STD_T'])
            # Apppend Blank for Stage 1 results to be populated
            r.append('')
            res.append(r) 
        # break
    df = pd.DataFrame(res, columns=HEADER[:len(HEADER)])
    if not os.path.exists('./prediction_data'):
        os.makedirs('./prediction_data')
    df.to_csv("./prediction_data/Cardiac_parameters_{}.csv".format(pred_name), index=False)

def execute_generate_features_test():
    # Data directories:
    # Path to final test set segmentation results of ACDC 2017 challenge
    test_prediction_path = './trained_models/ACDC/FCRD_ACDC/predictions/best_model_class2/testing2/patient071'
    # test_prediction_path = '/media/brats/0d4a2225-d6b1-4b80-94fd-7c8ae0b1fa102/MAK/Cardiac/ACDC_Project/models/FIRD_ACDC_P_3_k_16_WCE_WDICE_AUG_256_minmax/predictions_BN_F20180407_120744/leaderboard'
    calculate_metrics_from_pred(test_prediction_path, pred_name='minmax_k_16')
