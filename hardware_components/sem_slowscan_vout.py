'''
Created on Oct 29, 2015

@author: NIuser
'''
import ScopeFoundry
from ScopeFoundry import HardwareComponent
from equipment.NI_Daq import Dac
import random



class SEMSlowscanVoutStage(HardwareComponent):
    
    name = "sem_slowscan_vout_stage"
    
    def setup(self):
        lq_params = dict(  dtype=float, ro=False,
                           initial = 0,
                           vmin=-10,
                           vmax=10,
                           si = False,
                           unit='V')
        self.x_position = self.add_logged_quantity("x_position", **lq_params)
        self.y_position = self.add_logged_quantity("y_position", **lq_params)       

        self.x_position.reread_from_hardware_after_write = False
        self.x_position.spinbox_decimals = 3
        
        self.y_position.reread_from_hardware_after_write = False
        self.y_position.spinbox_decimals = 3
        
#        self.x_chan = self.add_logged_quantity('x_chan', dtype=str, initial='/X')

    def connect(self):
        if self.debug_mode.val: print "connecting to NI Dac output task"

        # Open connection to hardware
        self.dac = Dac('X-6368/ao0:1','SEM_slowscan_dac_out')
        self.dac.start()

        # connect logged quantities
        self.x_position.hardware_set_func  = self.write_x
        self.y_position.hardware_set_func  = self.write_y

    def disconnect(self):
        if self.debug_mode.val: print "disconnecting from NI Dac output"
        
        #disconnect logged quantities from hardware
        for lq in self.logged_quantities.values():
            lq.hardware_read_func = None
            lq.hardware_set_func = None
        
        #disconnect hardware
        self.dac.close()
        # clean up hardware object
        del self.dac

    def write_x(self,val):
        self.dac.set((val,-1*self.y_position.val))

    def write_y(self,val):
        self.dac.set((self.x_position.val,-1*val))
        
    def write_xy(self, x, y):
        self.dac.set((x,-1*y))
        #self.x_position.update_value(x, update_hardware=False)
        #self.y_position.update_value(y, update_hardware=False)
        
if __name__ == '__main__':
    from PySide import QtGui
    import sys
    
    
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("sem_slowscan_vout")
    
    gui = ScopeFoundry.BaseMicroscopeGUI(app)
    gui.show()
    
    sem_slowscan_vout = SEMSlowscanVout(gui)
    
    
    
    sys.exit(app.exec_())    
    