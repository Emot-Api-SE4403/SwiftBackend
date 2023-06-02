
# Swift E-Learning Backend Service

[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=Emot-Api-SE4403_SwiftBackend&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=Emot-Api-SE4403_SwiftBackend)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Emot-Api-SE4403_SwiftBackend&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=Emot-Api-SE4403_SwiftBackend)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=Emot-Api-SE4403_SwiftBackend&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=Emot-Api-SE4403_SwiftBackend)
![CodeQL](https://github.com/Emot-Api-SE4403/SwiftBackend/actions/workflows/github-code-scanning/codeql/badge.svg)
![CI Status](https://github.com/Emot-Api-SE4403/SwiftBackend/actions/workflows/ci.yaml/badge.svg)

#### Sebuah server backend yang didukung oleh FastApi untuk Swift e-Learning. 


## Dokumentasi API

Jika Anda ingin melihat dokumentasi API, buka
```bash
    http://localhost:8000/docs
```
atau
```bash
    http://localhost:8000/redoc 
```
di browser web Anda. Ini akan menampilkan halaman Swagger UI dan ReDoc documentation.



## Menjalankan Secara Lokal

### Klon repositori

```bash
  git clone https://github.com/Emot-Api-SE4403/SwiftBackend.git
```

### Buka direktori proyek

```bash
  cd SwiftBackend
```

### Instal kebutuhan

```bash
  pip install -r requirements.txt
```

### Buat file variabel lingkungan `.env` 
lihat <a href="#environment-variables">#environment-variables</a>

### Mulai server

```bash
  uvicorn main:app --reload
```


## Environment Variables

Untuk menjalankan proyek ini, Anda perlu menambahkan variabel lingkungan berikut ke file .env Anda


- `SECRET_KEY_AUTH` database encription key, generate menggunakan ``openssl rand -hex 32``
- `S3_ACCESS_KEY` s3/secret/access/application key
- `S3_KEY_ID` id of your s3 key
- `S3_URL` s3 url
- `EMAIL_API_KEY_PUBLIC` mailjet public api key 
- `EMAIL_API_KEY_PRIVATE` mailjet private api key 
- `MY_EMAIL` email used in mailjet
- `SQL_DATABASE_URL` database url string, example ``mysql+mysqldb://root@localhost:3306/test?charset=utf8``
- `DOMAIN` Your backend domain, example ``http://localhost:8000``
