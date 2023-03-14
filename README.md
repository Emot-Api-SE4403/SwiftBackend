
# Swift E-Learning Backend Service

Sebuah server backend yang didukung oleh FastApi untuk Swift e-Learning





## Menjalankan Secara Lokal

Klon repositori

```bash
  git clone https://github.com/Emot-Api-SE4403/SwiftBackend.git
```

Buka direktori proyek

```bash
  cd SwiftBackend
```

Instal MySQL


Terdapat dua pilihan untuk menginstal MySQL. Anda dapat menggunakan Docker atau XAMPP.
- Untuk menginstal MySQL menggunakan Docker, ikuti langkah-langkah yang disebutkan dalam [dokumentasi resmi.](https://hub.docker.com/_/mysql)

- Untuk menginstal MySQL menggunakan XAMPP, [unduh dan instal XAMPP](https://www.apachefriends.org/download.html). Setelah diinstal, mulai server MySQL dari panel kontrol XAMPP

Instal kebutuhan

```bash
  pip install -r requirements.txt
```

Mulai server

```bash
  uvicorn main:app --reload
```


## Environment Variables

Untuk menjalankan proyek ini, Anda perlu menambahkan variabel lingkungan berikut ke file .env Anda

`SECRET_KEY_AUTH`

`SQL_DATABASE_URL`


## Dokumentasi API

Jika Anda ingin melihat dokumentasi API, buka
```http
    http://localhost:8000/docs 
```
atau
```http 
    http://localhost:8000/redoc 
```
di browser web Anda. Ini akan menampilkan halaman Swagger UI dan ReDoc documentation.
