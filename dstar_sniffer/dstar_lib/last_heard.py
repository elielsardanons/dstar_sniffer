from datetime import datetime
import time

from last_heard_render import render_last_heard_html
from dstar_sniffer.util_lib import config
from dstar_sniffer.aprs_lib.nmea import gpgga_get_position, dprs_get_position

def last_heard_callback(dstar_stream):
	last = LastHeard()
	last.add(dstar_stream)

class LastHeard:

	instance = None

	class __LastHeard:

		last_heard = {}
		output_html_file = None
		
		def __init__(self):
			cfg = config.config_load()
			self.output_html_file = cfg.get("last_heard", "output_file")

	def __init__(self):
		if LastHeard.instance == None:
			LastHeard.instance = LastHeard.__LastHeard()

        def __getattr__(self, name):
                return getattr(self.instance, name)

	def add(self, dstar_stream):
		cs_user = dstar_stream['my'].strip()

		if cs_user in self.last_heard:
			self.last_heard.pop(cs_user, None)
		self.last_heard[cs_user] = {}

		self.last_heard[cs_user]['time'] = datetime.now()
		self.last_heard[cs_user]['ur'] = dstar_stream['ur']
		self.last_heard[cs_user]['my'] = dstar_stream['my']
		self.last_heard[cs_user]['sfx'] = dstar_stream['sfx']
		self.last_heard[cs_user]['rpt1'] = dstar_stream['rpt1']
		self.last_heard[cs_user]['rpt2'] = dstar_stream['rpt2']
		self.last_heard[cs_user]['message'] = dstar_stream['message']
		self.last_heard[cs_user]['gps'] = dstar_stream['gps']
		self.last_heard[cs_user]['raw'] = dstar_stream['slow_speed_data']
		position = None
		if '$GPGGA' in dstar_stream['gps']:
			position = gpgga_get_position(dstar_stream['gps']['$GPGGA'])
		if 'DPRS' in dstar_stream['gps']:
			position = dprs_get_position(dstar_stream['gps']['DPRS'])
		if position:
			lat_sign = ''
			long_coord = ''
			if position['lat_coord'] == 'S':
				lat_sign = '-'
			if position['long_coord'] == 'W':
				long_sign = '-'
			self.last_heard[cs_user]['latitude'] = lat_sign + self.gpgga_latitude_to_gmap(position['lat'])
			self.last_heard[cs_user]['longitude'] = long_sign + self.gpgga_longitude_to_gmap(position['long'])
		
		# remove old entries.
		self.cleanup()
		self.update_output()

	def gpgga_latitude_to_gmap(self, value):
		position = str(value)
		return str(float(float(position[:2]) + float(position[2:]) / 60))

	def gpgga_longitude_to_gmap(self, value):
		position = str(value)
		return str(float(float(position[:3]) + float(position[3:]) / 60))

	def cleanup(self):
		for cs in self.last_heard.keys():
			diff = time.mktime(datetime.now().timetuple()) - time.mktime(self.last_heard[cs]['time'].timetuple())
			if (diff / 60) > 120:
				self.last_heard.pop(cs, None)

	# write an html based on the last_heard info.
	def update_output(self):
		html_file = open(self.output_html_file, "w+")
		html_file.write(render_last_heard_html(self.last_heard))
		html_file.close()

