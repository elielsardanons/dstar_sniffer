#!/usr/bin/env python

import socket
import sys
from struct import *
import ConfigParser
from dstar import DStar
from aprsis import AprsIS
import logging

if __name__ == "__main__":

	logger = logging.getLogger('dstar_sniffer')
	hdlr = logging.FileHandler('/var/log/dstar_sniffer.log')
	formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	hdlr.setFormatter(formatter)
	logger.addHandler(hdlr) 
	logger.setLevel(logging.INFO)

	# Read configuration file.
	config = ConfigParser.ConfigParser()
	config.read("dstar_sniffer.conf")
	controller_ip = config.get("controller", "ip")
	controller_port = config.getint("controller", "port")
	controller_iface = config.get("controller", "iface")

	# Connect to APRS-IS network.
	aprsIS = AprsIS(logger, config.get("aprs-is", "callsign"), config.get("aprs-is", "password"))

	# Initialize the dstar packet manipulation class
	dstar = DStar(logger)

	try:
		s = socket.socket(socket.AF_PACKET , socket.SOCK_RAW , socket.ntohs(0x0003))
		s.setsockopt(socket.SOL_SOCKET, 25, controller_iface) # Bind to device
	except socket.error , msg:
		logger.info('Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
		sys.exit()

	# receive packets
	while True:
		packet = s.recvfrom(65565)

		#packet string from tuple
		packet = packet[0]

		#parse ethernet header
		eth_length = 14

		eth_header = packet[:eth_length]
		eth = unpack('!6s6sH' , eth_header)
		eth_protocol = socket.ntohs(eth[2])

		#Parse IP packets, IP Protocol number = 8
		if eth_protocol == 8 :
			# parse IP header
			ip_header = packet[eth_length:20+eth_length]
			iph = unpack('!BBHHHBBH4s4s' , ip_header)
			version_ihl = iph[0]
			version = version_ihl >> 4
			ihl = version_ihl & 0xF
			iph_length = ihl * 4
			protocol = iph[6]
			s_addr = socket.inet_ntoa(iph[8]);
			d_addr = socket.inet_ntoa(iph[9]);

			# UDP packets
			if protocol == 17 and s_addr == controller_ip:
				u = iph_length + eth_length
				udph_length = 8
				udp_header = packet[u:u+8]
				udph = unpack('!HHHH' , udp_header)

				source_port = udph[0]
				dest_port = udph[1]
				length = udph[2]

				if dest_port != controller_port:
					continue

				h_size = eth_length + iph_length + udph_length
				data_size = len(packet) - h_size

				# get data from the packet
				data = packet[h_size:]

				dstar_stream = dstar.parse(data)
				if dstar_stream != None:
					# End of stream!
					logger.info(dstar_stream)
					if 'D74' in dstar_stream['sfx'] and '$GPGGA' in dstar_stream['gps']:
						# only send beacon from Kenwood D74
						aprsIS.send_beacon(dstar_stream['my'], dstar_stream['sfx'], dstar_stream['message'],\
						dstar_stream['gps']['$GPGGA'])

