from setuptools import setup, find_packages
from os import path


def extract_version():
    path_to_init = path.join(path.dirname(__file__), 'sensordata', '__init__.py')
    with open(path_to_init, 'r') as f:
        version_line = [line for line in f.readlines() if line.startswith('VERSION')][0]
        raw_version = version_line.split('=')[-1].strip()
        return '.'.join([str(x) for x in eval(raw_version)])


setup(
    name='sensor-data-collection',
    packages=find_packages(exclude=['tests']),
    install_requires=['pyzmq', 'multiprocess', 'argparse'],
    version=extract_version(),
    entry_points={
        'console_scripts': [
            'sensor-data=sensordata.extraction:main'
        ]
    }
)
