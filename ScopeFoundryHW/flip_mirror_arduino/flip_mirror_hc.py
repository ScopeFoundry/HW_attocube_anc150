'''
Created on Jun 27, 2014

@author: Edward Barnard
'''
from __future__ import division, absolute_import, print_function
from ScopeFoundry import HardwareComponent

try:
    from .flip_mirror_arduino_interface import FlipMirrorArduino
except Exception as err:
    print("Cannot load required modules for FlipMirrorArduino:", err)


FLIP_MIRROR_PORT = "COM8"

class FlipMirrorHW(HardwareComponent):
    
    def setup(self):
        self.name = 'flip_mirror'
        self.debug = False
        
        # Create logged quantities        
        self.flip_mirror_position = self.add_logged_quantity("mirror_position", dtype=bool,
                                                                choices = [
                                                                        ("Spectrometer", 0),
                                                                        ("APD", 1)]
                                                             )
        self.POSITION_SPEC = False
        self.POSITION_APD = True
        
        # connect GUI
        if hasattr(self.gui.ui, 'flip_mirror_checkBox'):
            self.flip_mirror_position.connect_bidir_to_widget(self.gui.ui.flip_mirror_checkBox)
        
    def connect(self):
        if self.debug: self.log.debug( "connecting to flip mirror arduino")
        
        # Open connection to hardware
        self.flip_mirror = FlipMirrorArduino(port=FLIP_MIRROR_PORT, debug=True)

        # connect logged quantities
        self.flip_mirror_position.hardware_read_func = \
                self.flip_mirror.read_position
        self.flip_mirror_position.hardware_set_func = \
                self.flip_mirror.write_posititon
        

        
        
    def disconnect(self):
        
        #disconnect logged quantities from hardware
        self.settings.disconnect_all_from_hardware()
        
        if hasattr(self, 'flip_mirror'):
            #disconnect hardware
            self.flip_mirror.close()
            
            # clean up hardware object
            del self.flip_mirror
