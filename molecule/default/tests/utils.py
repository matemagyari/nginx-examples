# Utility functions for tests
import os

# todo read from from Ansible
domain = "my-helloworld.com"

def current_dir():
    return os.path.dirname(os.path.realpath(__file__))

nginx_config_path = "/etc/nginx/sites-enabled/{}".format(domain)

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def read_nginx_config_file(filename):
    path = "{dir}/nginx_configs/{file}".format(dir=current_dir(), file=filename)
    read_file(path)

def copy_file_to_host(host, local_path, remote_path):
    content = read_file(local_path)

    # delete content of file if exists or create a new empty one
    assert host.run("echo '' > {}".format(remote_path)).succeeded

    for line in content.split():
        cmd = "echo '{}\n' >> {}".format(line, remote_path)
        assert host.run(cmd).succeeded

def reconfigure_nginx(host, config_file):
    nginx = host.service("nginx")
    assert nginx.is_enabled

    copy_file_to_host(host = host,
                      local_path = "{}/nginx_configs/{}".format(current_dir(), config_file),
                      remote_path = nginx_config_path)

    cmd = host.run("nginx -s reload")
    assert cmd.succeeded

    print("NGINX reloaded")

    assert nginx.is_running

def http_response(host, url):
    return host.run("curl {}".format(url)).stdout

def assert_http_response_contains(host, url, partial_content):
    assert partial_content in http_response(host, url)