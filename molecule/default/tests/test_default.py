import os

import testinfra.utils.ansible_runner

from utils import *

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

def test_hosts_file(host):
    f = host.file('/etc/hosts')

    assert f.exists
    assert f.user == 'root'
    assert f.group == 'root'

def test_static_page(host):
    reconfigure_nginx(host, config_file = "static.conf")
    assert_http_response_contains(host, "http://localhost:80", 'Hello NGINX World')

def test_simple_proxy(host):
    reconfigure_nginx(host, config_file = "simple_proxy.conf")
    assert_http_response_contains(host, "http://localhost:80", 'NodeJs Hello')


