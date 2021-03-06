<h1 align="center">Docker-runner API</h1>

![Image alt](image/arhitecture.png)

---
**A small python-flask API for managing docker containers at local machine.**

# Description
With this app you can manage docker containers from config.json file. Main page hosts on /docker-api/apps path. App has a simple UI, where you can add new docker, edit and delete it. 
All local ports for running docker containers takes from url in config file.
App control your local ports and path to dockers and give a massage if it will be wrong.
Also, you can edit directly config.json file and then put to "Update config" link at main page. In that case, the app check url and path to docker for all containers and doesn't run wrong one.


# Installation features

1. Copy API from repository;
2. Install all requirements apps from requirements.txt `/Docker_app$ pip install -r requirements.txt `
3. Run app by `/Docker_app$ python docker_api/app.py`
4. Main page at http://localhost:5000/docker-api/apps

## Required python v3 and more:

1. Flask for python;
2. Docker for python;
3. Admin(superuser) permission for your user.

# Instruction to use:

API have GUI and you can use any browser to use it.
Also below you can see how to use the application from the command line.

## 1. Main page with running dockers.

http://localhost:5000/docker-api/apps  
`curl http://localhost:5000/docker-api/apps`

This command start all apps from config file. If some docker have errors in path or urls, app doesnt start it.

## 2. Start new docker container.

In GUI you can push "Add app" link, fill in the fields of the proposed form and click "submit" button.
If there be some incorrect information, the docker will not be started and you received a error message.
It also update your config file.  
`curl -X POST -d "app_name=some_name&path=some_path&http_port=some_port&url=some_url" http://localhost:5000/docker-api/apps/create`

## 3. Delete docker container.

In GUI you can push "Delete app" button at the main page.  
`curl -X POST http://localhost:5000/docker-api/apps/<app_id>/delete`

## 4. Update information about docker container.

In GUI you can push "Change config" link, fill in the fields of the proposed form and click "submit" button.
If there be some incorrect information, the docker will not be started and you received a error message.
But app always stops the initial application.  
`curl -X POST -d "app_name=some_name&path=some_path&http_port=some_port&url=some_url" http://localhost:5000/docker-api/apps/<app_id>/edit`

## 5. Update all docker-containers according to config file.

In GUI you can push "Restart containers according to config" link.
It stops all active dockers and start all dockers from config file. If there is some incorrect information in config file, app doesnt start wrong one, but you almost can see that app in list at main page.
Than, you can edit the wrong app and it will be work fine.
After using this function, you need to wait until all the containers start working.  
`curl -X GET http://localhost:5000/docker-api/apps/update`

## 6. Stop all docker-containers.

In GUI you can push "Stop apps" link, it stops all active dockers.
We recommend use it before you stop the application.  
`curl -X GET http://localhost:5000/docker-api/apps/stop_all`

