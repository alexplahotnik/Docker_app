import os
import requests as req
import time

import docker.errors
import pytest

import docker_api.app as api

with api.app.test_client() as test_client:
    def test_start_and_stop_apps_positive():
        list_of_apps = [
            {"app_name": "catnip", "path": "alexplahotnik/catnip",
             "http_port": "5000", "url": "http://localhost:5555", "id": 1},
            {"app_name": "echo-server2", "path": "jmalloc/echo-server",
             "http_port": "8080", "url": "http://localhost:44655", "id": 3}
        ]
        api._start_apps(list_of_apps)
        time.sleep(5)
        assert req.get("http://localhost:44655").status_code == 200
        assert req.get("http://localhost:5555").status_code == 200
        api._stop_apps(list_of_apps)
        with pytest.raises(req.exceptions.ConnectionError):
            req.get("http://localhost:44655").status_code


    def test_start_app_wrong_path():
        list_of_apps = [{"app_name": "catnip", "path": "alexplahotnik/catnip123",
             "http_port": "5000", "url": "http://localhost:5555", "id": 1}]
        with pytest.raises(docker.errors.ImageNotFound):
            api._start_apps(list_of_apps)


    def test_update_config():
        config = {"apps": [{"app_name": "catnip", "path": "alexplahotnik/catnip123",
                         "http_port": "5000", "url": "http://localhost:5555", "id": 1}]}
        api._update_config('tests/test_config.json', obj=config)
        assert api._update_config('tests/test_config.json', operation='r') == config
        os.remove('tests/test_config.json')


    def test_check_path_errors_and_run_positive():
        list_of_apps = [
            {"app_name": "catnip", "path": "alexplahotnik/catnip",
             "http_port": "5000", "url": "http://localhost:5555", "id": 1},
            {"app_name": "echo-server2", "path": "jmalloc/echo-server",
             "http_port": "8080", "url": "http://localhost:44655", "id": 3}
        ]
        assert not api._check_path_errors_and_launch(list_of_apps)
        time.sleep(5)
        assert req.get("http://localhost:44655").status_code == 200
        assert req.get("http://localhost:5555").status_code == 200
        api._stop_apps(list_of_apps)


    def test_check_path_errors_and_run_negative():
        list_of_apps = [
            {"app_name": "catnip", "path": "alexplahotnik/catnip2356",
             "http_port": "5000", "url": "http://localhost:5555", "id": 1},
            {"app_name": "echo-server2", "path": "jmalloc/echo-server",
             "http_port": "8080", "url": "http://localhost:44655", "id": 3}
        ]
        with api.app.test_request_context():
            assert api._check_path_errors_and_launch(list_of_apps)
        time.sleep(5)
        assert req.get("http://localhost:44655").status_code == 200
        api._stop_apps([{"app_name": "echo-server2", "path": "jmalloc/echo-server",
                         "http_port": "8080", "url": "http://localhost:44655", "id": 3}])


    def test_update_config_changes():
        api.timestamp = 1
        config = {"apps": [{"app_name": "catnip", "path": "alexplahotnik/catnip",
                            "http_port": "5000", "url": "http://localhost:5555", "id": 1},
                           {"app_name": "echo-server", "path": "jmalloc/echo-server",
                            "http_port": "8080", "url": "http://localhost:44655", "id": 4}]}
        api._update_config('docker_api/config.json', config)
        response = test_client.post('/docker-api/apps/update')
        time.sleep(5)
        assert req.get("http://localhost:44655").status_code == 200
        assert req.get("http://localhost:5555").status_code == 200


    def test_home_page_and_start_function():
        response = test_client.get('/docker-api/apps')
        time.sleep(5)
        assert response.status_code == 200
        assert b"List of docker projects" in response.data


    def test_create_get_page():
        response = test_client.get('/docker-api/apps/create')
        assert response.status_code == 200


    def test_create_post_page():
        response = test_client.post('/docker-api/apps/create', data=dict(
            app_name="catnip2", path='alexplahotnik/catnip', http_port=5000, url="http://localhost:7456"))
        time.sleep(5)
        assert req.get("http://localhost:7456").status_code == 200
        assert len(api._update_config('docker_api/config.json', operation='r')["apps"]) == 3


    def test_create_post_wrong_path():
        response = test_client.post('/docker-api/apps/create', data=dict(
            app_name="catnip3", path='alexplahotnik/catnip111', http_port=5000, url="http://localhost:6545"))
        assert len(api._update_config('docker_api/config.json', operation='r')["apps"]) == 3


    def test_update_get_page():
        response = test_client.get('/docker-api/apps/4/edit')
        assert response.status_code == 200


    def test_update_post_wrong_path():
        response = test_client.post('/docker-api/apps/4/edit', data=dict(
            app_name="echo-server-new1", path='jmalloc/echo-serer112', http_port=8080, url="http://localhost:6545"))
        with pytest.raises(req.exceptions.ConnectionError):
            req.get("http://localhost:44655").status_code
        assert api._update_config('docker_api/config.json', operation='r')["apps"][1]["app_name"] != "echo-server-new1"


    def test_update_post_page():
        response = test_client.post('/docker-api/apps/4/edit', data=dict(
            app_name="echo-server-new", path='jmalloc/echo-server', http_port=8080, url="http://localhost:6545"))
        time.sleep(5)
        assert req.get("http://localhost:6545").status_code == 200
        assert api._update_config('docker_api/config.json', operation='r')["apps"][1]["app_name"] == "echo-server-new"


    def test_del_page():
        response = test_client.post('/docker-api/apps/5/delete')
        time.sleep(5)
        with pytest.raises(req.exceptions.ConnectionError):
            req.get("http://localhost:7456").status_code
        assert len(api._update_config('docker_api/config.json', operation='r')["apps"]) == 2
        api._stop_apps(api.docker_apps["apps"])


