from setuptools import setup, find_packages
import os

thelibFolder = os.path.dirname(os.path.realpath(__file__))
requirementPath = thelibFolder + '/requirements.txt'
install_requires = [] # Here we'll get: ["gunicorn", "docutils>=0.3", "lxml==0.5a7"]
if os.path.isfile(requirementPath):
    with open(requirementPath) as f:
        install_requires = f.read().splitlines()

setup(
    name="PEAK", 
    version='1.0.0', 
    author='Bruno Ribeiro', 
    author_email='brgri@isep.ipp.pt', 
    description='Python-based Ecosystem for Agent Communities', 
    packages=find_packages(),
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "peak=peak.__main__:main"
        ],
    })