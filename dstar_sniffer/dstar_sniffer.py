#!/usr/bin/env python

#
# DSTAR Repeater Controller Sniffer
#
# Coded by Eliel Sardanons (LU1ALY)
#

import socket
import sys
import logging
import logging.config

from dstar_lib import DStar
from aprs_lib import aprsis_dstar_callback
from net_lib import parse_packet
from util_lib.daemon import Daemon
from util_lib import config

class DStarSniffer(Daemon):
	def run(self):
		# Setup logging
		logging.config.fileConfig('/etc/dstar_sniffer/logging.conf')
		logger = logging.getLogger(__name__)
		logger.info("DStar Sniffer started.")

		# Read configuration file.
		cfg = config.config_load()
		controller_ip = cfg.get("controller", "ip")
		controller_port = cfg.getint("controller", "port")
		controller_iface = cfg.get("controller", "iface")

		# Initialize the dstar packet manipulation class
		dstar = DStar()

		# Register a dstar stream callback, this will
		# be executed once we parse the full dstar stream.
		dstar_stream_callback = []
		dstar_stream_callback.append(aprsis_dstar_callback) # Upload received positions to APRS-IS

		try:
			# Start listening to every UDP packet.
			s = socket.socket(socket.AF_PACKET , socket.SOCK_RAW , socket.ntohs(0x0003))
			s.setsockopt(socket.SOL_SOCKET, 25, controller_iface) # Bind to device
		except socket.error , msg:
			logger.error('Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
			sys.exit(-1)

		# Main loop, receive udp packets and run callbacks
		while True:
			packet = s.recvfrom(65565)
			data = parse_packet(packet, controller_ip, controller_port)
			if data != None:
				dstar_stream = dstar.parse(data)
				if dstar_stream != None:
					# End of stream!
					logger.info(dstar_stream)
					logger.info("Start running callbacks for received stream [%s]", dstar_stream['id'])
					for cb in dstar_stream_callback:
						logger.debug("Running callback: %s" + str(cb.__name__))
						cb(dstar_stream)
					logger.info("End running callbacks for received stream [%s]", dstar_stream['id'])

		logger.info("DStar sniffer ends running.")

def main():
	daemon = DStarSniffer('/var/run/dstar_sniffer.pid')
	daemon.start()