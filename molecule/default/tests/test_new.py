import pytest

from utils import *

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