import datetime
from distutils.log import debug
import os
from zipfile import ZipFile
from flask import Flask, render_template, redirect, url_for, session, flash, Markup, request
from werkzeug.utils import secure_filename
from forms import RegistrationForm, LoginForm, ResetPassword
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
import pymysql
import re
from google.cloud import storage
from datetime import datetime, date, timedelta
from flask_session import Session
from os.path import basename
# from flask_wtf.csrf import CSRFProtect
import requests
import time
from flask_mail import Message, Mail
from random import *


from test import execute
from generate_cardiac_features_test import execute_generate_features_test
from diagnosis import diagnosis_stage_1
# from stage_2_diagnosis import diagnosis_stage_2
from make_image import *
from take_data_csv import *
from delete_input_nifty import *

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(50)
bcrypt = Bcrypt(app)
# # csrf = CSRFProtect(app)
WTF_CSRF_ENABLED = True

app.config["MAIL_SERVER"]='smtp.gmail.com'  
app.config["MAIL_PORT"] = 465      
app.config["MAIL_USERNAME"] = 'qardiosis@gmail.com'  
app.config['MAIL_PASSWORD'] = 'wgtyspzqxfbkttaz'  
app.config['MAIL_USE_TLS'] = False  
app.config['MAIL_USE_SSL'] = True   
otp = randint(000000,999999)
mail = Mail(app)

db_user = os.environ.get('CLOUD_SQL_USERNAME')
db_password = os.environ.get('CLOUD_SQL_PASSWORD')
db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')

# #########
path = os.getcwd()
# # file Upload
UPLOAD_FOLDER = os.path.join(path, 'testing/testing2/patient071')

# # Make directory if uploads is not exists
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)
    
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# #File Upload Configuration
app.config['UPLOAD_EXTENSIONS'] = ['dcm', 'nii', 'gz', 'zip', 'gzip', 'GZ']
# ############
# #Storage Configuration
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'qardiosis-gae.json'
storage_client = storage.Client()
bucket_name = os.environ.get('CLOUD_STORAGE_BUCKET_NAME')
bucket = storage_client.bucket(bucket_name)

my_bucket = storage_client.get_bucket(bucket_name)


def conf():
    # When deployed to App Engine, the `GAE_ENV` environment variable will be
    # set to `standard`
    try:
        # if os.environ.get('GAE_ENV') == 'flex':
            # If deployed, use the local socket interface for accessing Cloud SQL
        unix_socket = '/cloudsql/{}'.format(db_connection_name)
        cnx = pymysql.connect(user=db_user, password=db_password,
                          db=db_name, unix_socket=unix_socket)
        # else:
        #     # If running locally, use the TCP connections instead
        #     # Set up Cloud SQL Proxy (cloud.google.com/sql/docs/mysql/sql-proxy)
        #     # so that your application can use 127.0.0.1:3306 to connect to your
        #     # Cloud SQL instance
        #     host = '127.0.0.1'
        #     cnx = pymysql.connect(user=db_user, password=db_password,
        #                       host=host, db=db_name)
        return cnx
    
    except pymysql.MySQLError as e:
        print(e)

@app.before_request
def make_session_permanent():
    session.permanent = True
    # app.permanent_session_lifetime = timedelta(minutes=1)


@app.route('/', methods=['GET', 'POST'])
def login():
    try:
        form = LoginForm(request.form)
        username = form.username.data
        password = form.password.data
        conn = conf()
        if form.validate_on_submit():
            try :
                with conn.cursor() as cur:
                    cur.execute('SELECT * FROM user WHERE username = %s AND state = %s', (username, True))
                    account = cur.fetchone()
                    print(account)
                    print(account[5])
                    conn.close()
                    result = bcrypt.check_password_hash(account[5], password)
                    if username and result:
                        session['logged in'] = True
                        session['username'] = account[4]
                        session['id'] = account[0]
                        print(session['id'])
                        return redirect(url_for('home'))
                    else:
                        flash(u"Incorrect Password ! Please try again.", "Error")
                        return redirect(url_for('login'))
            except Exception as e:
                flash(u"Your Username Doesn't Exist or You input wrong username. Please, try again!", "Error")
                print(e)
    except Exception as e:
        flash(u"You have to login first", "Error")
        print (e)
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        form = RegistrationForm(request.form)
        conn = conf()
        con= conf()
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        username = form.username.data
        password = form.password.data
        medical_number = form.medical_number.data
        print(medical_number)
        if form.validate_on_submit():
            try :
                with conn.cursor() as cursor:
                    query = f"SELECT * FROM user WHERE username = '{username}' OR email='{email}'"
                    cursor.execute(query)
                    account=cursor.fetchone()
                    conn.close()
                    if account:
                        flash("Username or Email already exists")
                        print("check 1")
                    elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                        flash("Invalid email address")
                        print("check 2")
                    elif not re.match(r'[A-Za-z0-9]+', username):
                        flash("Username must contain only characters and numbers !")
                        print("check 3")
                    elif not username or not password or not email or not first_name or not last_name or not medical_number:
                        flash ("Please fill out the form !")
                        print("check 4")
                    else:
                        try :
                            with con.cursor() as cur:
                                hashed_pw_user = str(bcrypt.generate_password_hash(password))
                                print(hashed_pw_user)
                                pw = hashed_pw_user.strip("b'")
                                print(pw)
                                cur.execute('INSERT INTO user VALUES(NULL, %s, %s, %s, %s, %s, %s, %s, %s);', (first_name, last_name, email, username, pw, medical_number, 'dafault_photo_profile.png', False ))
                                print("check insert data")
                                con.commit()
                                print("check commit")
                                msg = Message("Qardiosis verification code",sender = 'qardiosis@gmail.com', recipients = [email])
                                msg.body = "Your Qardiosis Verification Code " + str(otp) + "\n\nJANGAN BERITAHU KODE RAHASIA INI KE SIAPAPUN termasuk pihak Qardiosis."
                                mail.send(msg)
                                return redirect(url_for('validate'))
                        except Exception as e :
                            print(e)
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)
    return render_template("register.html", form=form)

@app.route('/validate', methods=['GET', 'POST'])
def validate():
    user_otp = request.form.get('otp')
    print(user_otp)
    con = conf()
    if request.method == 'POST':
        if otp == int(user_otp):
            try :
                with con.cursor() as cur:
                    cur.execute('UPDATE user SET state=% s ORDER BY id DESC LIMIT 1;', (True))
                    con.commit()
                    return """
                    <div class="text-center">
                            Email  verification is  successful, please click <a class="small loginlink" href="/">this link</a> to login
                    </div>
                    """
            except Exception as e:
                print(e)
        else:
            flash("Failure, OTP does not match")
    return render_template('verify.html')

@app.route('/reset', methods=['GET', 'POST'])
def reset():
    try:
        form = ResetPassword()
        conn = conf()
        con = conf()
        email = form.email.data
        new_password = form.new_password.data
        confirm_password = form.confirm_password.data
        if form.validate_on_submit():
            try:
                with conn.cursor() as cursor:
                    query = f"SELECT * FROM user WHERE email = '{email}'"
                    cursor.execute(query)
                    account=cursor.fetchone()
                    conn.close()
                    if account:
                        try :
                            if new_password == confirm_password:
                                try:
                                    with con.cursor() as cur:
                                        hashed_pw_user = bcrypt.generate_password_hash(confirm_password)
                                        cur.execute('UPDATE user SET password=% s WHERE email=% s', (hashed_pw_user, email, ))
                                        con.commit()
                                        flash("Your password has been changed !")
                                        return redirect(url_for('reset'))
                                except Exception as e :
                                    print(e)
                            else:
                                flash("Password not valid. Please try again !")
                                return redirect(url_for('reset'))
                        except Exception as e :
                            print(e)
                    else:
                        flash("Invalid email address.")
                        return redirect(url_for('reset'))
            except Exception as e:
                print(e)
        return render_template('resetpassword.html', form=form)
    except Exception as e :
        return "error"

## Define first name ##
def user():
    try:
        con = conf()
        print("Check username")
        try :
            if 'id' in session:
                id = session['id']
                print("id username" + str(id))
                with con.cursor() as cur:
                    cur.execute('SELECT first_name, img_profile FROM user WHERE id=% s', (id,))
                    data = cur.fetchone()
                    print("username data" + str(data))
                    return data
        except Exception as e:
            print(e)
    except Exception as e:
        print(e)


### Dashboard View ###
@app.route('/home')
def home():
    con = conf()
    date = ''
    anomaly_hc=''
    anomaly_dc=''
    anomaly_mi=''
    anomaly_nc=''
    total=''
    link = ''
    name = ''
    arv = ''
    user_data = user()
    if session.get('id') != None :
        id = session['id']
        print(id)
        date = datetime.now()
        date = date.strftime("%A, %d %B %Y")
        print(date)
        name = user_data[0].capitalize()
        print(name)
        photo = user_data[1]
        print(photo)
        link = 'https://storage.cloud.google.com/{}/{}'.format(bucket_name, photo)
        try:
            with con.cursor() as cur:
                cur.execute("select COUNT(anomaly) from data WHERE anomaly=' Dilated Cardiomyopathy' AND user_id=% s AND state=% s;", (id, True ))
                dc = cur.fetchall()
                print("check dc")
                anomaly_dc = dc[0][0]
                cur.execute("select COUNT(anomaly) from data WHERE anomaly='Normal' AND user_id=% s AND state=% s;", (id,True ))
                nc = cur.fetchall()
                print(nc)
                anomaly_nc = nc[0][0]
                cur.execute("select COUNT(anomaly) from data WHERE anomaly='Hypertrophic Cardiomyopathy' AND user_id=% s AND state=% s;", (id,True ))
                hc = cur.fetchall()
                anomaly_hc = hc[0][0]
                cur.execute("select COUNT(anomaly) from data WHERE anomaly='Myocardial Infarction' AND user_id=% s AND state=% s;", (id,True ))
                mi = cur.fetchall()
                anomaly_mi = mi[0][0]
                cur.execute("select COUNT(anomaly) from data WHERE 'anomaly= Abnormal Right Ventricle' AND user_id=% s AND state=% s;", (id, True ))
                arv = cur.fetchall()
                arv = arv[0][0]
                cur.execute("select COUNT(*) from data WHERE user_id=% s AND state=% s;", (id, True ))
                total = cur.fetchall()
                total = total[0][0]
        except Exception as e :
            print (e)
    else:
        flash(u"Can't display the page. You have to login first", "Error")
    return render_template("index.html", name=name, datetime=date, nc=anomaly_nc, hc=anomaly_hc, dc=anomaly_dc, mi=anomaly_mi, arv=arv, total=total, link=link)


def id_patient(user_id, birthdate):
    try:
        con = conf()
        with con.cursor() as cur:
            cur.execute('SELECT id FROM data')
            total = len(cur.fetchall())
            con.close()
            print(total)
            i = 1
            idpatient = i + total
            datebirth = birthdate.strftime("%d%m%Y")
            id_patient = str(user_id) + str(datebirth) + str(idpatient)
            print("id patient" + id_patient)
            return id_patient
    except Exception as e:
        print(e)
        print("Cannot get id_patient")

# ##############
def upload_to_storage(blob_name, file_path, bucket_name):
    # Trying upload image to google cloud storage
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(str(blob_name))
        blob.upload_from_filename(file_path)

        print('success')
        print(blob)
        return blob
    except Exception as e:
        print('can\'t upload to cloud storage')
        print(e)
        return('error')

def download_from_storage(blob_name, file_path, bucket_name):
    try:
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(str(blob_name))
        blob.download_to_filename(file_path)
        print(
            "Blob {} downloaded to file path {}. successfully ".format(
                blob, file_path
            )
        )
        print('success')
        return blob
    except Exception as e:
        print('can\'t download from cloud storage')
        print(e)
        return ('error')
# ###############


@app.route("/upload")
def upload():
    name = ''
    data = ''
    link = ''
    if session.get('id') != None :
        id = session['id']
        if request.method == 'GET':
            try:
                user_data = user()
                name = user_data[0].capitalize()
                photo = user_data[1]
                link = 'https://storage.cloud.google.com/{}/{}'.format(bucket_name, photo)
                data=[{'gender':'Male'}, {'gender':'Female'}]
                print(data)
            except Exception as e:
                print(e)
    else:
        flash(u"Can't display the page. You have to login first", "Error")
    return render_template('uploadfiles.html', name=name, gender=data, link=link)



@app.route("/upload/#", methods=['POST'])
def data_patient():
    try:
        con = conf()
        if session.get('id') != None:
            id = session['id']
            if request.method == 'POST':
                try:
                    patient_name = request.form.get('patient_name')
                    gender = request.form.get('gender_select')
                    patient_weight = int(request.form.get('patient_weight'))
                    patient_height = int(request.form.get('patient_height'))
                    patient_birth = datetime.strptime(request.form.get('patient_birth'), '%Y-%m-%d')
                    check_date = request.form.get('patient_check_date')
                    hospital_name = request.form.get('hospital')
                    upload_date = datetime.now()
                    today = date.today()
                    patient_age = today.year - patient_birth.year - ((today.month, today.day) < (patient_birth.month, patient_birth.day))
                    patient_bsa = float((pow((patient_weight), 0.425) * pow((patient_height), 0.725) * 0.007184))
                    patient_id = id_patient(id, patient_birth)

                    with con.cursor() as cur:
                        cur.execute('INSERT INTO data VALUES (NULL,% s,% s, % s, % s, % s, % s, % s, % s, % s, % s, % s, % s, % s, % s, % s, % s, % s, % s, % s)', (id, patient_name,patient_id,upload_date,check_date,gender,patient_age,patient_bsa,'',hospital_name,'','',0,0,0,0,0,0,False))
                        con.commit()
                        con.close()
                        print("Success to add data to database")
                except Exception as e:
                    print (e)
            return ('', 204)
    except Exception as e:
        print(e)


###################
@app.route('/upload/##', methods=['POST'])
def uploadimage():
    try:
        filename = ''
        con = conf()
        dt = datetime.now()
        ts = dt.timestamp()
        directory = '1'+'_qardiosis_'+str(ts)
        # parent_dir = app.config['UPLOAD_FOLDER']
        # path_dir = os.path.join(parent_dir, directory)
        if session.get('id') != None:
            id = session['id']
            if request.method == 'POST':
                try:
                    files = request.files.getlist('files')
                    print(files)
                    try:
                        file_image = []
                        for file in files:
                            if file:
                                try:
                                    filename = secure_filename(file.filename)
                                    extension = filename.rsplit('.', 1)[1]
                                    if extension not in app.config['UPLOAD_EXTENSIONS']:
                                        print('File extension not allowed')
                                    else:
                                        dt = datetime.now()
                                        ts = dt.timestamp()
                                        image_name = str(id) +'_qardiosis_'+str(ts)
                                        print("file kamu nii ya :" + filename)
                                        image1 = image_name +'.'+ 'png'
                                        image2 = image_name + 'GT' +'.'+'png'
                                        print("ini nama image file nifti kamu" + image1)
                                        print("Ini nama image file nifti kamu" + image2)
                                        file_image.append(filename)
                                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                                        print("Image berhasil di save ke path patient 101")
                                except Exception as e:
                                    print(e)
                            else:
                                print("bad request")
                        ##Machine learning
                        start_time_global = time.time()
                        start_time_1 = time.time()
                        execute()
                        end_time_1 = time.time()
                        start_time_2 = time.time()
                        execute_generate_features_test()
                        end_time_2 = time.time()
                        start_time_3 = time.time()
                        diagnosis_stage_1()
                        end_time_3 = time.time()
                        make_4D_raw()
                        print("4D figure has been created...")
                        make_4D_GT()
                        print("4D GT figure has been created...")

                        data = take_data()
                        print("execute() run in %s seconds ---" % (end_time_1 - start_time_1))
                        print("execute_generate_features_test() run in %s seconds ---" % (end_time_2 - start_time_2))
                        print("diagnosis_stage_1() run in %s seconds ---" % (end_time_3 - start_time_3))
                        print("--- %s seconds ---" % (time.time() - start_time_global))
                        print("ini hasilnya")
                        print(data)
                        old_image1 = './image_figure/my_plot_4D.png'
                        old_image2 = './image_figure/my_plot_4D_GT.png'
                        new_image1 = f'./image_figure/{image1}'
                        new_image2 = f'./image_figure/{image2}'
                        os.rename(old_image1, new_image1)
                        os.rename(old_image2, new_image2)
                        print("berhasil merubah nama file")
                        upload_to_storage(image1, new_image1, bucket_name)
                        upload_to_storage(image2, new_image2, bucket_name)
                        print("berhasil upload ke storage")
                        with con.cursor() as cur:
                            cur.execute('UPDATE data SET anomaly=%s, img_result1=%s, img_result2=%s, ed_lv=%s, es_lv=%s, ed_rv=%s, es_rv=%s, ed_lvrv=%s, es_lvrv=%s WHERE user_id=% s ORDER BY id DESC LIMIT 1', (data['GROUP'],image1,image2,data['ED[vol(LV)]'],data['ES[vol(LV)]'],data['ED[vol(RV)]'],data['ES[vol(RV)]'],data['ED[vol(LV)/vol(RV)]'],data['ES[vol(LV)/vol(RV)]'], id, ))
                            con.commit()
                            print("berhasil menambahakan data ML ke db")
                        delete_nifty_input()
                    except Exception as e:
                        print(e)
                except Exception as e:
                    print(e)
        return redirect(url_for('result'))
    except:
        return "You have to login first"

@app.route('/upload/##', methods=['GET'])
def submit_image():
    return ('', 204)

@app.route('/view/result', methods=['GET', 'POST'])
def result():
    try:
        img = user()
        data = ''
        link_src = ''
        link = ''
        name = ''
        anomaly = ''
        src2 =''
        print(img)
        name = img[0]
        photo = img[1]
        print("link foto " + photo)
        link = 'https://storage.cloud.google.com/{}/{}'.format(bucket_name, photo)
        con = conf()
        if session.get('id') != None:
            id = session['id']
            if request.method == 'GET':
                try:
                    with con.cursor() as cur:
                        cur.execute('SELECT * FROM data WHERE user_id=% s ORDER BY id DESC LIMIT 1', (id, ))
                        data = cur.fetchall()
                        print(data)
                        con.close()
                        link_src = 'https://storage.cloud.google.com/{}/{}'.format(bucket_name, data[0][11])
                        src2 = 'https://storage.cloud.google.com/{}/{}'.format(bucket_name, data[0][12])
                        anomaly = data[0][9]
                        print(anomaly)
                        print(link_src)
                        print("Link source image " + link_src)
                except Exception as e:
                    print(e)
            if request.method == 'POST':
                try:
                    with con.cursor() as cur:
                        cur.execute('UPDATE data SET state=% s WHERE user_id=% s ORDER BY id DESC LIMIT 1', (True, id, ))
                        con.commit()
                        print("berhasil update state")
                    return '', 204
                except Exception as e:
                    print(e)
    except Exception as e:
        flash(u"Can't display the page. You have to login first", "Error")
    return render_template('viewimage.html', link_src=link_src, link=link, data=data, name=name, anomaly = anomaly, src2=src2)

@app.route('/view/finish', methods=['GET', 'POST'])
def finish():
    try:
        if request.method == 'POST':
            if request.form.get('OK') == 'done':
                return redirect(url_for('upload'))
        return ('', 204)
    except:
        return "You have to login first"

@app.route("/history")
def history():
    data = ''
    name = ''
    link = ''
    if session.get('id') != None:
            id = session['id']
            user_data = user()
            name = user_data[0].capitalize()
            photo = user_data[1]
            con = conf()
            link = 'https://storage.cloud.google.com/{}/{}'.format(bucket_name, photo)
            if request.method == 'GET':
                try:
                    with con.cursor() as cur:
                        cur.execute('SELECT * FROM data WHERE user_id=% s AND state=% s', (id, True))
                        data = cur.fetchall()
                        print(data)
                except Exception as e:
                    print(e)
    else :
        flash(u"Can't display the page. You have to login first", "Error") 
    return render_template("history.html", data=data, name=name, link=link)

@app.route("/history/delete/<int:id_patient>", methods=['GET', 'POST'])
def delete_data(id_patient):
    con = conf()
    with con.cursor() as cur:
        cur.execute('DELETE FROM data WHERE id= %s', (id_patient, ))
        con.commit()
        con.close()
        print('successfully deleted data')
        return redirect(url_for('history'))

## Download History ##
@app.route('/history/view/<int:id_patient>', methods=['GET'])
def download_data(id_patient):
    con = conf()
    with con.cursor() as cur:
        cur.execute('SELECT img_result1 FROM data WHERE id= %s', (id_patient, ))
        url_img = cur.fetchall()[0][0]
        print(url_img)
        url_img = f"https://storage.cloud.google.com/{bucket_name}/{url_img}"
        print("itu url img kamu" + url_img)
        con.close()
    return render_template("image.html", url_img=url_img)

@app.route("/setting")
def setting():
    name = ''
    profile = ''
    link = ''
    if session.get('id') != None:
        id = session['id']
        user_data = user()
        name = user_data[0].capitalize()
        con = conf()
        if request.method == 'GET':
            try:
                with con.cursor() as cur:
                    cur.execute('SELECT * FROM user WHERE id=%s', (id, ))
                    profile = cur.fetchall()
                    print(profile)
                    con.close()
                    photo_profile = profile[0][7]
                    print("your photo url"+photo_profile)
                    link = 'https://storage.cloud.google.com/{}/{}'.format(bucket_name, photo_profile)
            except Exception as e:
                print(e)
    else:
        flash(u"You have to login first", "Error") 
    return render_template("setting.html", name=name, profile=profile, link=link)

@app.route("/setting/#", methods=['GET', 'POST'])
def edit_setting():
    con = conf()
    if request.method == 'POST' and session.get('id') != None:
        id = session['id']
        try:
            photo_profile = request.files['pic']
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            email = request.form.get('email')
            user_name = request.form.get('user_name')
            medical_number = request.form.get('medical_number')
            curr_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            conf_new_pass = request.form.get('confirm_new_password')
            if first_name != '':
                with con.cursor() as cur:
                    cur.execute('UPDATE user SET first_name=% s WHERE id=% s', (first_name, id, ))
                    con.commit()
                    print('Success to update first name')
            if last_name != '':
                with con.cursor() as cur:
                    cur.execute('UPDATE user SET last_name=% s WHERE id=% s', (last_name, id, ))
                    con.commit()
                    print('Success to update last name')
            if email != '':
                with con.cursor() as cur:
                    cur.execute('UPDATE user SET email=% s WHERE id=% s', (email, id, ))
                    con.commit()
                    print('Success to update email')
            if user_name != '':
                with con.cursor() as cur:
                    cur.execute('UPDATE user SET username=% s WHERE id=% s', (user_name, id, ))
                    con.commit()
                    print('Success to update Username')
            if medical_number != '':
                with con.cursor() as cur:
                    cur.execute('UPDATE user SET medical_number=% s WHERE id=% s', (medical_number, id, ))
                    con.commit()
                    print('Success to update medical number')
            if conf_new_pass != '' and curr_password and conf_new_pass == new_password :
                with con.cursor() as cur:
                    hashed_pw_user = bcrypt.generate_password_hash(conf_new_pass)
                    cur.execute('UPDATE user SET password=% s WHERE id=% s', (hashed_pw_user, id, ))
                    con.commit()
                    print('Success to update password')
            if photo_profile:
                try:
                    filename = secure_filename(photo_profile.filename)
                    extension = filename.rsplit('.', 1)[1]
                    if filename:
                        dt = datetime.now()
                        ts = dt.timestamp()
                        image = str(id) + '_photo_profile_'+ str(ts) + '.' + extension
                        photo_profile.save(os.path.join(app.config['UPLOAD_FOLDER'], image))
                        path_im = './testing/testing2/patient071/' + image
                        print("berhasil upload id file uploads")
                        upload_to_storage(image, path_im, bucket_name)
                        with con.cursor() as cur:
                            cur.execute('UPDATE user SET img_profile=% s WHERE  id=% s', (image, id, ))
                            con.commit()
                            print('Berhasil update image profile')
                        os.remove(path_im)
                        return redirect(url_for('setting'))
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)
    return ('', 204)
    
@app.route("/logout")
def logout():
    try :
        session.pop('logged in', None)
        session.pop('id', None)
        session.pop('username', None)
        return redirect(url_for('login'))
    except Exception as e:
        print(e)
    

def get_all_file_paths(directory):
    file_paths = []
    for root, directories, files in os.walk(directory):
        for filename in files:
            print("Ini root" + root)
            filepath = os.path.join(root, filename)
            print("Ini file path si image" + filepath)
            print(file_paths)
            file_paths.append(filepath)
            
    return file_paths



if __name__ == '__main__':
    app.run(debug=True, threaded=True)
