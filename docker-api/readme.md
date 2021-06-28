<h1 align="center">Docker-runner API</h1>
**A small python-flask API for for managing docker containers at local machine.**
---

# Description
With this app you can manage docker containers from config.json file. Main page hosts on /docker-api/apps path. App has a simple UI, where you can add new docker, edit and delete it. Also, you can edit directly config.json file and then put to "Update config" link at main page.
All local ports for running docker containers takes randomly. You can show it by ```$ docker ps``` command in command line.

# Installation features

1. Copy API from repository.
2. Add key.py file with your SECRET_KEY to "docker-api" directory.
3. Run app.py

## Required python v3 and more:

1. Flask for python
2. Docker for python
3. Admin(superuser) permission for your user
