# app
 
Requirements

Django 1.9.1

PostgreSQL 9.1

Python2.7

Procedure

Clone this repository and then

First install a virtual environment with command

    $ virtualenv testenv 
    
    $ source testenv/bin/activate
    
    $ pip install -r requirements.txt
    
Just do migration for the app from project root.

    $ python manage.py migrate
    
    $ python manage.py createsuperuser
   
after that run server locally with following command

   $ python manage.py runserver 0.0.0.0:8000
