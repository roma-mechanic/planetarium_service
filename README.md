# Planetarium-service API
Django-RESt project for reservation tickets for astronomic show in Planetarium service. 

## Planetarium-service can be downloaded from:
[from git hub pull here](https://github.com/roma-mechanic/planetarium_service)

## Installation

Python must be already installed


```bash
git clone https://github.com/roma-mechanic/planetarium_service
cd Planetarium-Service
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
```
Fill in the .env file with user data according to the .env_sample file

```bash
python manage.py runserver
```

### How to run with Docker:

Important ! Docker must be already installed

- Fill in the .env file with user data according to the .env_sample file.
```bash
docker-compose up --build
```
- Create admin user.
- Create / get JWT-token and authorization.
- Use planetarium-service application.

## Project scheme

![Project scheme](/static/images/Planetarium_show.drawio.svg)

## Demo swagger scheme endpoints
![Demo swagger scheme endpoints](/static/images/swagger_scheme_API.png)

