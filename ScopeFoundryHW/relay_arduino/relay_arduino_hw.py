'''
Created on Feb 6, 2017

@author: Alan Buckley
'''
from __future__ import division, absolute_import, print_function
from ScopeFoundry import HardwareComponent

import logging

logger = logging.getLogger(__name__)

try: 
    from ScopeFoundryHW.relay_arduino.relay_arduino_interface import RelayArduinoInterface
except Exception as err:
    logger.error("Cannot load required modules for RelayArduinoInterface, {}".format(err))

class RelayArduinoHW(HardwareComponent):
    
    name = 'relay_arduino_hw'
    
    def setup(self):
        self.port = self.settings.New(name="port", initial="COM3", dtype=str, ro=False)
        
        self.relay1 = self.settings.New(name="relay1", initial=0, dtype=bool, ro=False)
        self.relay2 = self.settings.New(name="relay2", initial=0, dtype=bool, ro=False)
        self.relay3 = self.settings.New(name="relay3", initial=0, dtype=bool, ro=False)
        self.relay4 = self.settings.New(name="relay4", initial=0, dtype=bool, ro=False)
    
    def connect(self):
        self.relay_interface = RelayArduinoInterface(port=self.port.val)
         
        self.relay1.connect_to_hardware(
            write_func = self.write_relay1)
        self.relay2.connect_to_hardware(
            write_func = self.write_relay2)
        self.relay3.connect_to_hardware(
            write_func = self.write_relay3)
        self.relay4.connect_to_hardware(
            write_func = self.write_relay4)

    
    def write_relay1(self, value):
        self.relay_interface.write_state(1, value)
    
    def write_relay2(self, value):
        self.relay_interface.write_state(2, value)
    
    def write_relay3(self, value):
        self.relay_interface.write_state(3, value)
    
    def write_relay4(self, value):
        self.relay_interface.write_state(4, value)
         
    def disconnect(self):
        self.settings.disconnect_all_from_hardware()
        if hasattr(self, 'relay_interface'):
            del self.relay_interface
        

