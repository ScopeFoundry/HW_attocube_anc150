'''
Created on Jul 12, 2016

@author: Daniel B. Durham
'''
from ScopeFoundry.scanning import BaseRaster2DSlowScan
import numpy as np
import time
#Sofia imports
from ScopeFoundry import Measurement
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

#Single Auger Map for now, will extend to range of energies later

class AugerSlowMap(BaseRaster2DSlowScan):
    
    name = "AugerSlowMap"
    def __init__(self,app):
        BaseRaster2DSlowScan.__init__(self, app, h_limits=(-10,10), v_limits=(-10,10), h_unit="V", v_unit="V")        
    
    def scan_specific_setup(self):
        #Hardware
        self.stage = self.app.hardware['sem_slowscan_vout_stage']
        self.singlechan_signal = self.app.hardware['sem_singlechan_signal']
        self.dualchan_signal = self.app.hardware['sem_dualchan_signal']
        self.e_analyzer = self.app.hardware['auger_electron_analyzer']
        self.counter_dac_hc = self.app.hardware['Counter_DAC_FPGA_VI_HC']

    def move_position_start(self, x,y):
        self.stage.settings['x_position'] = x
        self.stage.settings['y_position'] = y
        
    def move_position_slow(self, x,y, dx,dy):
        self.stage.settings['x_position'] = x
        self.stage.settings['y_position'] = y
        
    def move_position_fast(self, x,y, dx,dy):
        #self.stage.settings['x_position'] = x
        #self.stage.settings['y_position'] = y
        self.stage.dac.set((x,-1*y))
        
    def pre_scan_setup(self):
        #Set up hdf5 datasets for SEM images and spectral maps
        H = self.h5_meas_group
        self.in_lens_data_h5 = H.create_dataset('in_lens', self.scan_shape, dtype=np.float)
        self.se2_data_h5 = H.create_dataset('se2', self.scan_shape, dtype=np.float)
        self.spec_map = np.zeros(self.scan_shape + (7,), dtype=np.float)
        self.spec_map_h5 = H.create_dataset('spec_map', self.scan_shape + (7,), dtype=np.float)
        #Also create a channel for number of FIFO elements read
        self.fpga_num_elements_h5 = H.create_dataset('fpga_num_elements',self.scan_shape,dtype=np.int)
        
        self.counter_dac_hc.engage_FIFO()
        
        #Perform an initial FIFO flush
        self.counter_dac_hc.flush_FIFO()

        self.t0 = time.time()
        
    def collect_pixel(self, pixel_num, k, j, i):
        # collect data
        # store in arrays
        
        
        #inlens = self.app.hardware['sem_dualchan_signal'].settings.inLens_signal.read_from_hardware()
        #sig = se2 = self.app.hardware['sem_dualchan_signal'].settings.se2_signal.read_from_hardware()
        se2, inlens = self.app.hardware['sem_dualchan_signal'].read_signals()
        
        buf_reshaped, read_elements = self.counter_dac_hc.read_FIFO(return_read_elements=True)
        
        #Store the seven analyzer channels in counts/s
        dwell_time = self.counter_dac_hc.settings['counter_ticks']/40e6 #assume 40MHz FPGA clock
        spec = (np.mean(buf_reshaped[0:7,:],axis=1))/dwell_time
        self.spec_map[k,j,i, :] =  spec        
        
        #Save the data to disk
        if self.settings['save_h5']:
            self.in_lens_data_h5[k,j, i] = inlens
            self.se2_data_h5[k,j,i] = se2
            self.spec_map_h5[k,j,i,:] = spec[0:7]
            self.fpga_num_elements_h5[k,j,i] = read_elements
        
       
        #self.display_image_map[k,j,i] = sig

        t1 = time.time()
        print "pixel", pixel_num, "time", t1 - self.t0, "sec"
        self.t0 = t1 

    def post_scan_cleanup(self):
        #Flush the FIFO Counter
        self.counter_dac_hc.disengage_FIFO()
        
        print(self.name, "post_scan_cleanup")
        #import scipy.io
        #scipy.io.savemat(file_name="%i_%s.mat" % (self.t0, self.name), mdict=dict(spec_map=self.spec_map))
    
#     def update_display(self):
#         BaseRaster2DSlowScan.update_display(self)
        
        #self.app.measurements.picam_readout.roi_data = self.roi_data
        #self.app.measurements.picam_readout.update_display()
        
        
    #Begin Sofia's Edits
    def setup_figure(self):
        BaseRaster2DSlowScan.setup_figure(self)
        
        self.graph_layout2=pg.GraphicsLayoutWidget(border=(100,100,100))
        self.graph_layout2.show()
        self.graph_layout2.setWindowTitle('pyqtgraph example: ImageItem')
        self.ui.plot_groupBox.layout().addWidget(self.graph_layout2)
              
        plot_pos = np.array([[0,0],[0,1],[0,2],[1,0],[1,1],[1,2],[2,0],[2,1],[2,2]])
        self.img_plots = []
        self.img_items = []
        for i in range(9):
            img_plot = self.graph_layout2.addPlot(row=plot_pos[i,0], col=plot_pos[i,1])
            img_item = pg.ImageItem()
            img_plot.addItem(img_item)
            img_plot.showGrid(x=True, y=True)
            img_plot.setAspectLocked(lock=True, ratio=1)
            self.img_plots.append(img_plot)
            self.img_items.append(img_item)
           
        self.hist_lut2 = pg.HistogramLUTItem()
        self.graph_layout2.addItem(self.hist_lut2, colspan=1, rowspan=3, col=3,row=0)
        self.hist_lut2.setImageItem(self.img_items[0])
        #self.hist_lut.vb.setLimits(yMin=0, yMax=1)
        self.hist_lut2.sigLookupTableChanged.connect(self.on_Lookup_Table_Changed)
        self.hist_lut2.sigLevelsChanged.connect(self.on_Lookup_Table_Changed)
        
        """        ##########Taken from setup_figure in BaseRaster2DSlowScan class###########
        
        #self.clear_qt_attr('current_stage_pos_arrow')
        self.current_stage_pos_arrow = pg.ArrowItem()
        self.current_stage_pos_arrow.setZValue(100)
        #for i in range(9):
        self.img_plots[0].addItem(self.current_stage_pos_arrow)
        
        #self.stage = self.app.hardware_components['dummy_xy_stage']
        self.stage.x_position.updated_value.connect(self.update_arrow_pos, QtCore.Qt.UniqueConnection)
        self.stage.y_position.updated_value.connect(self.update_arrow_pos, QtCore.Qt.UniqueConnection)
        
        self.stage.x_position.connect_bidir_to_widget(self.ui.x_doubleSpinBox)
        self.stage.y_position.connect_bidir_to_widget(self.ui.y_doubleSpinBox)

        
        self.graph_layout.nextRow()
        self.pos_label = pg.LabelItem(justify='right')
        self.pos_label.setText("=====")
        self.graph_layout.addItem(self.pos_label)

        self.scan_roi = pg.ROI([0,0],[1,1], movable=True)
        self.scan_roi.addScaleHandle([1, 1], [0, 0])
        self.scan_roi.addScaleHandle([0, 0], [1, 1])
        self.update_scan_roi()
        self.scan_roi.sigRegionChangeFinished.connect(self.mouse_update_scan_roi)
        
        self.img_plots[0].addItem(self.scan_roi)        
        for lqname in 'h0 h1 v0 v1 dh dv'.split():
            self.settings.as_dict()[lqname].updated_value.connect(self.update_scan_roi)
        for i in range(9):
            self.img_plots[i].scene().sigMouseMoved.connect(self.mouseMoved)
       ###########END#######"""
       
       
    def on_Lookup_Table_Changed(self):
        for i in range(9):
            self.img_items[i].setLookupTable(self.hist_lut2.getLookupTable)
            self.img_items[i].setLevels(self.hist_lut2.region.getRegion())
               
    def update_display(self):
        kk, jj, ii = self.current_scan_index
        
        self.display_image_map = np.sum(self.spec_map, axis=3)
    
        
        #self.display_image_map = self.in_lens_data_h5[kk,:,:]
        BaseRaster2DSlowScan.update_display(self)

        
         
    #         self.vLine.setPos(self.history_i)
    #         self.plot_lines[0].setData(self.randomnumbers)
        for ii in range(7):
            self.img_items[ii].setImage(self.spec_map[kk,:,:, ii].T)
    #         for i in range(9):
    #             self.img_items[i].setImage(self.imageA[i].T)

        self.img_items[7].setImage(self.in_lens_data_h5[kk,:,:].T)
        self.img_items[8].setImage(self.se2_data_h5[kk,:,:].T)
        self.app.qtapp.processEvents()
        
    def mouseMoved(self,evt):
        pass
#         for i in range(9):
#             mousePoint = self.img_plots[i].vb.mapSceneToView(evt)
#             self.pos_label.setText(
#                 "H {:+02.2f} um [{}], V {:+02.2f} um [{}]: {:1.2e} Hz".format(
#                             mousePoint.x(), 0, mousePoint.y(), 0, 0))

        
        
        