import os

import testinfra.utils.ansible_runner

from utils import *

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_simple_proxy(host):
    config = """
        server {
            location / {
                proxy_pass http://localhost:3000;
            }
        }
    """
    reconfigure_nginx2(host, config_file_content=config)

    assert_http_response_contains(host, "http://localhost:80", 'NodeJs Hello')


def test_static_content_multiple_locations(host):
    config = """
        server {
          root /var/www/default-domain;
          
          location / {
          }

          # /jack maps to /var/www/default-domain/jack  
          location /jack/ {
          }
          
          # /jane maps to /var/www/jane_home/htmls/jane 
          location /jane/ {
            root /var/www/jane_home/htmls;
          }
        }
    """

    joe_content = "<html>Joe</html>"
    jack_content = "<html>Jack</html>"
    jane_content = "<html>Jane</html>"

    copy_content_to_file(host, joe_content, "/var/www/default-domain/joe.html")
    copy_content_to_file(host, jack_content, "/var/www/default-domain/jack/jack.html")
    copy_content_to_file(host, jane_content, "/var/www/jane_home/htmls/jane/jane.html")

    reconfigure_nginx2(host, config_file_content=config)

    assert_http_response_contains(host, "http://localhost:80/joe.html", joe_content)
    assert_http_response_contains(host, "http://localhost:80/jack/jack.html", jack_content)
    assert_http_response_contains(host, "http://localhost:80/jane/jane.html", jane_content)

