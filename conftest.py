from time import sleep

import docker

from modules.transports import get_transport_config

PATH = 'tests'
port_ssh = get_transport_config()['transports']['SSH']['port']
port_sql = get_transport_config()['transports']['MySQL']['port']
env_sql = get_transport_config()['transports']['MySQL']['environment']
containers_env = {
    'Dockerfile_ubuntu_sshd': {
        'name': 'cont_ubuntu_sshd',
        'ports': {'22/tcp': port_ssh}
    },
    'Dockerfile_mariadb': {
        'name': 'mariadb',
        'ports': {'3306/tcp': ('127.0.0.1', port_sql)},
        'environment': env_sql
    }
}


def pytest_sessionstart(session):    
    client = docker.from_env()
    client.containers.prune()
    for dockerfile, container_env in containers_env.items():
        images = client.images.build(path=PATH, dockerfile=dockerfile)
        try:
            client.containers.run(image=images[0],
                                  detach=True,
                                  **container_env)
        except Exception as e:
            if str(e).startswith('409 Client Error: Conflict'):
                pass
            else:
                print(e)
    client.containers.prune()
    sleep(15)  # waiting for start containers


def pytest_sessionfinish(session, exitstatus):
    containers = docker.from_env().containers.list()
    running_containers = {env['name'] for env in containers_env.values()}
    for container in containers:
        if container.name in running_containers:
            container.stop()
            container.remove()
