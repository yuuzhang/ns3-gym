from setuptools import setup, find_packages
from termcolor import colored
import sys
import os.path

cwd = os.getcwd()
protobufFile = cwd + '/ns3gym/messages_pb2.py'

if not os.path.isfile(protobufFile):
    print(colored('File: ', 'red'), "ns3-gym/src/opengym/model/ns3gym/ns3gym/messages_pb2.py", colored(' was not found.', 'red'))
    sys.exit('Protocol Buffer messages are missing. Please run ' + colored('./waf configure', 'green') + ' to generate the file')


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='ns3gym',
    version='0.1.0',
    packages=find_packages(),
    scripts=[],
    url='',
    license='MIT',
    author='Piotr Gawlowicz',
    author_email='gawlowicz.p@gmail.com',
    description='OpenAI Gym meets ns-3',
    long_description='OpenAI Gym meets ns-3',
    keywords='openAI gym, ML, RL, ns-3',
    install_requires=['pyzmq', 'numpy', 'protobuf', 'protobuf3', 'gym'],
    extras_require={},
)
