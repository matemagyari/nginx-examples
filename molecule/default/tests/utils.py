# Utility functions for tests
import os

# todo read from from Ansible
domain = "default-domain"

def current_dir():
    return os.path.dirname(os.path.realpath(__file__))

nginx_config_path = "/etc/nginx/sites-enabled/{}".format(domain)

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def read_nginx_config_file(filename):
    path = "{dir}/nginx_configs/{file}".format(dir=current_dir(), file=filename)
    read_file(path)

def copy_content_to_file(host, content, remote_path):
    # delete content of file if exists or create a new empty one
    assert host.run("echo '' > {}".format(remote_path)).succeeded

    for line in content.splitlines():
        cmd = "echo '{}' >> {}".format(line, remote_path)
        assert host.run(cmd).succeeded

def copy_file_to_host(host, local_path, remote_path):
    copy_content_to_file(host, read_file(local_path), remote_path)

def add_static_content_to_nginx(host, file_name, content = None):
    remote_file_path = "/var/www/{}/{}".format(domain, file_name)
    if content is None:
        copy_file_to_host(host = host,
                          local_path = "{}/static_content/{}".format(current_dir(), file_name),
                          remote_path = remote_file_path)
    else:
        copy_content_to_file(host, content, remote_file_path)

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