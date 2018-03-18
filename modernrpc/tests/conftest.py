# coding: utf-8
import pytest
from django.contrib.auth.models import Permission, Group, AnonymousUser
from jsonrpcclient import http_client as jsonrpcclient

from . import python_xmlrpc


@pytest.fixture(scope='session')
def common_pwd():
    """The default password, used to create any user"""
    return '123456789!'


@pytest.fixture(scope='session')
def anonymous_user():
    return AnonymousUser()


@pytest.fixture
def john_doe(django_user_model, common_pwd):
    """Create and return a standard Django user"""
    return django_user_model.objects.create_user('johndoe', email='jd@example.com', password=common_pwd)


@pytest.fixture
def superuser(django_user_model, common_pwd):
    """Create and return a Django superuser"""
    return django_user_model.objects.create_superuser('admin', email='admin@example.com', password=common_pwd)


@pytest.fixture
def group_A(db):
    """Return a group named 'A'. Create it if necessary"""
    group, _ = Group.objects.get_or_create(name='A')
    return group


@pytest.fixture
def group_B(db):
    """Return a group named 'B'. Create it if necessary"""
    group, _ = Group.objects.get_or_create(name='B')
    return group


@pytest.fixture
def add_user_perm():
    """Return permission 'auth.add_user'"""
    return Permission.objects.get(codename='add_user')


@pytest.fixture
def change_user_perm():
    """Return permission 'auth.change_user'"""
    return Permission.objects.get(codename='change_user')


@pytest.fixture
def delete_user_perm():
    """Return permission 'auth.delete_user'"""
    return Permission.objects.get(codename='delete_user')


@pytest.fixture(scope='session')
def live_server_url(live_server):
    """Return the url associated with unit tests Django live server"""
    return live_server.url


@pytest.fixture(scope='session')
def all_rpc_url(live_server):
    """Return the default RPC test endpoint URL. See 'testsite.urls' for additional info."""
    return live_server + '/all-rpc/'


@pytest.fixture(scope='session')
def all_rpc_doc_url(live_server):
    """Return the URL to view configured to serve RPC documentation. See 'testsite.urls' for additional info."""
    return live_server + '/all-rpc-doc/'


@pytest.fixture(scope='session')
def json_only_url(live_server):
    """Return the JSON-RPC specific endpoint URL. See 'testsite.urls' for additional info."""
    return live_server + '/json-only/'


@pytest.fixture(scope='session')
def xml_only_url(live_server):
    """Return the XML-RPC specific endpoint URL. See 'testsite.urls' for additional info."""
    return live_server + '/xml-only/'


@pytest.fixture(scope='session')
def xmlrpc_client(all_rpc_url):
    """Return the default XML-RPC client"""
    return python_xmlrpc.ServerProxy(all_rpc_url)


@pytest.fixture(scope='session')
def jsonrpc_client(all_rpc_url):
    """Return the default JSON-RPC client"""
    return jsonrpcclient.HTTPClient(all_rpc_url)


def get_url_with_auth(orig_url, username, password):
    return orig_url.replace('://', '://{uname}:{pwd}@').format(uname=username, pwd=password)


@pytest.fixture
def xmlrpc_client_as_superuser(all_rpc_url, superuser, common_pwd):
    """Return the default XML-RPC client, logged as superuser"""
    endpoint = get_url_with_auth(all_rpc_url, superuser.username, common_pwd)
    return python_xmlrpc.ServerProxy(endpoint)


@pytest.fixture
def jsonrpc_client_as_superuser(all_rpc_url, superuser, common_pwd):
    """Return the default JSON-RPC client, logged as superuser"""
    endpoint = get_url_with_auth(all_rpc_url, superuser.username, common_pwd)
    return jsonrpcclient.HTTPClient(endpoint)


@pytest.fixture
def xmlrpc_client_as_user(all_rpc_url, john_doe, common_pwd):
    """Return the default XML-RPC client, logged as superuser"""
    endpoint = get_url_with_auth(all_rpc_url, john_doe.username, common_pwd)
    return python_xmlrpc.ServerProxy(endpoint)


@pytest.fixture
def jsonrpc_client_as_user(all_rpc_url, john_doe, common_pwd):
    """Return the default JSON-RPC client, logged as superuser"""
    endpoint = get_url_with_auth(all_rpc_url, john_doe.username, common_pwd)
    return jsonrpcclient.HTTPClient(endpoint)
