# Nginx examples

A collection of tests demonstrating Nginx features. Each test aims to be as simple as possible to showcase one feature of Nginx.

The tests are written in the Testinfra framework and executed with Molecule.
Molecule uses Docker to start up a container, upon which Ansible starts up a Nodejs application and an Nginx service.
Each test case uploads an NGINX configuration file, reloads it in NGINX and executes some verification logic.

Local requirements: Docker, Ansible, Molecule

The tests are located under [molecule/default/tests](molecule/default/tests)

## Features

- Simple static content
- Simple proxy
