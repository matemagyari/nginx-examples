import os

def print_current_dir():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    print("dir_path: {}".format(dir_path))

def test_curl_is_installed(host):
    print_current_dir()
    curl = host.package("curl")
    assert curl.is_installed