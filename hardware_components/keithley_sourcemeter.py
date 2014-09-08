'''
Created on 31.08.2014

@author: Benedikt
'''
#from . import HardwareComponent
import serial


KeithleyPort = 'COM4'
KeithleyBaudRate = 9600

class KeithleySourceMeterComponent(object): #object-->HardwareComponent
    
    name = None
    debug = False
    
    def setup(self):
        self.name = 'keithley_sourcemeter'
        self.debug = True
        
    def connect(self):
        self.ser = serial.Serial(port=KeithleyPort, baudrate = KeithleyBaudRate)#,  stopbits=1, xonxoff=0, rtscts=0, timeout=5.0       
        print 'connected to ',self.name
    

    def disconnect(self):
        self.ser.write('smua.source.output = smua.OUTPUT_OFF\n')
        self.ser.close()
        print 'disconnected ',self.name
        
        
        
        

        

