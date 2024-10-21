# Nameko relies on eventlet
# You should monkey patch the standard library as early as possible to avoid
# importing anything before the patch is applied.
# See http://eventlet.net/doc/patching.html#monkeypatching-the-standard-library
import json

import eventlet

eventlet.monkey_patch()  # noqa (code before rest of imports)

import pytest
import requests
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

TOXIPROXY_PROXY_NAME = 'nameko_sqlalchemy_test_mysql'


DeclarativeBase = declarative_base(name='examplebase')


class ExampleModel(DeclarativeBase):
    __tablename__ = 'example'
    id = Column(Integer, primary_key=True)
    data = Column(String(100))


@pytest.fixture
def toxiproxy(toxiproxy_api_url, toxiproxy_db_url):

    class Controller(object):
        def __init__(self, api_url):
            self.api_url = api_url

        def enable(self):
            resource = f'http://{self.api_url}/reset'
            requests.post(resource)

        def disable(self):
            resource = f'http://{self.api_url}/proxies/{TOXIPROXY_PROXY_NAME}'
            data = {
                'enabled': False
            }
            requests.post(resource, json.dumps(data))

        def reset(self):
            self.enable()

    if toxiproxy_api_url and toxiproxy_db_url:
        controller = Controller(toxiproxy_api_url)
        controller.reset()

        yield controller

        controller.reset()
    else:
        yield
