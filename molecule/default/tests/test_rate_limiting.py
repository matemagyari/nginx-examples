import pytest
import time

from utils import *


def test_rate_limit(host):
    clean_up_and_reconfigure_nginx(host, config="""
        limit_req_zone $binary_remote_addr zone=mylimit:10m rate=1r/s;

        server {
            location / {
                limit_req zone=mylimit;

                proxy_pass http://localhost:3000;
            }
        }
    """)

    # reset
    execute(host, cmd="curl http://localhost/reset")

    start = current_milli_time()
    while current_milli_time() - start < 2000:
        print("hi")
        http_response(host, url = "http://localhost/something")

    assert_http_response_contains(host, "http://localhost/state", "hello [blah-blah]")

