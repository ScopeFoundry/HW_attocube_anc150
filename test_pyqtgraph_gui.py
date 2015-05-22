import sys
from PySide import QtGui, QtCore

from base_gui import BaseMicroscopeGUI
from measurement_components.apd_confocal import APDOptimizerMeasurement

import pyqtgraph as pg
## Switch to using white background and black foreground
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

import numpy as np

class TestGUI(BaseMicroscopeGUI):
    
    ui_filename = "trpl_gui.ui"

    def setup(self):
        #Add hardware components
        print "Adding Hardware Components"

        #Add measurement components
        print "Create Measurement objects"
        self.apd_optimizer_measure = self.add_measurement_component(APDOptimizerMeasurement(self))
        
        # Connect to custom gui

        #im_display = self.add_image_display('im_disp', self.ui.plot2d_widget)
        """
        l = graph_layout = self.add_pg_graphics_layout('test_layout', self.ui.plot2d_widget)

        l.addLabel('Long Vertical Label', angle=-90, rowspan=3)
        
        ## Add 3 plots into the first row (automatic position)
        p1 = l.addPlot(title="Plot 1")
        p2 = l.addPlot(title="Plot 2")
        p2.setAspectLocked(lock=True, ratio=1)
        vb = l.addViewBox(lockAspect=True)
        img = pg.ImageItem(np.random.normal(size=(100,100)))
        #img.setRect(QtCore.QRect(0,0,10,10))
        img.translate(3,2)
        img.scale(0.01, 0.01)
        vb.addItem(img)
        vb.autoRange()
        
        p2.addItem(img)
        p1.plot([1,3,2,4,3,5])
        p2.plot([1,3,2,4,3,5])
        """

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("TRPL Microscope Control Application")
    
    gui = TestGUI(app)
    gui.show()
    
    sys.exit(app.exec_())