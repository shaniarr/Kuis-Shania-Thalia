from matplotlib import patches
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
import os, sys


def make_4D_raw():
    list_of_files = sorted( filter( lambda x: os.path.isfile(os.path.join('./testing/testing2/patient071', x)),
                            os.listdir('./testing/testing2/patient071') ) )
    test_load = nib.load('./testing/testing2/patient071/' + list_of_files[0]).get_data()
    fig, axes = plt.subplots(ncols=5, nrows=4, figsize=(50, 50))
    plt.gcf().set_size_inches(50, 50)
    for t, ax in enumerate(axes.flatten()):    
        ax.imshow(test_load[:, :, 4, t].T, cmap='gray')  # index with t!
        
        ax.axis('off')
        ax.set_title('t = %i' % int(t+1), fontsize=40)

    plt.savefig('./image_figure/my_plot_4D.png')

def make_4D_GT():
    list_of_files = sorted( filter( lambda x: os.path.isfile(os.path.join('./trained_models/ACDC/FCRD_ACDC/predictions/best_model_class2/testing2/patient071', x)),
                            os.listdir('./trained_models/ACDC/FCRD_ACDC/predictions/best_model_class2/testing2/patient071') ) )
    test_load = nib.load('./trained_models/ACDC/FCRD_ACDC/predictions/best_model_class2/testing2/patient071/' + list_of_files[0]).get_data()
    fig, axes = plt.subplots(ncols=5, nrows=4, figsize=(50, 50))
    plt.gcf().set_size_inches(50, 50)
    for t, ax in enumerate(axes.flatten()):    
        ax.imshow(test_load[:, :, 4, t].T, cmap='gray')  # index with t!
        
        ax.axis('off')
        ax.set_title('t = %i' % int(t+1), fontsize=40)

    plt.savefig('./image_figure/my_plot_4D_GT.png')


