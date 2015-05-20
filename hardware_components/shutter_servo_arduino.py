'''
Created on Oct 27, 2014

@author: Edward Barnard
'''
from . import HardwareComponent

try:
    from equipment.shutter_servo_arduino import ShutterServoArduino
except Exception as err:
    print "Cannot load required modules for ShutterServoArduino:", err


SHUTTER_SERVO_ARDUINO_PORT = "COM23"

class ShutterServoHardwareComponent(HardwareComponent):
    
    def setup(self):
        self.name = 'shutter_servo'
        
        # Create logged quantities        
        self.angle = self.add_logged_quantity("angle", dtype=int, vmin=0, vmax=180, unit='deg')

        self.shutter_open = self.add_logged_quantity("shutter_open", dtype=bool,
                                                                choices = [
                                                                        ("Open", True),
                                                                        ("Closed", False)])

        # connect GUI
        self.shutter_open.connect_bidir_to_widget(self.gui.ui.shutter_open_checkBox)
        
        
    def connect(self):
        if self.debug_mode.val: print "connecting to shutter servo arduino"
        
        # Open connection to hardware
        self.shutter_servo = ShutterServoArduino(port=SHUTTER_SERVO_ARDUINO_PORT, debug=self.debug_mode.val)

        # connect logged quantities
        self.angle.hardware_read_func = \
                self.shutter_servo.read_position
        self.angle.hardware_set_func = \
                self.shutter_servo.write_posititon
        

        self.shutter_open.hardware_read_func = \
                self.shutter_servo.read_open
        self.shutter_open.hardware_set_func = \
                self.shutter_servo.move_open
                
        def set_debug(d):
            self.shutter_servo.debug = d
        self.debug_mode.hardware_set_func = set_debug
        
        #connect logged quantities together        
        self.shutter_open.updated_value[(None,)].connect(self.angle.read_from_hardware)

        
    def disconnect(self):
        
        #disconnect logged quantities from hardware
        for lq in self.logged_quantities.values():
            lq.hardware_read_func = None
            lq.hardware_set_func = None
        
        #disconnect hardware
        self.shutter_servo.close()
        
        # clean up hardware object
        del self.shutter_servo