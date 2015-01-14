'''
Created on Sep 23, 2014

@author: Benedikt 
'''
from . import HardwareComponent
import time

try:
    from equipment.power_wheel_arduino import PowerWheelArduino
except Exception as err:
    print "Cannot load required modules for arduino power wheel:", err


PowerWheelArduinoPort = 'COM1'

class PowerWheelArduinoComponent(HardwareComponent): #object-->HardwareComponent
    
    name = 'power wheel arduino'
    debug = False
    
    def setup(self):
        self.debug = True

        # logged quantity        
        self.encoder_pos = self.add_logged_quantity('encoder_pos', 
                                                    dtype=int, unit='steps', 
                                                    si=False, ro=True)
        self.move_steps  = self.add_logged_quantity('move_steps',  
                                                    dtype=int, unit='steps',
                                                    vmin=1, vmax=3200, initial=10,  
                                                    si=False, ro=False)
        self.speed       = self.add_logged_quantity("speed", 
                                                    dtype=int, unit='steps/sec', 
                                                    vmin=1, vmax=1000, initial=100, 
                                                    si=True, ro=False)


        #  operations
        self.add_operation("zero_encoder", self.zero_encoder)
        self.add_operation("move_fwd", self.move_fwd)
        self.add_operation("move_bkwd", self.move_bkwd)


        # connect to gui
        self.move_steps.connect_bidir_to_widget(self.gui.ui.powerwheel_move_steps_doubleSpinBox)
        self.gui.ui.powerwheel_move_fwd_pushButton.clicked.connect(self.move_fwd)
        self.gui.ui.powerwheel_move_bkwd_pushButton.clicked.connect(self.move_bkwd)

    def connect(self):
        if self.debug: print "connecting to arduino power wheel"
        
        # Open connection to hardware
        self.power_wheel = PowerWheelArduino(port='COM16', debug=self.debug_mode.val)
        
        # connect logged quantities
        self.encoder_pos.hardware_set_func = \
             self.power_wheel.write_steps
        self.encoder_pos.hardware_read_func= \
             self.power_wheel.read_encoder

        self.speed.hardware_set_func = \
            self.power_wheel.write_speed
        self.speed.hardware_read_func = \
            self.power_wheel.read_speed

        print 'connected to ',self.name
    

    def disconnect(self):

        # disconnect logged quantities from hardware
        # ///\
    
        #disconnect hardware
        self.power_wheel.close()
        
        # clean up hardware object
        del self.power_wheel
        
        print 'disconnected ',self.name
        
    #@QtCore.Slot()
    def move_fwd(self):
        #self.power_wheel.write_steps(self.move_steps.val)
        t0 = time.time()
        self.power_wheel.write_steps_and_wait(self.move_steps.val)
        print time.time() - t0, "sec for", self.move_steps.val, "steps"
        self.power_wheel.read_status()
        self.encoder_pos.read_from_hardware()
        
    #@QtCore.Slot()
    def move_bkwd(self):
        self.power_wheel.write_steps_and_wait(-1 * self.move_steps.val)
        time.sleep(0.2)
        #TODO really should wait until done

        self.encoder_pos.read_from_hardware()

    #@QtCore.Slot()
    def zero_encoder(self):
        self.power_wheel.write_zero_encoder()
        self.encoder_pos.read_from_hardware()
