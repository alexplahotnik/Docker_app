<h1 align="center">Docker-runner API</h1>

---
**A small python-flask API for managing docker containers at local machine.**

# Description
With this app you can manage docker containers from config.json file. Main page hosts on /docker-api/apps path. App has a simple UI, where you can add new docker, edit and delete it. 
All local ports for running docker containers takes from url in config file.
App control your local ports and path to dockers and give a massage if it will be wrong.
Also, you can edit directly config.json file and then put to "Update config" link at main page. In that case, the app check url and path to docker for all containers and doesn't run wrong one.


# Installation features

1. Copy API from repository;
2. Install all requirements apps from requirements.txt `/final_task$ pip install -r requirements.txt `
3. Run app by `/final_task$ python docker_api/app.py`
4. Main page at http://localhost:5000/docker-api/apps

## Required python v3 and more:

1. Flask for python;
2. Docker for python;
3. Admin(superuser) permission for your user.
