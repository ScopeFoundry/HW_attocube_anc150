import serial


class prologix_usb_gpib_dev(object):
	
	def __init__(self, port='/dev/ttyUSB1', addr=5, debug=False):
		self.port = port
		self.addr = addr
		self.debug = debug
		self.ser = serial.Serial(self.port, 115200, timeout=1,
				parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, xonxoff=False, rtscts=False)

	def readline(self):
        	data = self.ser.readline()
       		if self.debug: print "prologix_usb_gpib_dev readline:", self.port, self.addr, "::", data
        	return data
   	def read(self): # read one character from buffer
     		data = self.ser.read()
	        if self.debug: print "prologix_usb_gpib_dev readline:", self.port, self.addr, "::", data
        	#data = data.lstrip('\n')
        	#data = data.lstrip('* ')
        	return data
   	def write(self, data):
		self.ser.write("++addr %i\r\n" % self.addr)
        	self.ser.write(data  + '\r\n')
        	return
	def ask(self, quest):
		self.write(quest)
		return self.readline()
	
