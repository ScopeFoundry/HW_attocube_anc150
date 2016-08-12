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
        
        self.chan_addr = self.add_logged_quantity("chan_addr", dtype=str, initial='X-6368/ao0:1')
        self.v_min = self.settings.New("v_min", dtype=float, initial=-10, unit='V', si=False)
        self.v_max = self.settings.New("v_max", dtype=float, initial=+10, unit='V', si=False)

        self.x_dir = self.settings.New("x_dir", dtype=int, initial=+1, choices=[("Normal", 1,), ("Reversed", -1)])
        self.y_dir = self.settings.New("y_dir", dtype=int, initial=+1, choices=[("Normal", 1,), ("Reversed", -1)])

        self.v_min.updated_value.connect(self.on_v_min_max_change)
        self.v_max.updated_value.connect(self.on_v_min_max_change)
        self.on_v_min_max_change()
    
    def on_v_min_max_change(self):
        self.x_position.change_min_max(self.v_min.val, self.v_max.val)
    
    def connect(self):
        if self.debug_mode.val: print "connecting to NI Dac output task"

        self.chan_addr.change_readonly(True)

        # Open connection to hardware
        self.dac = Dac(self.chan_addr.val,'SEM_slowscan_dac_out')
        self.dac.start()

        # connect logged quantities
        self.x_position.hardware_set_func  = self.write_x
        self.y_position.hardware_set_func  = self.write_y

    def disconnect(self):
        if self.debug_mode.val: print "disconnecting from NI Dac output"
        
        self.chan_addr.change_readonly(False)

        #disconnect logged quantities from hardware
        for lq in self.settings.as_list():
            lq.hardware_read_func = None
            lq.hardware_set_func = None
        
        #disconnect hardware
        self.dac.close()
        # clean up hardware object
        del self.dac

    def write_x(self,x):
        self.write_xy(x, self.y_position.val)
    
    def write_y(self,y):
        self.write_xy(self.x_position.val, y)
        
    def write_xy(self, x, y):
        self.dac.set((self.x_dir.val*x,self.y_dir.val*y))
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
    