from ScopeFoundry import Measurement
import pyqtgraph as pg
import numpy as np

class PicamReadout(Measurement):

    name = "picam_readout"
    
    def setup(self):
        
        self.display_update_period = 0.050 #seconds

        #connect events

        #local logged quantities

    def run(self):

        picam_hc = self.app.hardware.picam
        cam = picam_hc.cam

        print "rois|-->", cam.read_rois()

        cam.commit_parameters()
        
        while not self.interrupt_measurement_called:
            dat = cam.acquire(readout_count=1, readout_timeout=-1)
            
            self.roi_data = cam.reshape_frame_data(dat)
            #print "roi_data shapes", [d.shape for d in self.roi_data]
        


    def setup_figure(self):

        if hasattr(self, 'graph_layout'):
            self.graph_layout.deleteLater() # see http://stackoverflow.com/questions/9899409/pyside-removing-a-widget-from-a-layout
            del self.graph_layout

        self.ui = self.graph_layout = pg.GraphicsLayoutWidget(border=(100,100,100))
        self.ui.setWindowTitle(self.name)

        self.spec_plot = self.graph_layout.addPlot()
        self.spec_plot_line = self.spec_plot.plot([1,3,2,4,3,5])
        self.spec_plot.enableAutoRange()
                
        self.graph_layout.nextRow()

        self.img_plot = self.graph_layout.addPlot()
        self.img_item = pg.ImageItem()
        self.img_plot.addItem(self.img_item)
        self.img_plot.showGrid(x=True, y=True)
        self.img_plot.setAspectLocked(lock=True, ratio=1)

        self.hist_lut = pg.HistogramLUTItem()
        self.hist_lut.autoHistogramRange()
        self.hist_lut.setImageItem(self.img_item)
        self.graph_layout.addItem(self.hist_lut)

        self.show_ui()

    def update_display(self):
        self.img_item.setImage(self.roi_data[0].T.astype(float), autoLevels=False)
        self.hist_lut.imageChanged(autoLevel=True, autoRange=True)

        self.spec_plot_line.setData(np.average(self.roi_data[0], axis=0))

