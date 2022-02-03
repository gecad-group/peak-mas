from setuptools import setup, find_packages

setup(
    name="PEAK", 
    version='1.0.0', 
    author='Bruno Ribeiro', 
    author_email='brgri@isep.ipp.pt', 
    description='Python-based Ecosystem for Agent Communities', 
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "peak=peak.mas.__main__:main",
            "peak-management=peak.management.__main__:main"
        ],
    })