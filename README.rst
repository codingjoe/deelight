Deelight - Yeelight Daylight
============================

**Night shift script for Xiaomi Mi Yeelight lights and light bulbs.**


Setup
-----

Raspberry Pi
~~~~~~~~~~~~

Download setup the latest version of Rasbian_ on your Raspberry Pi.

.. _Rasbian: https://www.raspberrypi.org/downloads/raspbian/


Next install the following packages:

.. code-block:: shell

    sudo apt-get install python3-pip -y

Deeelight
~~~~~~~~~

Install the Python package

.. code-block:: shell

    sudo pip install deelight

and run the deelight command

.. code-block:: shell

    deelight "New York, US" -v


Autostart
~~~~~~~~~

If you are running ``deelight`` on Raspbian or any other Debian system you can
add a simple upstart script. It will be executed once your network is up.

.. code-block:: shell

    sudo nano /etc/systemd/system/deelight.service

.. code-block:: ini

    [Unit]
    Description=Daylight mode for Xiaomi Mi Yeelight
    After=network-online.target

    [Service]
    Type=idle
    ExecStart=/usr/bin/python3 /usr/local/bin/deelight Valletta -v
    Restart=always

    [Install]
    WantedBy=multi-user.target

.. code-block:: shell

    sudo systemctl enable deelight.service
    sudo service deelight start
