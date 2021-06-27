import os
import json
import docker

from flask import Flask, abort, request, render_template, url_for, flash, redirect

app = Flask(__name__)
client = docker.from_env()
app.config['SECRET_KEY'] = 'Asw7we89cxhjy9'
active_apps = {}


def _start_apps(list_of_apps: list):
    for app in list_of_apps:
        active_apps[app['app_name']] = \
            client.containers.run(app['path'], detach=True, ports={f"{app['http_port']}/tcp": None})


def _stop_apps(list_of_apps: list):
    for app in list_of_apps:
        active_apps[app['app_name']].stop()
        del active_apps[app['app_name']]


def _update_config(path: str, obj):
    with open(path, 'w') as f:
        json.dump(obj, f)


@app.before_first_request
def start_api():
    global docker_apps, timestamp
    timestamp = os.stat('config.json').st_mtime
    with open('config.json', 'r') as f:
        docker_apps = json.load(f)
    if docker_apps['apps']:
        _start_apps(docker_apps['apps'])


@app.route('/')
def index():
    return redirect(url_for('get_apps'))


@app.route('/docker-api/apps', methods=['GET'])
def get_apps():
    return render_template("apps_page.html", docker_apps=docker_apps['apps'])


@app.route('/docker-api/apps/update', methods=['GET'])
def update_config():
    global docker_apps, timestamp
    if timestamp != os.stat('config.json').st_mtime:
        timestamp = os.stat('config.json').st_mtime
        _stop_apps(docker_apps['apps'])
        with open('config.json', 'r') as f:
            docker_apps = json.load(f)
        if docker_apps['apps']:
            _start_apps(docker_apps['apps'])
    return redirect(url_for('get_apps'))


@app.route('/docker-api/apps/create', methods=['GET', 'POST'])
def create_app():
    if request.method == "POST":
        docker_app = {
            "app_name": request.form["app_name"],
            "path": request.form["path"],
            "http_port": request.form["http_port"],
            "url": request.form["url"]
        }
        if docker_apps['apps']:
            docker_app['id'] = docker_apps['apps'][-1]["id"] + 1
        else:
            docker_app['id'] = 1
        if not all(docker_app.values()):
            flash("All attributes are required!")
        else:
            docker_apps['apps'].append(docker_app)
            _update_config("config.json", docker_apps)
            _start_apps([docker_app])
            return redirect(url_for('get_apps'))
    return render_template('create.html')


@app.route('/docker-api/apps/<int:app_id>/edit', methods=['GET', 'POST'])
def update_app(app_id):
    global docker_apps
    docker_app = list(filter(lambda x: x['id'] == app_id, docker_apps['apps']))
    if request.method == 'POST':
        _stop_apps(docker_app)
        docker_app[0]['app_name'] = request.form['app_name']
        docker_app[0]['path'] = request.form['path']
        docker_app[0]['http_port'] = request.form['http_port']
        docker_app[0]['url'] = request.form['url']
        if not all(docker_app[0].values()):
            flash('All attributes are required!')
        else:
            docker_apps['apps'][app_id-1] = docker_app[0]
            _update_config("config.json", docker_apps)
            _start_apps(docker_app)
            return redirect(url_for('get_apps'))
    return render_template('config_corr.html', docker_app=docker_app)


@app.route('/docker-api/apps/<int:app_id>/delete', methods=['POST'])
def del_app(app_id):
    docker_app = list(filter(lambda x: x['id'] == app_id, docker_apps['apps']))
    if len(docker_app) == 0:
        abort(404)
    docker_apps['apps'].remove(docker_app[0])
    _update_config("config.json", docker_apps)
    _stop_apps(docker_app)
    return render_template("apps_page.html", docker_apps=docker_apps['apps'])


if __name__ == '__main__':
    app.run(debug=True)
