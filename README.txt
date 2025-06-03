""""CARA MENGIMPORT SOURCE CODE KE DALAM GOOGLE CLOUD PLATFORM (GCP)""""

1. Upload Source Code Ke Git atau GitHub
2. Buka Akun GCP, lalu buka Cloud Shell pada Console GCP
3. Cloning project atau repository yang telah diupload di GitHub menggunakan command :
	git clone LINK_REPOSITORY
4. Terlebih dahulu membuat Cloud SQL dan database dengan tabel yang ada pada file "qardiosis_db_user" dan "qardiosis_db_data"
5. Lalu buat bucket pada Cloud Storage
6. Masukkan nama database server dan nama bucket didalam app.yaml, pada bagian :
	env_variables:
  		CLOUD_SQL_USERNAME: 'username_db'
  		CLOUD_SQL_PASSWORD: 'password_db'
  		CLOUD_SQL_DATABASE_NAME: 'database_name'
  		CLOUD_SQL_CONNECTION_NAME: 'connection_name_db'
  		CLOUD_STORAGE_BUCKET_NAME: 'bucket_name'
7. Setelah app.yaml selesai dikonfigurasi, pergi ke direktori project yang sudah dicloning dalam cloud shell menggunakan command :
	cd NAMA_DIRECTORY_PROJECT
8. Deploy aplikasi dengan menggunakan command:
	gcloud app deploy
9. Setelah selesai proses deploy pada Google App Engine, maka link aplikasi dapat diakses dengan command:
	gcloud app browse
