import numpy as np
import time
from PySide import QtCore, QtGui
import pyqtgraph as pg
import random

from ScopeFoundry import Measurement 
from measurement_components.base_3d_scan import Base3DScan
from measurement_components.base_2d_scan import Base2DScan

class APDConfocalScanMeasurement(Base2DScan):
    
    name = "apd_confocal"
           
    def scan_specific_setup(self):
        
        self.int_time = self.gui.apd_counter_hc.int_time
        self.display_update_period = 0.02 #seconds

        #connect events
        self.gui.ui.scan_apd_start_pushButton.clicked.connect(self.start)
        self.gui.ui.scan_apd_stop_pushButton.clicked.connect(self.interrupt)
        
        self.int_time = self.gui.apd_counter_hc.int_time
        
        # local logged quantities

        # connect to gui
        self.gui.ui.scan_apd_start_pushButton.clicked.connect(self.start)
        self.gui.ui.scan_apd_stop_pushButton.clicked.connect(self.interrupt)
        self.gui.ui.clearfig_pushButton.setEnabled(True)
        self.gui.ui.clearfig_pushButton.clicked.connect(self.setup_figure)

    def setup_figure(self):
        self.display_update_period = 0.02 #seconds
        self.initial_scan_setup_plotting = False

        #2D scan area
        """self.fig2d = self.gui.add_figure('2d', self.gui.ui.plot2d_widget)
        self.fig2d.clf()
        
        self.ax2d = self.fig2d.add_subplot(111)
        self.ax2d.plot([0,1])

        self.ax2d.set_xlim(0, 100)
        self.ax2d.set_ylim(0, 100)
                    
        self.fig2d.canvas.mpl_connect('button_press_event', self.on_fig2d_click)
        """

        # new pyqtgraph fig
        if hasattr(self, 'img_view'):
            self.img_view.deleteLater() # see http://stackoverflow.com/questions/9899409/pyside-removing-a-widget-from-a-layout
            del self.img_view
        #self.img_view = pg.ImageView()
        #self.gui.ui.plot2d_widget.layout().addWidget(self.img_view)

        if hasattr(self, 'graph_layout'):
            self.graph_layout.deleteLater() # see http://stackoverflow.com/questions/9899409/pyside-removing-a-widget-from-a-layout
            del self.graph_layout
        self.graph_layout=pg.GraphicsLayoutWidget(border=(100,100,100))
        self.gui.ui.plot2d_widget.layout().addWidget(self.graph_layout)
        
        
        self.img_plot = self.graph_layout.addPlot()
        #self.img_plot.getViewBox().setLimits(minXRange=-10, maxXRange=100, minYRange=-10, maxYRange=100)

        self.img_item = pg.ImageItem()
        self.img_plot.addItem(self.img_item)

        #self.stage_pos_arrow = pg.ArrowItem() 
        #self.img_plot.addItem(self.stage_pos_arrow)
        
        #self.gui.mcl_xyz_stage_hc.x_position.updated_value[float].connect(self.stage_pos_arrow.setX)
        #self.gui.mcl_xyz_stage_hc.y_position.updated_value[float].connect(self.stage_pos_arrow.setY)
        
        
        self.current_pixel_arrow = pg.ArrowItem()
        self.current_pixel_arrow.setZValue(100)
        self.img_plot.addItem(self.current_pixel_arrow)
        
        self.img_plot.showGrid(x=True, y=True)
        self.img_plot.setAspectLocked(lock=True, ratio=1)
        
        
        self.hist_lut = pg.HistogramLUTItem()
        self.hist_lut.autoHistogramRange()
        self.hist_lut.setImageItem(self.img_item)
        self.graph_layout.addItem(self.hist_lut)

        print "pos label"
        self.graph_layout.nextRow()
        self.pos_label = pg.LabelItem(justify='right')
        self.pos_label.setText("TEST")
        self.graph_layout.addItem(self.pos_label)
        self.pos_label_text = "asdf"
                
        print self.img_plot.scene().sigMouseClicked
        #proxy = pg.SignalProxy(self.img_plot.scene().sigMouseMoved, delay=0.1, rateLimit=10, slot=self.mouseMoved)
        self.img_plot.scene().sigMouseClicked.connect(self.mouse_clicked)
        #print proxy
        #self.img_plot.scene().sigMouseMoved.connect(self.mouseMoved)
        
        self.scan_roi = pg.ROI([0,0],[1,1], movable=False)
        for lqname in 'h0 h1 v0 v1 dh dv'.split():
            self.logged_quantities[lqname].updated_value.connect(self.update_scan_roi)
        self.update_scan_roi()
        self.img_plot.addItem(self.scan_roi)


    def update_scan_roi(self):
        h0 = self.h0.val
        v0 = self.v0.val
        h1 = self.h1.val
        v1 = self.v1.val
        dh = self.dh.val
        dv = self.dv.val
        
        H = np.arange(h0, h1, dh)
        V = np.arange(v0, v1, dv)
        
        self.scan_roi.setPos( (H[0]-dh*0.5, V[0]-dv*0.5, 0) )
        self.scan_roi.setSize( (dh + H[-1]-H[0], dv + V[-1]-V[0], 0))
    
    
    def mouse_clicked(self,evt):
        #print evt
        #print evt.pos()
        #print evt.scenePos()
        mousePoint = self.img_plot.vb.mapSceneToView(evt.scenePos())
        x,y = mousePoint.x(), mousePoint.y()
        print "({} ,{}, None),".format(x,y)
    
    #@QtCore.Slot()
    def mouseMoved(self,evt):
        #print "asdf", evt.pos()
        #self.pos_label.setText(str(evt.x()))
        #if self.img_plot.sceneBoundingRect().contains(evt):
        mousePoint = self.img_plot.vb.mapSceneToView(evt)
        #print mousePoint
        
        ii = self.h_array.searchsorted(mousePoint.x()) # not quite right
        jj = self.v_array.searchsorted(mousePoint.y()) # not quite right
        
        ii %= len(self.h_array)
        jj %= len(self.v_array)
        #print ii,jj
        
        self.pos_label_text = "H {:+02.2f} um [{}], V {:+02.2f} um [{}]: {:1.2e} Hz ".format(
                                mousePoint.x(), ii, mousePoint.y(), jj,
                                self.count_rate_map[jj,ii] 
                                )
        
        if not self.is_measuring():
            self.pos_label.setText(self.pos_label_text)
            self.gui.app.processEvents()

        
    def on_fig2d_click(self, evt):
        
        stage = self.gui.mcl_xyz_stage_hc
        #print evt.xdata, evt.ydata, evt.button, evt.key
        if not self.is_measuring():
            if evt.key == "shift":
                print "moving to ", evt.xdata, evt.ydata
                #self.nanodrive.set_pos_ax(evt.xdata, HAXIS_ID)
                #self.nanodrive.set_pos_ax(evt.ydata, VAXIS_ID)
                
                new_pos = [None,None,None]                
                new_pos[stage.h_axis_id-1] = evt.xdata
                new_pos[stage.v_axis_id-1] = evt.ydata
                
                stage.nanodrive.set_pos_slow(*new_pos)
                stage.read_from_hardware()

    def pre_scan_setup(self):
        #hardware 
        self.apd_counter_hc = self.gui.apd_counter_hc
        self.apd_count_rate = self.gui.apd_counter_hc.apd_count_rate


        #scan specific setup
        
        
        # create data arrays
        self.count_rate_map = np.zeros((self.Nv, self.Nh), dtype=float)
        self.count_rate_map_h5 = self.h5_meas_group.create_dataset('count_rate_map', shape=(self.Nv, self.Nh), dtype=float, compression='gzip')
        
        self.gui.settings_auto_save()
        
        #update figure
        
        """self.fig2d.clf()
        self.ax2d = self.fig2d.add_subplot(111)
        self.ax2d.plot([0,1])

        self.ax2d.set_xlim(0, 100)
        self.ax2d.set_ylim(0, 100)
                    
        self.fig2d.canvas.mpl_connect('button_press_event', self.on_fig2d_click)
        self.imgplot = self.ax2d.imshow(self.count_rate_map, 
                                    origin='lower',
                                    vmin=1e4, vmax=1e5, interpolation='nearest', 
                                    extent=self.imshow_extent)

        """

        # pyqt graph
        self.initial_scan_setup_plotting = True


        # set up experiment
        # experimental parameters already connected via LoggedQuantities
        
        # open shutter 
        self.gui.shutter_servo_hc.shutter_open.update_value(True)
        time.sleep(0.5)

    def post_scan_cleanup(self):
        # close shutter 
        self.gui.shutter_servo_hc.shutter_open.update_value(False)

    def collect_pixel(self, i_h, i_v):
        # collect data
        self.apd_count_rate.read_from_hardware()
                          
        # store in arrays
        self.count_rate_map[i_v,i_h] = self.apd_count_rate.val
        self.count_rate_map_h5[i_v,i_h] = self.apd_count_rate.val
        
        # update graph elements
        self.current_pixel_arrow.setPos(self.h_array[i_h], self.v_array[i_v])
    
    def scan_specific_savedict(self):
        return {
                     'count_rate_map': self.count_rate_map,
        }               


    def update_display(self):
        
        #self.img_plot.scene().sigMouseClicked.connect(self.mouse_clicked)
        #self.img_plot.scene().sigMouseClicked.connect(self.mouse_clicked)
        if self.initial_scan_setup_plotting:
            self.img_item = pg.ImageItem()
            self.img_plot.addItem(self.img_item)
            self.hist_lut.setImageItem(self.img_item)
    
            self.img_item.setImage(self.count_rate_map.T)
            x0, x1, y0, y1 = self.imshow_extent
            print x0, x1, y0, y1
            self.img_item.setRect(QtCore.QRectF(x0, y0, x1-x0, y1-y0))
            self.initial_scan_setup_plotting = False
        
        #print "updating figure"
        im_data = self.count_rate_map #
        #im_data = np.log10(self.count_rate_map)
        """
        self.imgplot.set_data(im_data)
        try:
            count_min =  np.percentile(im_data[np.nonzero(self.count_rate_map)], 1)
        except Exception as err:
            count_min = 0
        count_max = np.percentile(im_data,99.)
        assert count_max > count_min
        self.imgplot.set_clim(count_min, count_max + 1)
        """
        #self.fig2d.canvas.draw()
        
        # pyqtgraph
        self.img_item.setImage(self.count_rate_map.T, autoRange=False, autoLevels=False)
        self.hist_lut.imageChanged(autoLevel=True)
        #self.gui.app.processEvent()
        #self.img_plot.repaint()
        #self.img_view.
        #self.img_view.translate(4,4)
        #self.img_view.setImage(img, autoRange=False, autoLevels, levels, axes, xvals, pos, scale, transform, autoHistogramRange)
        #self.pos_label.setText(time.time())
        self.pos_label.setText(self.pos_label_text)
        self.gui.app.processEvents()

class APDConfocalScan3DMeasurement(Base3DScan):

    name = "apd_confocal_scan3d"
    
    def scan_specific_setup(self):
        
        self.int_time = self.gui.apd_counter_hc.int_time

    def setup_figure(self):
        pass
    
    def pre_scan_setup(self):
        #hardware 
        self.apd_counter_hc = self.gui.apd_counter_hc
        self.apd_count_rate = self.gui.apd_counter_hc.apd_count_rate

        #scan specific setup
        
        # create data arrays
        self.count_rate_map = np.zeros((self.Nz, self.Ny, self.Nx), dtype=float)
        self.count_rate_map_h5 = self.h5_meas_group.create_dataset('count_rate_map', 
                                shape=(self.Nz, self.Ny, self.Nx), dtype=float, compression='gzip', shuffle=True)

        #update figure
    
    def collect_pixel(self, i, j, k):
        # collect data
        self.apd_count_rate.read_from_hardware()
                          
        # store in arrays
        self.count_rate_map[k,j,i] = self.apd_count_rate.val
        self.count_rate_map_h5[k,j,i] = self.apd_count_rate.val
        
    
    def scan_specific_savedict(self):
        return {'count_rate_map': self.count_rate_map}
        
    def update_display(self):
        pass
    

from measurement_components.mcl_stage_slowscan import MCLStage2DSlowScan

class APD_MCL_2DSlowScan(MCLStage2DSlowScan):
    
    name = 'APD_MCL_2DSlowScan'
    
    def pre_scan_setup(self):
        #hardware 
        self.apd_counter_hc = self.app.hardware.apd_counter
        self.apd_count_rate = self.apd_counter_hc.apd_count_rate


        #scan specific setup
        
        # create data arrays
        self.count_rate_map = np.zeros(self.scan_shape, dtype=float)
        self.count_rate_map_h5 = self.h5_meas_group.create_dataset('count_rate_map', 
                                                                   shape=self.scan_shape,
                                                                   dtype=float, 
                                                                   compression='gzip')
        
        #self.app.settings_auto_save()
        

        # pyqt graph
        self.initial_scan_setup_plotting = True


        # set up experiment
        # experimental parameters already connected via LoggedQuantities
        
        # open shutter 
        # self.gui.shutter_servo_hc.shutter_open.update_value(True)
        # time.sleep(0.5)
        
    def post_scan_cleanup(self):
        # close shutter 
        #self.gui.shutter_servo_hc.shutter_open.update_value(False)
        pass
    
    def collect_pixel(self, pixel_num, k, j, i):
        # collect data
        print(pixel_num, k, j, i)
        self.apd_count_rate.read_from_hardware()
                          
        # store in arrays
        self.count_rate_map[k,j,i] = self.apd_count_rate.val
        self.count_rate_map_h5[k,j,i] = self.apd_count_rate.val
  
        self.display_image_map[k,j,i] = self.apd_count_rate.val
    