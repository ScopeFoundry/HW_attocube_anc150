'''
Created on Feb 4, 2015

@author: NIuser
'''

from measurement_components.measurement import Measurement


class SemRasterRepScan(Measurement):

    name = "sem_raster_rep_scan"
    
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
        
        
        self.sample_rate = self.add_logged_quantity("sample_rate", dtype=float, ro=False, initial=5e5, vmin=1, vmax=2e6, unit='Hz')
        self.continuous_scan = self.add_logged_quantity("continuous_scan", dtype=int, ro=False, initial=0, vmin=0, vmax=1, unit='',
                                                        choices=[('Off',0),('On',1)])
        
        #connect events
        self.gui.ui.sem_raster_start_pushButton.clicked.connect(self.start)
        self.gui.ui.sem_raster_interrupt_pushButton.clicked.connect(self.interrupt)
        
        self.xoffset.connect_bidir_to_widget(self.gui.ui.xoffset_doubleSpinBox)
        self.yoffset.connect_bidir_to_widget(self.gui.ui.yoffset_doubleSpinBox)
        self.xsize.connect_bidir_to_widget(self.gui.ui.xsize_doubleSpinBox)
        self.ysize.connect_bidir_to_widget(self.gui.ui.ysize_doubleSpinBox)
        self.angle.connect_bidir_to_widget(self.gui.ui.angle_doubleSpinBox)
        self.sample_rate.connect_bidir_to_widget(self.gui.ui.sample_rate_doubleSpinBox)
    def setup_figure(self):
        self.fig = self.gui.add_figure('sem_raster', self.gui.ui.sem_raster_plot_widget)


    def _run(self):
        from equipment.SEM.raster_generator import  RasterGenerator
        from equipment.NI_Daq import Sync

        self.raster_gen = RasterGenerator(points=self.points.val, lines=self.lines.val, 
                                          xoffset=self.xoffset.val, yoffset=self.yoffset.val,
                                          xsize=self.xsize.val, ysize=self.ysize.val,
                                          angle=self.angle.val)
        
        # need to update values based on clipping
        
        self.xy_raster_volts = self.raster_gen.data()
        self.num_pixels = self.raster_gen.count()
       
        #setup tasks
        while self.continuous_scan.val==1:
            self.sync_analog_io = Sync('X-6368/ao0:1', 'X-6368/ai1:3')
        
        #self.sync_analog_io.setup(rate_out=self.sample_rate.val, count_out=self.num_pixels, 
        #                          rate_in=self.sample_rate.val, count_in=self.num_pixels )
            self.sync_analog_io.setup(self.sample_rate.val, int(self.num_pixels), self.sample_rate.val, int(self.num_pixels),is_finite=True)
        
       
            self.sync_analog_io.out_data(self.xy_raster_volts)
        
        #for i in range(2):
            self.sync_analog_io.start()
            self.adc_data = self.sync_analog_io.read_buffer(timeout=10)

        
            in3 = self.adc_data[::3]
            in1 = self.adc_data[1::3]
            in2 = self.adc_data[2::3]
            out1 = self.xy_raster_volts[::2]
            out2 = self.xy_raster_volts[1::2]

            out1 = out1.reshape(self.raster_gen.shape())
            out2 = out2.reshape(self.raster_gen.shape())
            in1 = in1.reshape(self.raster_gen.shape())
            in2 = in2.reshape(self.raster_gen.shape())
            in3 = in3.reshape(self.raster_gen.shape())

            self.sem_image = in3
            #self.update_display()
        
    def update_display(self):        
        #print "updating figure"
        #self.fig.clf()
        
        if not hasattr(self,'ax'):
            self.ax = self.fig.add_subplot(111)
            
        if not hasattr(self, 'img'):
            self.img = self.ax.imshow(self.sem_image)

        self.img.set_data(self.sem_image)

        self.fig.canvas.draw()
        
        