import os
import json
import docker.errors

from flask import Flask, abort, request, render_template, url_for, flash, redirect, get_flashed_messages

from key import SECRET_KEY

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
client = docker.from_env()
active_apps = {}


def _start_apps(list_of_apps: list):
    """Run all dockers from list_of_apps"""
    for app in list_of_apps:
        active_apps[app['id']] = client.containers.run(
            app['path'], detach=True, ports={f"{app['http_port']}/tcp": app['url'][app['url'].find('st:')+3:]}
        )


def _stop_apps(list_of_apps: list):
    """Stop all dockers from list_of_apps"""
    for app in list_of_apps:
        active_apps[app['id']].stop()
        del active_apps[app['id']]


def _update_config(path: str, obj=None, operation=None):
    """Update or read your config file"""
    if operation == 'r':
        with open(path, 'r') as f:
            result = json.load(f)
        return result
    with open(path, 'w') as f:
        json.dump(obj, f)


def _check_path_errors_and_launch(list_of_dockers: list):
    """Check all path, and doesnt run wrong one"""
    error = False
    for index, app in enumerate(list_of_dockers):
        try:
            _start_apps([app])
        except docker.errors.ImageNotFound:
            flash(f"You give wrong path to docker {app['app_name']}!")
            error = True
    return error


@app.before_first_request
def start_api():
    """Run all dockers at start of app"""
    global docker_apps, timestamp
    timestamp = os.stat('docker_api/config.json').st_mtime
    docker_apps = _update_config('docker_api/config.json', operation='r')
    if docker_apps['apps']:
        _check_path_errors_and_launch(docker_apps['apps'])


@app.route('/')
def index():
    return redirect(url_for('get_apps'))


@app.route('/docker-api/apps', methods=['GET'])
def get_apps():
    return render_template("apps_page.html", docker_apps=docker_apps['apps'])


@app.route('/docker-api/apps/update', methods=['GET'])
def update_config_changes():
    """Republication of docker containers according to config file, if it was changed"""
    global docker_apps, timestamp
    if timestamp != os.stat('docker_api/config.json').st_mtime:
        timestamp = os.stat('docker_api/config.json').st_mtime
        if docker_apps['apps']:
            _stop_apps(docker_apps['apps'])
        docker_apps = _update_config('docker_api/config.json', operation='r')
        _check_path_errors_and_launch(docker_apps['apps'])
    return redirect(url_for('get_apps'))


@app.route('/docker-api/apps/create', methods=['GET', 'POST'])
def create_app():
    """Create new docker container and run it"""
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
            if not _check_path_errors_and_launch([docker_app]):
                docker_apps['apps'].append(docker_app)
                _update_config("docker_api/config.json", docker_apps)
                return redirect(url_for('get_apps'))
    return render_template('create.html')


@app.route('/docker-api/apps/<int:app_id>/edit', methods=['GET', 'POST'])
def update_app(app_id):
    """Change docker container config and get republication of it"""
    global docker_apps
    docker_app = list(filter(lambda x: x['id'] == app_id, docker_apps['apps']))
    if request.method == 'POST':
        docker_app[0]['app_name'] = request.form['app_name']
        docker_app[0]['path'] = request.form['path']
        docker_app[0]['http_port'] = request.form['http_port']
        docker_app[0]['url'] = request.form['url']
        if not all(docker_app[0].values()):
            flash('All attributes are required!')
        else:
            if docker_app[0]['id'] in active_apps:
                _stop_apps(docker_app)
            if not _check_path_errors_and_launch(docker_app):
                for index, app in enumerate(docker_apps['apps']):
                    if app['id'] == docker_app[0]['id']:
                        docker_apps['apps'][index] = docker_app[0]
                _update_config("docker_api/config.json", docker_apps)
                flash('Your changes have been saved successfully')
                return render_template("apps_page.html", docker_apps=docker_apps['apps'])
    return render_template('config_corr.html', docker_app=docker_app)


@app.route('/docker-api/apps/<int:app_id>/delete', methods=['POST'])
def del_app(app_id):
    """Stop docker file and delete it from config"""
    docker_app = list(filter(lambda x: x['id'] == app_id, docker_apps['apps']))
    if len(docker_app) == 0:
        abort(404)
    docker_apps['apps'].remove(docker_app[0])
    _update_config("docker_api/config.json", docker_apps)
    _stop_apps(docker_app)
    return render_template("apps_page.html", docker_apps=docker_apps['apps'])


if __name__ == '__main__':
    app.run(debug=True, testing=True)
