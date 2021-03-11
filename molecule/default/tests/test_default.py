import testinfra.utils.ansible_runner

from utils import *

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_simple_proxy(host):
    delete_files_under(host, "/var/www/default-domain")

    config = """
        server {
            location / {
                proxy_pass http://localhost:3000;
            }
        }
    """
    reconfigure_nginx2(host, config_file_content=config)

    assert_http_response_contains(host, "http://localhost:80", 'NodeJs Hello')


def test_try_files_404(host):
    delete_files_under(host, "/var/www/default-domain")

    config = """
        server {
          root /var/www/default-domain;
          location / {
            try_files $uri $uri/ =404;
          }
        }
    """

    reconfigure_nginx2(host, config_file_content=config)

    assert_http_not_found(host, "http://localhost:80/jack.html")


def test_try_files_with_default(host):
    delete_files_under(host, "/var/www/default-domain")

    config = """
        server {
          root /var/www/default-domain;
          location / {
            try_files $uri /default/index.html;
          }
        }
    """

    index_content = "<html>Index</html>"
    copy_content_to_file(host, index_content, "/var/www/default-domain/default/index.html")

    reconfigure_nginx2(host, config_file_content=config)

    assert_http_response_contains(host, "http://localhost:80/nonexisting.html", index_content)


def test_change_listener_port(host):
    delete_files_under(host, "/var/www/default-domain")

    config = """
        server {
          listen 8085;
          root /var/www/default-domain;
          location / {
          }
        }
    """

    joe_content = "<html>Joe</html>"
    copy_content_to_file(host, joe_content, "/var/www/default-domain/joe.html")

    reconfigure_nginx2(host, config_file_content=config)

    assert_http_response_contains(host, "http://localhost:8085/joe.html", joe_content)


def test_regex_locations(host):
    delete_files_under(host, "/var/www/default-domain")

    config = """
        server {
          root /var/www/default-domain;
          
          location / {
          }

          # /jack maps to /var/www/default-domain/jack  
          location ~ \.(mp3|mp4) {
            root /var/www/default-domain/music;
          }
        }
    """

    index_content = "<html>index</html>"
    some_mp3 = "I am an mp3"
    some_mp4 = "I am an mp4"

    copy_content_to_file(host, index_content, "/var/www/default-domain/index.html")
    copy_content_to_file(host, some_mp3, "/var/www/default-domain/music/some.mp3")
    copy_content_to_file(host, some_mp4, "/var/www/default-domain/music/some.mp4")

    reconfigure_nginx2(host, config_file_content=config)

    assert_http_response_contains(host, "http://localhost:80/index.html", index_content)
    assert_http_response_contains(host, "http://localhost:80/some.mp3", some_mp3)
    assert_http_response_contains(host, "http://localhost:80/some.mp4", some_mp4)


def test_multiple_locations(host):
    delete_files_under(host, "/var/www/default-domain")

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
            root /var/www/default-domain/jane_home/htmls;
          }
        }
    """

    joe_content = "<html>Joe</html>"
    jack_content = "<html>Jack</html>"
    jane_content = "<html>Jane</html>"

    copy_content_to_file(host, joe_content, "/var/www/default-domain/joe.html")
    copy_content_to_file(host, jack_content, "/var/www/default-domain/jack/jack.html")
    copy_content_to_file(host, jane_content, "/var/www/default-domain/jane_home/htmls/jane/jane.html")

    reconfigure_nginx2(host, config_file_content=config)

    assert_http_response_contains(host, "http://localhost:80/joe.html", joe_content)
    assert_http_response_contains(host, "http://localhost:80/jack/jack.html", jack_content)
    assert_http_response_contains(host, "http://localhost:80/jane/jane.html", jane_content)

