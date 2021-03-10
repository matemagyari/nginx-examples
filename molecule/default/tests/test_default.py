import os

import testinfra.utils.ansible_runner

from utils import *

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

def test_static_page(host):
    add_static_content_to_nginx(host, "index.html")
    reconfigure_nginx(host, config_file = "simple_static_content.conf")

    assert_http_response_contains(host, "http://localhost:80", 'Index page')

def test_static_page_2(host):
    content = "<html>Hey</html>"
    add_static_content_to_nginx(host, "index.html", content)
    reconfigure_nginx(host, config_file = "simple_static_content.conf")

    assert_http_response_contains(host, "http://localhost:80", content)

def test_simple_proxy(host):
    reconfigure_nginx(host, config_file = "simple_proxy.conf")

    assert_http_response_contains(host, "http://localhost:80", 'NodeJs Hello')


