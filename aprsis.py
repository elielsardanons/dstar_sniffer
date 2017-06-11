import aprs
import nmea

class AprsIS:

	def __init__(self, callsign, password):
		self.aprs_connection = aprs.TCP(callsign, password)
		self.aprs_connection.start()

	def send_beacon(self, callsign, sfx, message, gpgga):
		position = nmea.gpgga_get_position(gpgga)
		aprs_frame = callsign+'>APK'+sfx+':!'+position['lat'] + position['lat_coord'] + '\\'+position['long']+position['long_coord']+'a/A=' + position['height'] + message
		try:
			self.aprs_connection.send(aprs.Frame(aprs_frame))
		except:
			print "Invalid aprs frame: " + aprs_frame