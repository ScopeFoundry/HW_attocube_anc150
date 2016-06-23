from __future__ import division, print_function
import numpy as np
from ScopeFoundry.scanning.base_cartesian_scan import BaseCartesian2DSlowScan

class HyperSpecPicam2DScan(BaseCartesian2DSlowScan):
    
    name = "hyperspec_picam_mcl"
    
    def scan_specific_setup(self):
        #Hardware
        self.stage = self.gui.hardware.mcl_xyz_stage
        self.picam = self.gui.hardware.picam    

    def move_position_start(self, x,y):
        #self.stage.y_position.update_value(x)
        #self.stage.y_position.update_value(y)
        self.stage.nanodrive.set_pos_slow(x,y,None)
    
    def move_position_slow(self, x,y, dx,dy):
        #self.stage.y_position.update_value(y)
        self.stage.nanodrive.set_pos_slow(x,y,None)
        self.stage.x_position.read_from_hardware()
        self.stage.y_position.read_from_hardware()

    def move_position_fast(self, x,y, dx,dy):
        #self.stage.x_position.update_value(x)
        self.stage.nanodrive.set_pos(x, y, None)            
    
    def pre_scan_setup(self):
        self.spec_map = np.zeros(self.scan_shape + (1340,), dtype=np.float)
        self.spec_map_h5 = self.h5_meas_group.create_dataset('spec_map', self.scan_shape + (1340,), dtype=np.float)

    def collect_pixel(self, pixel_num, k, j, i):
        # collect data
        # store in arrays        
        dat = self.picam.cam.acquire(readout_count=1, readout_timeout=-1)
            
        self.roi_data = self.picam.cam.reshape_frame_data(dat)
        self.spec_map[k,j,i, :] = spec =  self.roi_data[0].sum(axis=0)
        
        self.spec_map_h5[k,j,i,:] = spec
        
        self.display_image_map[k,j,i] = np.sum(spec)

    def post_scan_cleanup(self):
        #H['spec_map'] = self.h_array
        pass
    
    def update_display(self):
        BaseCartesian2DSlowScan.update_display(self)
        
        self.app.measurements.picam_readout.roi_data = self.roi_data
        self.app.measurements.picam_readout.update_display()
    
    