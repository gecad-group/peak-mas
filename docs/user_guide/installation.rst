Installation Guide
==================

This guide will help you install PEAK on your machine and configuring a XMPP server for your agents to communicate.

Requirements:

* Python v3.9.6
* An XMPP server (e.g., `Ejabberd`_ or `Prosody`_)

Creating a Virtual Environment
--------------------------------

There are several options to manage Python virtual environments. In this guide, we will show you how to create a virtual environment using `venv`_ and `conda`_.

Venv
^^^^^^^^^^^^

It is recommended to create a virtual environment to avoid dependency conflicts with other Python projects. You can create a virtual environment using `venv`_ by running the following command in your terminal::

    $ python3 -m venv .venv

This will create a virtual environment named ``.venv`` in your current directory. Activate the virtual environment with the command::

    $ source peak-env/bin/activate  # On Unix or MacOS
    $ peak-env\Scripts\activate     # On Windows

Miniconda
^^^^^^^^^^^^

Other option is to use `conda`_ to create a virtual environment. For that you first need to install `miniconda`_ following the instructions in its `documentation <https://www.anaconda.com/docs/getting-started/miniconda/install>`__. 
Then you can create a conda environment with the command::

    $ conda create --name peak python=3.9.6



Installing PEAK
----------------

To install PEAK is very easy, you just need to have pip installed in your terminal and run the following command line::

    $ pip install peak-mas

.. tip::

  It is recommended to use a virtual environment to avoid dependency conflicts with other Python packages.

Here we are going to teach you how to install PEAK. 

Firstly, you need to install Python v3.9.6. After that, you can install PEAK by using `pip`_::
    
    $ pip install peak-mas

Another way to install PEAK is via `conda`_. For that, you can download the `env.yml`_ file from the repository, and type these commands in the terminal::

    $ conda env create -f environment.yml
    $ conda activate peak

Test if it is well installed by using one of the commands bellow::

    $ peak
    $ python -m peak

Installing and Configuring an XMPP server
------------------------------------------------

Now you are ready to go!


.. _pip: https://pip.pypa.io/en/stable/
.. _conda: https://docs.conda.io/en/latest/miniconda.html
.. _env.yml: https://github.com/gecad-group/peak-mas/blob/main/env.yml
.. _Ejabberd: https://www.ejabberd.im/
.. _Prosody: https://prosody.im/
.. _venv: https://docs.python.org/3/library/venv.html
.. _miniconda: https://www.anaconda.com/docs/getting-started/miniconda/main