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
            print("pixel 0: creating data arrays")
            spec_map_shape = self.scan_shape + winspec_readout.data.shape
            self.spec_map = np.zeros(spec_map_shape, dtype=np.float)
            self.spec_map_h5 = self.h5_meas_group.create_dataset('spec_map', spec_map_shape, dtype=np.float)
            self.h5_file.flush()
            
        if (pixel_num % 5) == 0:
            self.h5_file.flush()
        

        #self.roi_data = self.picam.cam.reshape_frame_data(dat)
        self.spec_map[k,j,i, :,:,:] = winspec_readout.data 
        self.spec_map_h5[k,j,i,:] = winspec_readout.data 

        self.display_image_map[k,j,i] = winspec_readout.data.sum()


    def post_scan_cleanup(self):
        winspec_readout = self.app.measurements.WinSpecRemoteReadout
        
        self.wavelength = winspec_readout.wls
        self.wavelength_h5 = self.h5_meas_group.create_dataset('wavelength', self.wavelength.shape, dtype=np.float)
        self.wavelength_h5[:] = self.wavelength[:]
        
        self.h5_file.flush()
        
    
    def update_display(self):
        MCLStage2DSlowScan.update_display(self)
        self.app.measurements.WinSpecRemoteReadout.update_display()

from ScopeFoundry.data_browser import DataBrowser, HyperSpectralBaseView
import h5py

class WinSpecMCL2DSlowScanView(HyperSpectralBaseView):

    name = 'WinSpecMCL2DSlowScan'
    
    def is_file_supported(self, fname):
        return "WinSpecMCL2DSlowScan.h5" in fname   
    
    
    def load_data(self, fname):    
        self.dat = h5py.File(fname, 'r')
        self.spec_map = np.squeeze(np.array(self.dat['/measurement/WinSpecMCL2DSlowScan/spec_map']), axis=(3,4))
        
        self.integrated_count_map =  self.spec_map.sum(axis=3)

        self.hyperspec_data = self.spec_map[0] # pick frame 0
        self.display_image = self.integrated_count_map[0]
        self.spec_x_array = self.dat['/measurement/WinSpecMCL2DSlowScan/wavelength']
        
    def scan_specific_setup(self):
        self.spec_plot.setLabel('left', 'Intensity', units='counts')
        self.spec_plot.setLabel('bottom', 'Wavelength', units='nm')        
        
