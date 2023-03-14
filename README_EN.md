
# Swift E-Learning Backend Service

A FastApi powered backend server for Swift e-Learning





## Run Locally

Clone the project

```bash
  git clone https://github.com/Emot-Api-SE4403/SwiftBackend.git
```

Go to the project directory

```bash
  cd SwiftBackend
```

Install MySQL


There are two options to install MySQL. You can either use Docker or XAMPP.
- To install MySQL using Docker, follow the steps mentioned in the official documentation.

- To install MySQL using XAMPP, download and install XAMPP. Once installed, start the MySQL server from the XAMPP control panel.

Install requirements

```bash
  pip install -r requirements.txt
```

Start the server

```bash
  uvicorn main:app --reload
```


## API documentation

If you want to see the API documentation, open 
```http
    http://localhost:8000/docs 
```
or
```http 
    http://localhost:8000/redoc 
```
in your web browser. This will show you the Swagger UI and ReDoc documentation pages respectively.
