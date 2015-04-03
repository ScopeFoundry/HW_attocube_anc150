'''
Created on Feb 4, 2015

@author: NIuser
'''
from hardware_components import HardwareComponent
try:
    from equipment.SEM.raster_generator import RasterGenerator
    from equipment.NI_Daq import Sync
except Exception as err:
    print "could not load modules needed for AttoCubeECC100:", err




class SemRasterScanner(HardwareComponent):
    
    name = 'sem_raster_scanner'

    def setup(self):
        self.display_update_period = 0.050 #seconds

        # Created logged quantities
        self.points = self.add_logged_quantity('points', initial=1024,
                                                   dtype=int,
                                                   ro=False,
                                                   vmin=1,
                                                   vmax=1e6,
                                                   unit='pixels')

        self.lines = self.add_logged_quantity('lines', initial=1024,
                                                   dtype=int,
                                                   ro=False,
                                                   vmin=1,
                                                   vmax=1e6,
                                                   unit='pixels')



        lq_params = dict(  dtype=float, ro=False,
                           initial = 0,
                           vmin=-50,
                           vmax=50,
                           unit='%')
        self.xoffset = self.add_logged_quantity('xoffset', **lq_params)
        self.yoffset = self.add_logged_quantity('yoffset', **lq_params)

        lq_params = dict(  dtype=float, ro=False,
                           initial = 100,
                           vmin=-100,
                           vmax=100,
                           unit='%')        
        self.xsize = self.add_logged_quantity("xsize", **lq_params)
        self.ysize = self.add_logged_quantity("ysize", **lq_params)
        
        self.angle = self.add_logged_quantity("angle", dtype=float, ro=False, initial=0, vmin=-180, vmax=180, unit="deg")
        
        
        self.sample_rate = self.add_logged_quantity("sample_rate", dtype=float, 
                                                    ro=False, 
                                                    initial=2e6, 
                                                    vmin=1, 
                                                    vmax=2e6,
                                                    unit='Hz')
        
        self.output_rate = self.add_logged_quantity("output_rate", dtype=float, 
                                                    ro=True, 
                                                    initial=5e5, 
                                                    vmin=1, 
                                                    vmax=2e6,
                                                    unit='Hz')
        
        self.sample_per_point = self.add_logged_quantity("sample_per_point", dtype=int, 
                                                    ro=False, 
                                                    initial=1, 
                                                    vmin=1, 
                                                    vmax=100,
                                                    unit='samples')
        
        self.ms_per_unit=self.add_logged_quantity("ms_per_unit",dtype=float,
                                                  ro=False)
        
        self.unit_of_rate=self.add_logged_quantity("unit_of_rate",dtype=int,
                                                   ro=False,
                                                   initial=0,
                                                   choices=[('ms/pixel',0),('ms/line',1),('ms/frame',2)])
        
        self.output_channel_names= self.add_logged_quantity("output_channel_names",dtype=str,
                                                        ro=False,
                                                        initial='X-6368/ao0:1')
        
        self.input_channel_names= self.add_logged_quantity("input_channel_names",dtype=str,
                                                        ro=False,
                                                        initial='X-6368/ai1:3')
        
        self.counter_channel_names= self.add_logged_quantity("counter_channel_names",dtype=str,
                                                        ro=False,
                                                        initial='X-6368/ctr0,X-6368/ctr1')
        
        self.counter_channel_terminals= self.add_logged_quantity("counter_channel_terminals",dtype=str,
                                                        ro=False,
                                                        initial='PFI0,PFI12')
        #connect events
        
        self.points.connect_bidir_to_widget(self.gui.ui.points_doubleSpinBox)
        self.lines.connect_bidir_to_widget(self.gui.ui.lines_doubleSpinBox)
        self.xoffset.connect_bidir_to_widget(self.gui.ui.xoffset_doubleSpinBox)
        self.yoffset.connect_bidir_to_widget(self.gui.ui.yoffset_doubleSpinBox)
        self.xsize.connect_bidir_to_widget(self.gui.ui.xsize_doubleSpinBox)
        self.ysize.connect_bidir_to_widget(self.gui.ui.ysize_doubleSpinBox)
        self.angle.connect_bidir_to_widget(self.gui.ui.angle_doubleSpinBox)
        self.sample_rate.connect_bidir_to_widget(self.gui.ui.sample_rate_doubleSpinBox)
        self.sample_per_point.connect_bidir_to_widget(self.gui.ui.sample_per_point_doubleSpinBox)     
        
    def connect(self):
        if self.debug_mode.val: print "connecting to {}".format(self.name)
        
        self.raster_gen = RasterGenerator(points=self.points.val, lines=self.lines.val, 
                                          xoffset=self.xoffset.val, yoffset=self.yoffset.val,
                                          xsize=self.xsize.val, ysize=self.ysize.val,
                                          angle=self.angle.val)
        
        # need to update values based on clipping
        
        self.xy_raster_volts = self.raster_gen.data()
        self.num_pixels = self.raster_gen.count()
        self.num_samples= self.num_pixels *self.sample_per_point.val
       
        #setup tasks
        #while self.continuous_scan.val==1:
        self.sync_analog_io = Sync(self.output_channel_names.val,self.input_channel_names.val,self.counter_channel_names.val.split(','),self.counter_channel_terminals.val.split(','))
        self.ctr_num=2
        '''
        from sample per point and sample rate, calculate the output(scan rate)
        '''
        self.output_rate.val=self.sample_rate.val/self.sample_per_point.val
        
        #self.sync_analog_io.setup(rate_out=self.sample_rate.val, count_out=self.num_pixels, 
        #                          rate_in=self.sample_rate.val, count_in=self.num_pixels )
        self.sync_analog_io.setup(self.output_rate.val, int(self.num_pixels), self.sample_rate.val, int(self.num_samples),is_finite=True)

    def disconnect(self):
        #disconnect logged quantities from hardware
        #for lq in self.logged_quantities.values():
        #    lq.hardware_read_func = None
        #    lq.hardware_set_func = None
        self.sync_analog_io.close()
        del self.sync_analog_io
        #disconnect hardware
        #self.nanodrive.close()
        
        # clean up hardware object
        #del self.nanodrive
