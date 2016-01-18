import serial

class PhiIonGun(object):
    
    def __init__(self, port="COM6", address=3, debug = False):
        self.port = port
        self.debug = debug
        
        if self.debug: print "Phi Ion Gun init, port=%s" % self.port
        
        self.ser = serial.Serial(port=self.port, baudrate=57600, timeout=1.0)
    
    
    def ask_cmd(self, cmd_id, data=None):
        msg = "~ %02X %02X" % (self.address, self.cmd_id)

        if data:
            msg += data
            msg += " "
    
        checksum = self.checksum_func(msg)
        full_msg = msg + ("%02X\n" % checksum)
        
        if self.debug:
            print "ask_cmd write->", repr(full_msg)
        
        self.ser.write(full_msg)

        resp = self.ser.readline()
        
        if self.debug:
            print "ask_cmd resp->", repr(resp)
        
        assert resp[0:8] == "%02X OK 00 "
        assert self.checksum_func(resp[:-3]) == int(resp[-3:-1],16)
        
        return_msg = resp[8:-3]
        return return_msg
    
    
    def checksum_func(self, data):
        checksum = 0x00
        for b in data:
            #print b
            checksum += ord(b)
            checksum = checksum & 0xFF
            print b, hex(checksum)
        print "checksum", hex(checksum)
        return checksum
    
    
    def read_version(self):
        """ '~ 03 02 25.' ||| '03 OK 00 3.0.1(Apr 19 2011 @13:13:19) B5.'
        """
        version_str = self.ask_cmd(0x02)
        return version_str
    
    def read_condenser_v(self):
        pass
    
    def write_condenser_v(self):
        pass
    
    
