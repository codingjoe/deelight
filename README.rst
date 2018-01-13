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

    sudo apt-get install python3 python3-pip -y

Deeelight
~~~~~~~~~

Install the Python package

.. code-block:: shell

    pip3 install deelight

and run the deelight command

.. code-block:: shell

    deelight "New York, US" -v


Autostart
~~~~~~~~~

If you are running ``deelight`` on Raspbian or any other Debian system,
simply do:

.. code-block:: shell

    sudo echo '#!/usr/bin/env sh' > /etc/network/if-up.d/deelight
    sudo echo "$(which deelight) \"New York, US\" -v"" >> /etc/network/if-up.d/deelight
    sudo chmod +x /etc/network/if-up.d/deelight

Deelight will be now run whenever your device is connected to the network.
