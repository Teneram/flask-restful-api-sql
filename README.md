Core: 
[![Python](https://img.shields.io/badge/python-3.10-green?logo=python)](https://www.python.org/downloads/release/python-3100/)
[![Flask](https://img.shields.io/badge/Flask-2.2.3-blue.svg?logo=flask)](https://flask.palletsprojects.com/en/2.2.x/)
![REST API](https://img.shields.io/badge/REST%20API-Active-brightgreen)
[![Swagger](https://img.shields.io/badge/Swagger-OpenAPI-blue.svg?logo=swagger)](https://swagger.io/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-v2.0.4-16er6e.svg?style=plastic)](https://www.sqlalchemy.org/)
[![Docker](https://img.shields.io/badge/Docker-20.10.8-blue.svg?logo=docker)](https://www.docker.com/)
[![My CLI App built with Typer](https://img.shields.io/badge/My%20CLI%20App-Typer-4B0082)](https://typer.tiangolo.com/)

Code style:
[![Flake8](https://img.shields.io/badge/flake8-6.0.0-red.svg)](https://flake8.pycqa.org/en/6.0.0/)
[![mypy](https://img.shields.io/badge/mypy-1.0.1-blue.svg)](https://mypy.readthedocs.io/en/stable/getting_started.html)
[![isort](https://img.shields.io/badge/isort-5.12.0-green.svg)](https://pypi.org/project/isort/)
[![Black Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://black.readthedocs.io/en/stable/getting_started.html)

# Flask RESTful API with SQL

---

Application allows you set up database with students, courses and groups.
Optionally you will be able to use random generation as an example which provide you with data 
for 200 students with allocation to groups and courses.

Also application provides you ability to:
- Retrieve information about all students/courses/groups;
- Retrieve detailed information about particular students/courses/groups by its ID;
- Add a new student;
- Update student data (assign to new course/change name);
- Delete random course of a student;
- Delete student by ID.

## Requirements

  * Python 3.10

## Local development requirements

Application use Docker containerization. To start using it make sure you have [Docker](https://docs.docker.com/get-docker/) installed on your PC.

## Build and Run

To start working with an application you can use next Make commands:

    $ make build                      # to create Docker containers 
    $ make create_db_with_test_data   # to create database with test data
    $ make start                      # to start conteiners
    $ make createDB                   # to create database 
    $ make fillDB                     # to fill database with test data
    $ make flake8                     # to check code by flake8
    $ make mypy                       # to check code by mypy 
    $ make isort                      # to check code by isort 
    $ make test                       # to run tests

## License
[MIT](https://choosealicense.com/licenses/mit/)