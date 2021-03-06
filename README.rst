DStar Repeater Controller UDP Sniffer (latest release v1.1)
=====================================
This project tries to send every position received in a dstar repeater to aprs-is.

ICOM rpt sends all the traffic to the gateway using UDP port 20000.
We try to capture that traffic sniffing the network while we unserialize the udp packets to get
the slow speed data and routing information found in every DV transmission.

At the moment only kenwood /D74 received positions are sent to APRS-IS.

Install
-------
In order to install Dstar sniffer you could::

     wget https://github.com/elielsardanons/dstar_sniffer/files/1081265/DStarSniffer-1.1.tar.gz
     tar xvzf DStarSniffer-1.1.tar.gz
     cd DStarSniffer-1.1/
     python setup.py install
     
or use *pip* and run::

     sudo pip install --upgrade git+https://github.com/elielsardanons/dstar_sniffer.git@1.1

All the configuration files will be installed in /etc/dstar_sniffer/

Configuration
-------------
All the application configuration is in one file (/etc/dstar_sniffer/dstar_sniffer.conf)::

    [controller]
    port= <where the icom rpt controller sends all the DV traffic>
    iface= <name of the interface where the icom rpt controller is connected to the gateway>
    ip= <ip of the icom rpt controller>


Run dstar_sniffer
-----------------
Dstar sniffer will run like a daemon in the background, to start the application you should execute::

    dstar_sniffer start
   
to *stop* dstar_sniffer run::

    dstar_sniffer stop
    
if for some reason you want to *restart* dstar_sniffer, run::

    dstar_sniffer restart

Logging
-------
Dstar Sniffer will log all its output to ``/var/log/dstar_sniffer.log``
If you want to modify this you need to edit the file ``/etc/dstar_sniffer/logging.conf``.


Useful links
------------
[Slow speed data format] <http://www.qsl.net/k/kb9mwr/projects/dv/dstar/Slow%20Data.pdf>

eliel@eliel.com.ar
