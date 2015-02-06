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

        # Created logged quantities
        self.points = self.add_logged_quantity('points', 
                                                   dtype=int,
                                                   ro=False,
                                                   vmin=1,
                                                   vmax=1e6,
                                                   unit='pixels')

        self.lines = self.add_logged_quantity('lines', 
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
        
        
        self.sample_rate = self.add_logged_quantity("sample_rate", dtype=float, ro=False, initial=5e5, vmin=1, vmax=2e6, unit='Hz')
        
        
        # connect GUI
        # no custom gui yet
        
        
    def connect(self):
        if self.debug_mode.val: print "connecting to {}".format(self.name)
        
        
        # Open connection to hardware                        
        #self.adc = Adc(channel='/Dev1/ai2', range=10, name=self.name, terminalConfig='rse')
        #self.adc.set_single()
        #self.adc.start()
        
        #self.sync_scan = Sync('X-6368/ao0:1', 'X-6368/ai1:3')
        #self.sync_scan.setup(rate, block, rate, block)


        #Connect lq to hardware
        #self.voltage.hardware_read_func = \
        #    self.read_adc_single



    def disconnect(self):
        #disconnect logged quantities from hardware
        #for lq in self.logged_quantities.values():
        #    lq.hardware_read_func = None
        #    lq.hardware_set_func = None
        
        #disconnect hardware
        #self.nanodrive.close()
        
        # clean up hardware object
        #del self.nanodrive
