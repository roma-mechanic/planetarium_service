# Planetarium-service API
Django-RESt project for reservation tickets for astronomic show in Planetarium service. 



## Installation
Python must be already installed.\
Clone this repository to your local machine\
[Planetarium-service can be downloaded from:](https://github.com/roma-mechanic/planetarium_service)\
Or\
git clone https://github.com/roma-mechanic/planetarium_service.git

### How to run with Docker:

Important ! Docker must be already installed

- Create and fill in the .env file with user data according to the .env_sample file.
- Run app
```bash
docker-compose up --build
```
- Create admin user.
```bash
python manage.py createsuperuser
```
- Create / get JWT-token and authorization.
- Use planetarium-service application.
- All endpoints in swagger documentation 127.0.0.1.8000/api/doc/swagger/

## Project scheme

![Project scheme](/uploads/images/Planetarium_show.drawio.svg)

## Demo swagger scheme endpoints
![Demo swagger scheme endpoints](/uploads/images/swagger_scheme_API.png)

