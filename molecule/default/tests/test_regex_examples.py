import pytest

from utils import *

# skip this file completely for now
pytestmark = pytest.mark.skip

def test_location_with_regex(host):
    clean_up_and_reconfigure_nginx(host, config="""
        server {
            location ~ /person/(.*) {
                return 200 "hello [$1]";
            }
        }
    """)

    assert_http_response_contains(host, "http://localhost/person/blah-blah", "hello [blah-blah]")

def test_location_with_regex_2(host):
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
