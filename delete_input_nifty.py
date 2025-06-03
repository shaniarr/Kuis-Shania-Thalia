import os 


def delete_nifty_input():
    for a in os.listdir('./testing/testing2/patient071'):
        os.remove('./testing/testing2/patient071/' + a)


