'''
Created on 21.09.2014

@author: Benedikt Ursprung
'''

import serial
import time

class PowerWheelArduino(object):
    "Arduino controlled flip mirror"
    
    def __init__(self, port="COM14", debug = False):
        self.port = port
        self.debug = debug
        
        if self.debug: print "PowerWheelArduino init, port=%s" % self.port
        
        self.ser = serial.Serial(port=self.port, baudrate=57600, timeout=0.1)
                                 
        self.ser.flush()
        time.sleep(0.1)


    def write_steps(self,steps):
        self.ser.write('am'+str(steps)+'\n')
        #print "steps ", steps
        
    def write_speed(self, speed):
        self.ser.write('as'+str(speed)+'\n')
        
    def read_status(self):
        self.ser.write('a?\n')
        status = self.ser.readline()
        return status    
    
    def read_encoder(self):
        
        if self.debug:
            print 'reading encoder'
            
        
        self.ser.write('ae\n')
                    
        
        resp=self.ser.readline()
        
        if self.debug:
            print int(float(resp[:-2]))

            
        return int(float(resp[:-2]))
        
        
    def close(self):
        self.ser.close()      
        


if __name__ == '__main__':
    W1 = PowerWheelArduino(debug=True);
    time.sleep(4)
    W1.write_steps('-400')
    time.sleep(4)
    W1.write_steps('400')    
    
    W1.read_status()
    
    
    W1.close()
    pass