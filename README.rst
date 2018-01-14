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

    sudo apt-get install python3 -y
    wget https://bootstrap.pypa.io/get-pip.py
    sudo python3 get-pip.py

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

    sudo touch /etc/network/if-up.d/deelight
    chmod +x /etc/network/if-up.d/deelight
    sudo nano /etc/network/if-up.d/deelight

.. code-block:: bash

    #!/bin/sh -e

    ## Replace this value with the correct city name.
    # CITY="New York, US"
    CITY=Valletta

    PIDFILE=/var/run/deelight.pid

    case "$IFACE" in
        lo)
            # The loopback interface does not count.
            # only run when some other interface comes up
            exit 0
            ;;
        *)
            ;;
    esac

    if [ -f "$PIDFILE" ] && \
       [ "$(ps -p "$(cat "$PIDFILE")" -o comm=)" == deelight ]; then
            exit 0
    fi

    deelight "$CITY" -vv >/var/log/deelight.log 2>&1 &
    echo $! >"$PIDFILE"
