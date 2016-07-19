from __future__ import division, print_function
import numpy as np
from measurement_components.mcl_stage_slowscan import MCLStage2DSlowScan
from ScopeFoundry import Measurement, LQRange
import time

class WinSpecMCL2DSlowScan(MCLStage2DSlowScan):
    
    name = "WinSpecMCL2DSlowScan"
    
    def scan_specific_setup(self):
        #Hardware
        self.stage = self.gui.hardware.mcl_xyz_stage
        self.winspec_hc = self.app.hardware.WinSpecRemoteClient

    
    def pre_scan_setup(self):
        self.winspec_client = self.winspec_hc.winspec_client       

    def collect_pixel(self, pixel_num, k, j, i):
        # collect data
        # store in arrays        
        
        winspec_readout = self.app.measurements.WinSpecRemoteReadout
        
        winspec_readout.run()
        
        if pixel_num == 0:
            spec_map_shape = self.scan_shape + winspec_readout.data.shape
            self.spec_map = np.zeros(spec_map_shape, dtype=np.float)
            self.spec_map_h5 = self.h5_meas_group.create_dataset('spec_map', spec_map_shape, dtype=np.float)
            
        

        #self.roi_data = self.picam.cam.reshape_frame_data(dat)
        self.spec_map[k,j,i, :,:,:] = winspec_readout.data 
        self.spec_map_h5[k,j,i,:] = winspec_readout.data 

        self.display_image_map[k,j,i] = winspec_readout.data.sum()


    def post_scan_cleanup(self):
        #H['spec_map'] = self.h_array
        #print(self.name, "post_scan_cleanup")
        #import scipy.io
        #scipy.io.savemat(file_name="%i_%s.mat" % (self.t0, self.name), mdict=dict(spec_map=self.spec_map))
        pass
    
    def update_display(self):
        MCLStage2DSlowScan.update_display(self)
        self.app.measurements.WinSpecRemoteReadout.update_display()
