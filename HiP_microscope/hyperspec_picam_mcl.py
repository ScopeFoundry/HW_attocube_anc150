from __future__ import division, print_function
import numpy as np
from ScopeFoundry.scanning.xy_scan_base import BaseXYSlowScan

class HyperSpecXYScan(BaseXYSlowScan):
    
    name = "hyerpspec_picam"
    
    def scan_specific_setup(self):
        #Hardware
        self.stage = self.gui.hardware.mcl_xyz_stage
        self.picam = self.gui.hardware.picam    
    
    
    
    def pre_scan_setup(self):
        self.spec_map = self.h5_meas_group.create_dataset('spec_map', (self.Nv.val, self.Nh.val, 1340), dtype=float)

    def move_position_start(self, x,y):
        #self.stage.y_position.update_value(x)
        #self.stage.y_position.update_value(y)
        self.stage.nanodrive.set_pos_slow(x,y,None)
    
    def move_position_line(self, x,y):
        #self.stage.y_position.update_value(y)
        self.stage.nanodrive.set_pos_ax(x, 1)
        self.stage.nanodrive.set_pos_ax(y, 2)

        
    def move_position_pixel(self, x,y):
        #self.stage.x_position.update_value(x)
        self.stage.nanodrive.set_pos_ax(x, 1)        

    def collect_pixel(self, i_h, i_v):
        pass
        dat = self.picam.cam.acquire(readout_count=1, readout_timeout=-1)
            
        self.roi_data = self.picam.cam.reshape_frame_data(dat)
        self.spec_map[i_v, i_h, :] = self.roi_data.sum(axis=1)
        
        self.display_image_map[i_h, i_v] = np.sum(self.roi_data)

    def post_scan_cleanup(self):
        #H['spec_map'] = self.h_array
        pass
    
    def update_display(self):
        BaseXYSlowScan.update_display(self)
        
        self.app.measurements.picam_readout.roi_data = self.roi_data
        self.app.measurements.picam_readout.update_display()
    
    