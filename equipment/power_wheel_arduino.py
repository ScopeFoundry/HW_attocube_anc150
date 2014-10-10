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
        
        self.ser = serial.Serial(port=self.port, baudrate=9600, timeout=0.1)
                                 
        self.ser.flush()
        time.sleep(0.1)


    def write_steps(self,steps):
        self.ser.write('S'+str(steps))
        #print "steps ", steps
        
    def write_pulse(self,pulse_l):
        self.ser.write('T'+str(pulse_l))
        #print "pulse ", pulse_l  
        
    def close(self):
        self.ser.close()      
        


if __name__ == '__main__':
    W1 = PowerWheelArduino(debug=True);
    time.sleep(4)
    W1.write_steps('-400')
    time.sleep(4)
    W1.write_steps('500')    
    
    W1.close()
    pass