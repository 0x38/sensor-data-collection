from fabric.api import *
from fabric.contrib.files import exists


@task
def prepare():
    local('python setup.py build sdist')


def package_version():
    return local('python setup.py --version', capture=True).stdout.strip()


def package_fullname():
    name = local('python setup.py --fullname', capture=True).stdout.strip()
    return name + '.tar.gz'

env.virtual_env_location = '/var/sensor_data_collection_env'
env.deploy_venv = 'SENSOR_DATA_COLLECTION_' + package_version()


def install_bluepy(pip_path):

    pip_absolute_path = '%s/%s' % (env.virtual_env_location, pip_path)

    # Install requirements
    sudo('apt-get install -y git build-essential libglib2.0-dev')

    # Install Bluepy
    bluepy_dir = "{deploy_venv}/bluepy".format(deploy_venv=env.deploy_venv)
    if exists(bluepy_dir):
        sudo('rm -rf {bluepy_dir}'.format(bluepy_dir=bluepy_dir))

    with cd(env.deploy_venv):
        run('git clone https://github.com/IanHarvey/bluepy.git')

    sudo('{pip} install -e {bluepy_dir}'.format(pip=pip_absolute_path, bluepy_dir=bluepy_dir))


@task
def deploy():
    prepare()
    package = package_fullname()
    tmp_package_path = '/tmp/%s' % package
    put('dist/%s' % package, tmp_package_path)

    sudo('/usr/bin/pip3 install virtualenv')

    if not exists(env.virtual_env_location):
        sudo('mkdir -p %s' % env.virtual_env_location)
        sudo('chown pi. %s' % env.virtual_env_location)

    with cd(env.virtual_env_location):

        pip_path = '%s/bin/pip' % env.deploy_venv

        if not exists(env.deploy_venv):
            run('python3 -m virtualenv %s' % env.deploy_venv)
            install_bluepy(pip_path)

        run('{pip} uninstall -y {package}; echo foo > /dev/null'.format(pip=pip_path, package=tmp_package_path))
        run('{pip} install {package}'.format(pip=pip_path, package=tmp_package_path))




