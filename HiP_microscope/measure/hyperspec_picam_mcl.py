from __future__ import division, print_function
import numpy as np
from ScopeFoundry.scanning.base_cartesian_scan import BaseCartesian2DSlowScan
from ScopeFoundry import Measurement, LQRange
import time

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
        
        print(self.name, "post_scan_cleanup")
        import scipy.io
        scipy.io.savemat(file_name="%i_%s.mat" % (self.t0, self.name), mdict=dict(spec_map=self.spec_map))

    def update_display(self):
        BaseCartesian2DSlowScan.update_display(self)
        
        self.app.measurements.picam_readout.roi_data = self.roi_data
        self.app.measurements.picam_readout.update_display()
    

class HyperSpecPicam3DStack(Measurement):
    
    name = 'HyperSpecPicam3DStack'
    
    def setup(self):
        lq_params = dict(dtype=float, vmin=0,vmax=100, ro=False, unit='um' )
        self.z0 = self.settings.New('z0',  initial=20, **lq_params  )
        self.z1 = self.settings.New('z1',  initial=30, **lq_params  )
        lq_params = dict(dtype=float, vmin=1e-9,vmax=100, ro=False, unit='um' )
        self.dz = self.settings.New('dz', initial=1, **lq_params)
        self.Nz = self.settings.New('Nz', dtype=int, initial=10, vmin=1)
        
        self.z_range = LQRange(min_lq=self.z0, max_lq=self.z1, step_lq=self.dz, num_lq=self.Nz)
    
    def run(self):
        
        self.scan2d = self.app.measurements["hyperspec_picam_mcl"]
        self.stage = self.app.hardware['mcl_xyz_stage']

        for kk, z in enumerate(self.z_range.array):
            if self.interrupt_measurement_called:
                self.scan2d.interrupt()
                break
            
            print(self.name, kk, z)
                        
            self.stage.settings['z_target'] = z
            time.sleep(1.)
            
            self.scan2d.start()
            while self.scan2d.is_measuring():
                if self.interrupt_measurement_called:
                    self.scan2d.interrupt()
                    break
                time.sleep(0.1)
        
    def update_display(self):
        self.scan2d.update_display()
        