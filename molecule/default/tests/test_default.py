import pytest

from utils import *

# todo list
# named location
# rewrite
# regex in location name
#


def test_simple_proxy(host):
    clean_up_and_reconfigure_nginx(host, config="""
        server {
            location / {
                proxy_pass http://localhost:3000;
            }
        }
    """)

    assert_http_response_contains(host, "http://localhost:80", 'NodeJs Hello')

@pytest.mark.skip(reason="No idea")
def test_simple_proxy_with_regex(host):
    clean_up_and_reconfigure_nginx(host, config="""
        server {
            root /var/www/default-domain;
            location / {
            }
            location ~ /person/(.*) {
                return http://localhost/$1;
            }
        }
    """)

    jack_html = "<html>joe</html>"
    copy_content_to_file(host, jack_html, "/var/www/default-domain/jack/index.html")
    assert_http_response_contains(host, "http://localhost/jack/index.html", jack_html)
    assert_http_response_contains(host, "http://localhost/person/jack/index.html", jack_html)


def test_try_files_delegate_to_named_location(host):
    clean_up_and_reconfigure_nginx(host, config="""
        server {
            root /var/www/default-domain;
            location / {
                # last option can be a named location
                try_files $uri $uri/index.html @mongrel;
            }
            
            location @mongrel {
                proxy_pass http://localhost:3000;
            }
        }
    """)

    assert_http_response_contains(host, "http://localhost/noneexisting.html", 'NodeJs Hello')



def test_try_files_404(host):
    clean_up_and_reconfigure_nginx(host, config="""
        server {
          root /var/www/default-domain;
          location / {
            try_files $uri $uri/ =404;
          }
        }
    """)

    assert_http_not_found(host, "http://localhost:80/jack.html")


def test_try_files_with_default(host):
    clean_up_and_reconfigure_nginx(host, config="""
        server {
          root /var/www/default-domain;
          location / {
            try_files $uri /default/index.html;
          }
        }
    """)

    index_content = "<html>Index</html>"
    copy_content_to_file(host, index_content, "/var/www/default-domain/default/index.html")

    assert_http_response_contains(host, "http://localhost:80/nonexisting.html", index_content)


@pytest.mark.skip(reason="No idea")
def test_try_files_with_trailing_slash(host):
    clean_up_and_reconfigure_nginx(host, config="""
        server {
          root /var/www/default-domain;
          location / {
            try_files $uri $uri/;
          }
        }
    """)

    index_content = "<html>index</html>"
    copy_content_to_file(host, index_content, "/var/www/default-domain/persons/index.html")
    assert_http_response_contains(host, "http://localhost:80/persons", index_content)


def test_change_listener_port(host):
    clean_up_and_reconfigure_nginx(host, config="""
        server {
          listen 8085;
          root /var/www/default-domain;
          location / {
          }
        }
    """)

    joe_content = "<html>Joe</html>"
    copy_content_to_file(host, joe_content, "/var/www/default-domain/joe.html")

    assert_http_response_contains(host, "http://localhost:8085/joe.html", joe_content)


@pytest.mark.skip(reason="this requires ssl certificate")
def test_multiple_listener_ports(host):
    clean_up_and_reconfigure_nginx(host, config="""
        server {
          listen 80;
          listen 443 ssl;
          root /var/www/default-domain;
          location / {
          }
        }
    """)

    index_content = "<html>Joe</html>"
    copy_content_to_file(host, index_content, "/var/www/default-domain/index.html")

    assert_http_response_contains(host, "http://localhost", index_content)
    assert_http_response_contains(host, "https://localhost", index_content)


def test_regex_locations(host):
    clean_up_and_reconfigure_nginx(host, config="""
        server {
          root /var/www/default-domain;

          location / {
          }

          location ~ \.(mp3|mp4) {
            root /var/www/default-domain/music;
          }
        }
    """)

    index_content = "<html>index</html>"
    some_mp3 = "I am an mp3"
    some_mp4 = "I am an mp4"

    copy_content_to_file(host, index_content, "/var/www/default-domain/index.html")
    copy_content_to_file(host, some_mp3, "/var/www/default-domain/music/some.mp3")
    copy_content_to_file(host, some_mp4, "/var/www/default-domain/music/some.mp4")

    assert_http_response_contains(host, "http://localhost:80/index.html", index_content)
    assert_http_response_contains(host, "http://localhost:80/some.mp3", some_mp3)
    assert_http_response_contains(host, "http://localhost:80/some.mp4", some_mp4)


def test_default_dirs_to_index(host):
    clean_up_and_reconfigure_nginx(host, config="""
        server {
          root /var/www/default-domain;

          # If a request ends with a slash, NGINX treats it as a request
          # for a directory and tries to find an index file in the directory
          location /persons/ {
          }
        }
    """)

    index_content = "<html>index</html>"
    copy_content_to_file(host, index_content, "/var/www/default-domain/persons/index.html")

    assert_http_response_contains(host, "http://localhost:80/persons/", index_content)
    assert_http_response_contains(host, "http://localhost:80/persons", "301 Moved Permanently")


def test_multiple_locations(host):
    clean_up_and_reconfigure_nginx(host, config="""
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
    """)

    joe_content = "<html>Joe</html>"
    jack_content = "<html>Jack</html>"
    jane_content = "<html>Jane</html>"

    copy_content_to_file(host, joe_content, "/var/www/default-domain/joe.html")
    copy_content_to_file(host, jack_content, "/var/www/default-domain/jack/jack.html")
    copy_content_to_file(host, jane_content, "/var/www/default-domain/jane_home/htmls/jane/jane.html")

    assert_http_response_contains(host, "http://localhost:80/joe.html", joe_content)
    assert_http_response_contains(host, "http://localhost:80/jack/jack.html", jack_content)
    assert_http_response_contains(host, "http://localhost:80/jane/jane.html", jane_content)


def test_reject_empty_server_name(host):
    clean_up_and_reconfigure_nginx(host, config="""
        server {
            listen      80;
            server_name "";
            return      400;
        }
    """)

    assert_http_response_contains(host, "http://localhost:80/anything", "400 Bad Request")


def test_choose_virtual_server_by_host(host):
    clean_up_and_reconfigure_nginx(host, config="""
        server {
            listen 80;
            server_name example.org www.example.org;
            location / {
              root /var/www/default-domain/server1;
            }
        }

        server {
            listen 80;
            server_name example2.org www.example2.org;
            location / {
              root /var/www/default-domain/server2;
            }
        }

       # default server to catch the rest
        server {
            listen 80 default_server;
            location / {
              root /var/www/default-domain/;
            }
        }
    """)

    default_index = "default index"
    server1_index = "server1 index"
    server2_index = "server2 index"

    copy_content_to_file(host, default_index, "/var/www/default-domain/index.html")
    copy_content_to_file(host, server1_index, "/var/www/default-domain/server1/index.html")
    copy_content_to_file(host, server2_index, "/var/www/default-domain/server2/index.html")

    assert_http_response_contains(host, "-H 'Host: example.org' http://localhost:80", server1_index)
    assert_http_response_contains(host, "-H 'Host: www.example.org' http://localhost:80", server1_index)

    assert_http_response_contains(host, "-H 'Host: example2.org' http://localhost:80", server2_index)
    assert_http_response_contains(host, "-H 'Host: www.example2.org' http://localhost:80", server2_index)

    assert_http_response_contains(host, "-H 'Host: somethingelse' http://localhost:80", default_index)


def test_choose_virtual_server_by_port(host):
    clean_up_and_reconfigure_nginx(host, config="""
        server {
            listen 8081;
            location / {
              root /var/www/default-domain/server1;
            }
        }
        server {
            listen 8082;
            location / {
              root /var/www/default-domain/server2;
            }
        }
    """)

    server1_index = "server1 index"
    server2_index = "server2 index"

    copy_content_to_file(host, server1_index, "/var/www/default-domain/server1/index.html")
    copy_content_to_file(host, server2_index, "/var/www/default-domain/server2/index.html")

    assert_http_response_contains(host, "http://localhost:8081", server1_index)
    assert_http_response_contains(host, "http://localhost:8082", server2_index)


def test_return(host):
    clean_up_and_reconfigure_nginx(host, config="""
        server {
            root /var/www/default-domain/server1;
            location /persons/ {
                return 301;
            }
        }
    """)