import serial

class crystaltech_dds(object):

    def __init__(self, port='/dev/ttyS3', debug=False):
    
        self.port = port
        self.debug = debug
        
        self.frequency = [0,0,0,0,0,0,0,0]
        self.amplitude = [0,0,0,0,0,0,0,0]
                
        self.ser = serial.Serial(port, 38400, timeout=1,
                    parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, xonxoff=False, rtscts=False)
    
    def readline(self):
        data = self.ser.readline()
        if self.debug: print "crystaltech_dds readline:", data                  
        return data
    def read(self): # read one character from buffer
        data = self.ser.read()
        if self.debug: print "crystaltech_dds read:", data
        #data = data.lstrip('\n')
        #data = data.lstrip('* ')
        return data
    def write(self, data):
        self.ser.write(data  + '\r\n')
        return
    def write_with_echo(self, data):
        if self.debug: print "crystaltech_dds write_with_echo:", data
        self.write(data)
       # return self.readline()

    def close(self):
        self.ser.close()
        
    def set_calibration(self, c0,c1,c2,c3):
        for i, c in enumerate([c0,c1,c2,c3]):
            self.write_with_echo("cal tuning %i %g" % (i, c))
            
    def get_calibration(self):
    
        # out put should look like this: "Tuning Polynomial Coefficient 0 is 3.531000e+02"
        
        c = [0,0,0,0]
        for i in [0,1,2,3]:
            self.write_with_echo("cal tuning %i" % i)
            output = self.readline()

            c[i] = float( output.split()[-1] )
        
        return tuple(c)
    
    def set_frequency(self, freq, channel=0):
        assert 50e6 < freq < 200e6
        self.write_with_echo("dds f %i %f" % (channel, freq))
        
    def set_wavelength(self, wl,  channel=0):
        assert 300 < wl < 2000
        self.write_with_echo("dds wave %i %f" % (channel, wl))
        
    def get_frequency(self, channel=0):
    
        #output in the form:"Channel 0 profile 0 frequency 8.278661e+07Hz (Ftw 888914432)"
        self.write_with_echo("dds f %i" % channel)
        output = self.readline()
        self.frequency[channel] = output.split()[5][:-2]
        return self.frequency[channel]
    
    def get_wavelength(self, channel=0):
        #FIXME
        #TODO
        #self.write_with_echo("cal tune %f" % self.get_frequency())
        #output = self.readline()
        pass

    def set_amplitude(self, amp, channel=0):
        "amplitude range from 0 to 16383 (2^14)"
        self.write_with_echo("dds a %i %i" % (channel, amp))

    def get_amplitude(self, channel=0):
        self.write_with_echo("dds a %i" % channel)
        output = self.readline()
        #output should look like:"Channel 1 @ 0"
        self.amplitude[channel] = int(output.split()[-1])
        return self.amplitude[channel]

    def modulation_enable(self):
        self.write_with_echo("dau en mod")
        self.write_with_echo("dau gain * 255")
        
    def modulation_disable(self):
        self.write_with_echo("dau gain * 0")
        self.write_with_echo("dau dis mod" )
        
if __name__ == '__main__':

    cdds = crystaltech_dds(port='/dev/ttyS1', debug=True)
    
    print cdds.get_calibration()
        
